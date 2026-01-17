import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { useNavigate } from 'react-router-dom';
import Navbar from '../../components/shared/Navbar';
import Badge from '../../components/shared/Badge';
import Button from '../../components/shared/Button';
import 'leaflet/dist/leaflet.css';
import './MapView.css';

// Fix for default marker icons in React-Leaflet
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

// Mock data
const MOCK_REPORTS = [
    { id: 1, title: 'Pothole on Main Street', category: 'Roads', status: 'Pending', position: [40.7128, -74.0060] },
    { id: 2, title: 'Street Light Not Working', category: 'Electricity', status: 'In Progress', position: [40.7138, -74.0070] },
    { id: 3, title: 'Garbage Pileup', category: 'Sanitation', status: 'Resolved', position: [40.7118, -74.0050] },
    { id: 4, title: 'Broken Water Pipe', category: 'Water', status: 'Pending', position: [40.7148, -74.0080] }
];

const MapView = () => {
    const navigate = useNavigate();
    const [selectedCategory, setSelectedCategory] = useState('');
    const center = [40.7128, -74.0060]; // NYC coordinates

    const getStatusVariant = (status) => {
        switch (status.toLowerCase()) {
            case 'resolved': return 'success';
            case 'in progress': return 'warning';
            case 'pending': return 'danger';
            default: return 'neutral';
        }
    };

    const filteredReports = selectedCategory
        ? MOCK_REPORTS.filter(r => r.category === selectedCategory)
        : MOCK_REPORTS;

    return (
      <div className="min-h-screen bg-background">
        <Navbar />

        <main className="map-view-container">
          <div className="map-sidebar">
            <h2 className="text-xl mb-md">Nearby Reports</h2>

            <div className="mb-md">
              <select
                className="form-select w-full"
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                <option value="">All Categories</option>
                <option value="road_issues">Road Issues</option>
                <option value="waste_management">Waste Management</option>
              </select>
            </div>

            <div className="reports-list">
              {filteredReports.map((report) => (
                <div
                  key={report.id}
                  className="report-list-item"
                  onClick={() => navigate(`/citizen/report/${report.id}`)}
                >
                  <div className="flex justify-between items-start mb-xs">
                    <h3 className="text-sm font-semibold">{report.title}</h3>
                    <Badge
                      variant={getStatusVariant(report.status)}
                      className="text-xs"
                    >
                      {report.status}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted">{report.category}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="map-container">
            <MapContainer
              center={center}
              zoom={13}
              style={{ height: "100%", width: "100%" }}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              {filteredReports.map((report) => (
                <Marker key={report.id} position={report.position}>
                  <Popup>
                    <div className="map-popup">
                      <h3 className="font-semibold mb-xs">{report.title}</h3>
                      <Badge
                        variant={getStatusVariant(report.status)}
                        className="text-xs mb-xs"
                      >
                        {report.status}
                      </Badge>
                      <p className="text-xs text-muted mb-sm">
                        {report.category}
                      </p>
                      <Button
                        size="sm"
                        onClick={() => navigate(`/citizen/report/${report.id}`)}
                      >
                        View Details
                      </Button>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </div>
        </main>
      </div>
    );
};

export default MapView;
