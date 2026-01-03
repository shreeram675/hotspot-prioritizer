import React, { useRef, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import LocationSearch from './LocationSearch';

// Custom marker icons
const createIcon = (color) => {
    return L.divIcon({
        className: 'custom-div-icon',
        html: `<div style="background-color: ${color}; width: 24px; height: 24px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);"></div>`,
        iconSize: [24, 24],
        iconAnchor: [12, 12]
    });
};

const reportIcon = createIcon('#3b82f6'); // blue
const userIcon = createIcon('#10b981'); // green

// Component to handle marker dragging
const DraggableMarker = ({ position, onPositionChange }) => {
    const markerRef = useRef(null);

    const eventHandlers = {
        dragend() {
            const marker = markerRef.current;
            if (marker != null) {
                const newPos = marker.getLatLng();
                onPositionChange(newPos.lat, newPos.lng);
            }
        },
    };

    return (
        <Marker
            draggable={true}
            eventHandlers={eventHandlers}
            position={position}
            ref={markerRef}
            icon={reportIcon}
        />
    );
};

// Component to update map center when coordinates change externally
const MapUpdater = ({ center }) => {
    const map = useMap();

    useEffect(() => {
        if (center && center[0] && center[1]) {
            map.setView(center, map.getZoom());
        }
    }, [center, map]);

    return null;
};

// Component to handle map clicks for placing marker
const MapClickHandler = ({ onLocationClick }) => {
    useMapEvents({
        click(e) {
            onLocationClick(e.latlng.lat, e.latlng.lng);
        },
    });
    return null;
};

const MiniMap = ({ lat, lon, userLocation, onLocationChange, showSearch = true }) => {
    // Use provided coords or default
    const center = (lat && lon) ? [lat, lon] : (userLocation || [51.505, -0.09]);
    const reportPosition = (lat && lon) ? [lat, lon] : center;

    const handleMarkerDrag = (newLat, newLon) => {
        onLocationChange(newLat, newLon);
    };

    return (
        <div className="w-full h-80 rounded-xl overflow-hidden border-2 border-slate-200 shadow-md relative">
            {/* Search Bar Overlay */}
            {showSearch && (
                <div className="absolute top-3 right-3 z-[1000] w-64 pointer-events-none">
                    <div className="pointer-events-auto">
                        <LocationSearch
                            onLocationSelect={(lat, lon) => {
                                onLocationChange(lat, lon);
                            }}
                        />
                    </div>
                </div>
            )}

            {/* Instructions overlay */}
            <div className="absolute top-3 left-3 z-[1000] bg-white/95 backdrop-blur-sm px-3 py-2 rounded-lg shadow-md text-xs pointer-events-none">
                <p className="font-semibold text-slate-700 flex items-center gap-1.5">
                    <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Click, drag, or search to set location
                </p>
            </div>

            <MapContainer
                center={center}
                zoom={15}
                scrollWheelZoom={true}
                className="h-full w-full"
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                <MapUpdater center={reportPosition} />
                <MapClickHandler onLocationClick={handleMarkerDrag} />

                {/* Draggable marker for report location */}
                <DraggableMarker
                    position={reportPosition}
                    onPositionChange={handleMarkerDrag}
                />

                {/* User location marker (if available and different from report location) */}
                {userLocation && (
                    <Marker position={userLocation} icon={userIcon} />
                )}
            </MapContainer>
        </div>
    );
};

export default MiniMap;
