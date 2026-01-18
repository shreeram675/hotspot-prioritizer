import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapPin, Camera, X, ArrowLeft } from 'lucide-react';
import Navbar from '../../components/shared/Navbar';
import Button from '../../components/shared/Button';
import Card from '../../components/shared/Card';
import api from '../../api';
import { useAuth } from '../../contexts/AuthContext';
import './NewReport.css';

const CATEGORIES = ["Road Issues", "Waste Management"];

const NewReport = () => {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [formData, setFormData] = useState({
    title: "",
    category: "",
    location: "",
    description: "",
    latitude: "",
    longitude: "",
  });
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleImageUpload = (e) => {
    const files = Array.from(e.target.files);
    const newImages = files.map((file) => ({
      file,
      preview: URL.createObjectURL(file),
    }));
    setImages((prev) => [...prev, ...newImages].slice(0, 5)); // Max 5 images
  };

  const removeImage = (index) => {
    setImages((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Validate required fields
      if (!formData.latitude || !formData.longitude) {
        throw new Error("Please provide a location");
      }

      // Map frontend categories to backend format
      const categoryMap = {
        "Road Issues": "road_issues",
        "Waste Management": "waste_management",
      };

      // Upload images if any
      let imageUrl = null;
      if (images.length > 0) {
        try {
          // Upload the first image to backend
          const formData = new FormData();
          formData.append('file', images[0].file);

          const uploadResponse = await api.post('/upload/image', formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          });

          imageUrl = uploadResponse.data.image_url;
          console.log('Image uploaded:', imageUrl);
        } catch (uploadError) {
          console.error('Image upload failed:', uploadError);
          throw new Error('Failed to upload image. Please try again.');
        }
      }

      // Prepare report data
      const reportData = {
        title: formData.title,
        description: formData.description,
        category: categoryMap[formData.category] || "other",
        latitude: parseFloat(formData.latitude),
        longitude: parseFloat(formData.longitude),
        image_url: imageUrl,
      };

      console.log("Submitting report:", reportData);

      // Submit report to backend
      const response = await api.post("/reports/", reportData);

      console.log("Report created:", response.data);

      // Show success message
      alert("Report submitted successfully! AI analysis has been performed.");

      // Navigate to the created report or dashboard
      if (response.data.id) {
        navigate(`/citizen/report/${response.data.id}`);
      } else {
        navigate("/citizen/dashboard");
      }
    } catch (err) {
      console.error("Error submitting report:", err);
      setError(
        err.response?.data?.detail ||
        err.message ||
        "Failed to submit report. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  };

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData((prev) => ({
            ...prev,
            latitude: position.coords.latitude.toFixed(6),
            longitude: position.coords.longitude.toFixed(6),
            location: `${position.coords.latitude.toFixed(6)}, ${position.coords.longitude.toFixed(6)}`,
          }));
        },
        (error) => {
          console.error("Error getting location:", error);
        },
      );
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <main className="container py-lg">
        <div className="report-form-header">
          <Button
            variant="ghost"
            icon={ArrowLeft}
            onClick={() => navigate("/citizen/dashboard")}
          >
            Back
          </Button>
          <h1 className="text-2xl">Report an Issue</h1>
        </div>

        {error && (
          <div
            style={{
              padding: "12px 16px",
              marginBottom: "20px",
              backgroundColor: "#fee",
              border: "1px solid #fcc",
              borderRadius: "8px",
              color: "#c33",
            }}
          >
            <strong>Error:</strong> {error}
          </div>
        )}

        <div className="report-form-container">
          <Card>
            <form onSubmit={handleSubmit} className="report-form">
              <div className="form-group">
                <label htmlFor="title" className="form-label">
                  Issue Title *
                </label>
                <input
                  id="title"
                  name="title"
                  type="text"
                  className="form-input"
                  placeholder="Brief description of the issue"
                  value={formData.title}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="category" className="form-label">
                  Category *
                </label>
                <select
                  id="category"
                  name="category"
                  className="form-select"
                  value={formData.category}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select a category</option>
                  {CATEGORIES.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="location" className="form-label">
                  Location *
                </label>
                <div className="location-input-group">
                  <div className="input-with-icon flex-1">
                    <MapPin size={18} className="input-icon" />
                    <input
                      id="location"
                      name="location"
                      type="text"
                      className="form-input"
                      placeholder="Enter location or use current location"
                      value={formData.location}
                      onChange={handleChange}
                      required
                    />
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={getCurrentLocation}
                  >
                    Use Current
                  </Button>
                </div>
                {formData.latitude && formData.longitude && (
                  <p className="text-xs text-muted mt-xs">
                    Coordinates: {formData.latitude}, {formData.longitude}
                  </p>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="description" className="form-label">
                  Description *
                </label>
                <textarea
                  id="description"
                  name="description"
                  className="form-textarea"
                  placeholder="Provide detailed information about the issue"
                  rows="5"
                  value={formData.description}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Photos (Optional, max 5)</label>
                <div className="image-upload-container">
                  <input
                    type="file"
                    id="image-upload"
                    accept="image/*"
                    multiple
                    onChange={handleImageUpload}
                    className="hidden"
                  />
                  <label htmlFor="image-upload" className="image-upload-btn">
                    <Camera size={24} />
                    <span>Upload Photos</span>
                  </label>
                </div>

                {images.length > 0 && (
                  <div className="image-preview-grid">
                    {images.map((img, index) => (
                      <div key={index} className="image-preview-item">
                        <img src={img.preview} alt={`Preview ${index + 1}`} />
                        <button
                          type="button"
                          className="image-remove-btn"
                          onClick={() => removeImage(index)}
                        >
                          <X size={16} />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="form-actions">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate("/citizen/dashboard")}
                >
                  Cancel
                </Button>
                <Button type="submit" variant="primary" disabled={loading}>
                  {loading ? "Submitting..." : "Submit Report"}
                </Button>
              </div>
            </form>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default NewReport;
