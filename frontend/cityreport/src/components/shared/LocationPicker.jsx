import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

// Fix Leaflet default icon issue in React
let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

const LocationMarker = ({ position, setPosition }) => {
    const map = useMapEvents({
        click(e) {
            setPosition(e.latlng);
        },
    });

    return position === null ? null : (
        <Marker position={position}></Marker>
    );
};

const LocationPicker = ({ position, onLocationChange }) => {
    // Default to a central location (e.g. Bangalore or generic) or user's current location if provided
    const [markerPos, setMarkerPos] = useState(position || { lat: 12.9716, lng: 77.5946 });

    useEffect(() => {
        if (position) {
            setMarkerPos(position);
        }
    }, [position]);

    const handleSetPosition = (latlng) => {
        setMarkerPos(latlng);
        onLocationChange(latlng.lat, latlng.lng);
    };

    return (
        <div style={{ height: '300px', width: '100%', marginBottom: '1rem', borderRadius: '8px', overflow: 'hidden', border: '1px solid #ddd' }}>
            <MapContainer
                center={markerPos}
                zoom={13}
                style={{ height: '100%', width: '100%' }}
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <LocationMarker position={markerPos} setPosition={handleSetPosition} />
            </MapContainer>
            <div className="text-xs text-muted mt-1 text-center">
                Click on the map to set location
            </div>
        </div>
    );
};

export default LocationPicker;
