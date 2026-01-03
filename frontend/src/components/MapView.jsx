import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, GeoJSON } from 'react-leaflet';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import MapLegend from './MapLegend';

// ... (Keep existing Icon and HeatmapLayer code) ...

// Fix for default marker icon
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

import 'leaflet.heat';

const HeatmapLayer = ({ points }) => {
    const map = useMap();

    useEffect(() => {
        if (!map || !points || points.length === 0) return;

        const heat = L.heatLayer(points, {
            radius: 25,
            blur: 15,
            maxZoom: 17,
        }).addTo(map);

        return () => {
            map.removeLayer(heat);
        };
    }, [map, points]);

    return null;
};

import UserLocationMarker from './UserLocationMarker';
import LocationSearch from './LocationSearch';

const MapView = () => {
    const [reports, setReports] = useState([]);
    const [gridData, setGridData] = useState(null);
    const [center, setCenter] = useState([51.505, -0.09]); // Default: London
    const [userLocation, setUserLocation] = useState(null);
    const [vizMode, setVizMode] = useState('heatmap'); // 'heatmap' or 'grid'
    const [locating, setLocating] = useState(false);
    const [locationError, setLocationError] = useState(null);
    const navigate = useNavigate();


    const handleLocate = () => {
        setLocating(true);
        setLocationError(null);
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const { latitude, longitude } = position.coords;
                    const userPos = [latitude, longitude];
                    setUserLocation(userPos);
                    setCenter(userPos);
                    fetchReports(latitude, longitude);
                    setLocating(false);
                },
                (error) => {
                    console.error("Geolocation denied or failed:", error);
                    let errMsg = "Location access denied. Please enable permissions.";
                    if (error.code === 2) errMsg = "Location unavailable.";
                    if (error.code === 3) errMsg = "Location request timed out.";
                    setLocationError(errMsg);
                    setLocating(false);
                },
                { enableHighAccuracy: true, timeout: 30000, maximumAge: 0 }
            );
        } else {
            setLocationError("Geolocation is not supported by your browser.");
            setLocating(false);
        }
    };

    useEffect(() => {
        handleLocate();
    }, []);

    useEffect(() => {
        if (vizMode === 'grid' && !gridData) {
            fetchGridData();
        }
    }, [vizMode]);

    const fetchReports = async (lat, lon) => {
        try {
            const token = localStorage.getItem('token');
            const config = token ? { headers: { Authorization: `Bearer ${token}` }, params: { lat, lon, radius_m: 5000 } } : { params: { lat, lon, radius_m: 5000 } };

            const response = await axios.get(`http://localhost:8000/reports/nearby`, config);
            setReports(response.data);
        } catch (error) {
            console.error("Error fetching reports:", error);
        }
    };

    const fetchGridData = async () => {
        try {
            const response = await axios.get(`http://localhost:8000/hotspots/`, {
                params: { method: 'grid', grid_size_deg: 0.005 } // ~500m
            });
            setGridData(response.data);
        } catch (error) {
            console.error("Error fetching grid data:", error);
        }
    };

    // Prepare heatmap points
    const heatmapPoints = reports.map(r => [r.lat, r.lon, r.upvote_count + 1]);

    // Grid Style
    const onEachGridFeature = (feature, layer) => {
        if (feature.properties && feature.properties.count) {
            layer.bindTooltip(`Reports: ${feature.properties.count}`, {
                permanent: false,
                direction: "center"
            });
        }
    };

    const gridStyle = (feature) => {
        const count = feature.properties.count;
        let fillColor = '#bfdbfe'; // blue-200
        if (count > 5) fillColor = '#ef4444'; // red-500
        else if (count > 2) fillColor = '#f97316'; // orange-500
        else if (count > 0) fillColor = '#facc15'; // yellow-400

        return {
            fillColor: fillColor,
            weight: 1,
            opacity: 1,
            color: 'white',
            dashArray: '3',
            fillOpacity: 0.6
        };
    };

    const handleUpvote = async (report) => {
        const token = localStorage.getItem('token');
        if (!token) {
            alert("Please login to upvote reports.");
            return;
        }

        const isUpvoted = report.is_upvoted;
        const originalCount = report.upvote_count;

        // Optimistic Update
        const updatedReports = reports.map(r => {
            if (r.report_id === report.report_id) {
                return {
                    ...r,
                    is_upvoted: !isUpvoted,
                    upvote_count: isUpvoted ? r.upvote_count - 1 : r.upvote_count + 1
                };
            }
            return r;
        });
        setReports(updatedReports);

        try {
            const config = {
                headers: { Authorization: `Bearer ${token}` }
            };

            if (isUpvoted) {
                await axios.delete(`http://localhost:8000/reports/${report.report_id}/unvote`, config);
            } else {
                await axios.post(`http://localhost:8000/reports/${report.report_id}/upvote`, {}, config);
            }
        } catch (error) {
            console.error("Upvote failed:", error);
            // Revert on error
            setReports(reports); // Revert to original state (closure captures original 'reports')
            alert("Failed to update upvote. Please try again.");
        }
    };

    return (
        <div className="h-full w-full relative">
            <MapContainer center={center} zoom={13} scrollWheelZoom={true} className="h-full w-full">
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {vizMode === 'heatmap' && <HeatmapLayer points={heatmapPoints} />}

                {vizMode === 'grid' && gridData && (
                    <GeoJSON
                        data={gridData}
                        style={gridStyle}
                        onEachFeature={onEachGridFeature}
                    />
                )}

                <UserLocationMarker position={userLocation} />

                {reports.map((report) => (
                    <Marker key={report.report_id} position={[report.lat, report.lon]}>
                        <Popup>
                            <div className="p-2 min-w-[200px]">
                                {report.images && report.images.length > 0 && (
                                    <div className="mb-2 rounded-lg overflow-hidden h-32 w-full bg-gray-100">
                                        <img
                                            src={`http://localhost:8000${report.images[0]}`}
                                            alt={report.title}
                                            className="w-full h-full object-cover"
                                        />
                                    </div>
                                )}
                                <h3 className="font-bold text-lg text-slate-800">{report.title}</h3>
                                <p className="text-sm text-slate-600 mb-1">{report.category}</p>
                                <div className="flex items-center justify-between mt-2">
                                    <button
                                        onClick={() => handleUpvote(report)}
                                        className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium transition-colors ${report.is_upvoted
                                            ? 'bg-blue-600 text-white hover:bg-blue-700'
                                            : 'bg-blue-100 text-blue-800 hover:bg-blue-200'
                                            }`}
                                    >
                                        {report.is_upvoted ? '👍 Upvoted' : '👍 Upvote'}
                                        <span className={`ml-1 ${report.is_upvoted ? 'text-blue-100' : 'text-blue-600'}`}>
                                            {report.upvote_count}
                                        </span>
                                    </button>
                                    <button
                                        onClick={() => navigate(`/reports/${report.report_id}`)}
                                        className="text-xs text-blue-600 hover:underline"
                                    >
                                        View Details
                                    </button>
                                </div>
                            </div>
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>

            {/* Controls */}
            <div className="absolute top-20 right-4 z-[1000] flex flex-col gap-4 items-end pointer-events-none">
                {/* Search Bar - Pointer events auto to allow interaction */}
                <div className="pointer-events-auto w-72">
                    <LocationSearch
                        onLocationSelect={(lat, lon) => {
                            const newCenter = [lat, lon];
                            setCenter(newCenter);
                            fetchReports(lat, lon);
                        }}
                    />
                </div>

                <div className="bg-white p-2 rounded-lg shadow-lg border border-slate-200 flex flex-col gap-2 w-full pointer-events-auto">
                    <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Visualization</label>
                    <div className="flex bg-slate-100 rounded-lg p-1">
                        <button
                            onClick={() => setVizMode('heatmap')}
                            className={`flex-1 px-3 py-1.5 text-sm font-medium rounded-md transition-all ${vizMode === 'heatmap'
                                ? 'bg-white text-blue-600 shadow-sm'
                                : 'text-slate-500 hover:text-slate-700'
                                }`}
                        >
                            Heatmap
                        </button>
                        <button
                            onClick={() => setVizMode('grid')}
                            className={`flex-1 px-3 py-1.5 text-sm font-medium rounded-md transition-all ${vizMode === 'grid'
                                ? 'bg-white text-blue-600 shadow-sm'
                                : 'text-slate-500 hover:text-slate-700'
                                }`}
                        >
                            Grid
                        </button>
                    </div>
                </div>

                <MapLegend mode={vizMode} />
            </div>

            {/* Locate Me Button & Error Toast */}
            <div className="absolute bottom-8 right-4 z-[1000] flex flex-col items-end gap-2">
                {locationError && (
                    <div className="bg-red-50 text-red-600 px-4 py-2 rounded-lg shadow-lg border border-red-200 text-sm font-medium mb-2 animate-fade-in">
                        {locationError}
                        <button onClick={() => setLocationError(null)} className="ml-2 font-bold">×</button>
                    </div>
                )}
                <button
                    onClick={handleLocate}
                    disabled={locating}
                    className="bg-white p-3 rounded-full shadow-lg border border-slate-200 text-slate-700 hover:bg-slate-50 transition-all active:scale-95 disabled:opacity-50"
                    title="Use My Location"
                >
                    {locating ? (
                        <svg className="animate-spin h-6 w-6 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                    ) : (
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                    )}
                </button>
            </div>
        </div>
    );
};

export default MapView;
