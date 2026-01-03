import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import MiniMap from './MiniMap';
import ReportDetailModal from './ReportDetailModal';
import LocationSearch from './LocationSearch';

// Component for submitting new reports
const ReportForm = () => {
    const [formData, setFormData] = useState({
        title: '',
        category: 'Infrastructure',
        description: '',
        lat: '',
        lon: '',
        image: null
    });
    const [nearbyReports, setNearbyReports] = useState([]); // Duplicates
    const [allNearbyReports, setAllNearbyReports] = useState([]); // All nearby (non-duplicates)
    const [selectedReport, setSelectedReport] = useState(null); // For modal
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const [message, setMessage] = useState('');
    const [imagePreview, setImagePreview] = useState(null);
    const [userLocation, setUserLocation] = useState(null);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            // Validate file size (10MB max)
            if (file.size > 10 * 1024 * 1024) {
                setMessage('Error: File size must be less than 10MB');
                return;
            }

            // Validate file type
            const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
            if (!validTypes.includes(file.type)) {
                setMessage('Error: Only JPG, PNG, and GIF images are allowed');
                return;
            }

            setFormData({ ...formData, image: file });

            // Create preview
            const reader = new FileReader();
            reader.onloadend = () => {
                setImagePreview(reader.result);
            };
            reader.readAsDataURL(file);
        }
    };

    const removeImage = () => {
        setFormData({ ...formData, image: null });
        setImagePreview(null);
    };

    const handleMapLocationChange = (lat, lon) => {
        setFormData({ ...formData, lat, lon });
    };

    const getLocation = () => {
        if (!navigator.geolocation) {
            setMessage("Error: Geolocation not supported.");
            return;
        }

        setMessage('Fetching precise location (please wait)...');
        let bestAccuracy = Infinity;
        let watchId = null;
        let timeoutId = null;

        const stopLocationWatch = () => {
            if (watchId !== null) {
                navigator.geolocation.clearWatch(watchId);
                watchId = null;
            }
            if (timeoutId !== null) {
                clearTimeout(timeoutId);
                timeoutId = null;
            }
        };

        // Timeout after 15 seconds
        timeoutId = setTimeout(() => {
            stopLocationWatch();
            if (bestAccuracy === Infinity) {
                setMessage("Could not get a high-accuracy location. Please try manually moving the pin.");
            } else {
                setMessage(`Location updated! (Accuracy: ${Math.round(bestAccuracy)}m)`);
                setTimeout(() => setMessage(''), 3000);
            }
        }, 15000);

        watchId = navigator.geolocation.watchPosition(
            (position) => {
                const { latitude, longitude, accuracy } = position.coords;

                // Update if this new position is more accurate or if we haven't set one yet
                if (accuracy < bestAccuracy) {
                    bestAccuracy = accuracy;
                    setFormData(prev => ({
                        ...prev,
                        lat: latitude,
                        lon: longitude
                    }));

                    // User feedback
                    setMessage(`Improving accuracy... (${Math.round(accuracy)}m)`);

                    // If highly accurate (< 10m), we can stop early
                    if (accuracy <= 10) {
                        stopLocationWatch();
                        setMessage(`Precise location found! (Accuracy: ${Math.round(accuracy)}m)`);
                        setTimeout(() => setMessage(''), 3000);
                    }
                }
            },
            (error) => {
                console.error("Geolocation error:", error);
                if (bestAccuracy === Infinity) {
                    setMessage("Error: Could not fetch location. Ensure GPS is on.");
                }
                stopLocationWatch();
            },
            {
                enableHighAccuracy: true,
                timeout: 15000,
                maximumAge: 0
            }
        );
    };

    // Get user location on mount
    useEffect(() => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition((position) => {
                const userPos = [position.coords.latitude, position.coords.longitude];
                setUserLocation(userPos);
                // Set initial report location to user location if not set
                if (!formData.lat && !formData.lon) {
                    setFormData({
                        ...formData,
                        lat: position.coords.latitude,
                        lon: position.coords.longitude
                    });
                }
            });
        }
    }, []);

    // Check for duplicates when lat/lon, title, or description changes
    useEffect(() => {
        const timer = setTimeout(() => {
            if ((formData.lat && formData.lon) || (formData.title || formData.description)) {
                checkDuplicates();
            } else {
                setNearbyReports([]);
            }
        }, 800); // 800ms debounce

        return () => clearTimeout(timer);
    }, [formData.lat, formData.lon, formData.title, formData.description]);

    const checkDuplicates = async () => {
        // If no text, we might want to skip or just show nearby? 
        // For now, let's enforce at least some text or location.
        // Backend `check_duplicate` requires `description` to be non-empty to run NLP, 
        // BUT I modified it: "if not description: return []".
        // Use title as description if description is empty.
        const textToCheck = (formData.title + " " + formData.description).trim();

        if (!textToCheck) {
            // If no text, strictly speaking we can't do "Duplicate Detection" per new logic.
            // We could fall back to /nearby if we wanted "Context nearby", but let's stick to the requested "Duplicate" feature.
            setNearbyReports([]);
            return;
        }

        try {
            const data = new FormData();
            data.append('description', textToCheck);
            if (formData.lat) data.append('lat', formData.lat);
            if (formData.lon) data.append('lon', formData.lon);

            const response = await axios.post('http://localhost:8000/reports/check-duplicates', data);
            const duplicates = response.data;
            setNearbyReports(duplicates);

            // Also fetch all nearby reports (not just duplicates)
            if (formData.lat && formData.lon) {
                fetchAllNearby(duplicates);
            }
        } catch (error) {
            console.error("Error checking duplicates:", error);
            // Don't show error to user constantly
        }
    };

    const fetchAllNearby = async (duplicates = []) => {
        try {
            const response = await axios.get('http://localhost:8000/reports/nearby', {
                params: { lat: formData.lat, lon: formData.lon, radius_m: 100 }
            });
            // Filter out duplicates already shown
            const duplicateIds = duplicates.map(d => d.report_id);
            setAllNearbyReports(response.data.filter(r => !duplicateIds.includes(r.report_id)));
        } catch (error) {
            console.error("Error fetching nearby reports:", error);
        }
    };

    const viewReportDetails = async (reportId) => {
        try {
            const response = await axios.get(`http://localhost:8000/reports/${reportId}`);
            setSelectedReport(response.data);
        } catch (error) {
            console.error("Error fetching report details:", error);
            setMessage('Error loading report details.');
        }
    };

    const handleUpvote = async (reportId) => {
        try {
            // Placeholder for upvote logic
            // await axios.post(`http://localhost:8000/reports/${reportId}/upvote`);
            setMessage(`Report ${reportId} upvoted! (Placeholder action)`);
            // Optionally, re-check duplicates to update upvote count
            checkDuplicates();
        } catch (error) {
            console.error("Error upvoting report:", error);
            setMessage('Failed to upvote report.');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage(''); // Clear previous messages
        try {
            const data = new FormData();
            data.append('title', formData.title);
            data.append('category', formData.category);
            data.append('description', formData.description);
            data.append('lat', formData.lat);
            data.append('lon', formData.lon);
            if (formData.image) {
                data.append('image', formData.image);
            }

            // Retrieve token from localStorage
            const token = localStorage.getItem('token');
            const config = {
                headers: {}
            };

            if (token) {
                config.headers['Authorization'] = `Bearer ${token}`;
            }

            await axios.post('http://localhost:8000/reports/', data, config);
            setMessage("Report submitted successfully! Redirecting...");
            setFormData({ // Reset form
                title: '',
                category: 'Infrastructure',
                description: '',
                lat: '',
                lon: '',
                image: null
            });
            setImagePreview(null); // Clear preview
            setNearbyReports([]); // Clear duplicates

            // Navigate to hotspots page after short delay
            setTimeout(() => {
                navigate('/hotspots');
            }, 1500);

        } catch (error) {
            console.error("Error submitting report:", error);
            if (error.response && error.response.status === 401) {
                setMessage("Error: You must be logged in to submit a report. Please go to Login.");
            } else {
                setMessage("Error: Failed to submit report. " + (error.response?.data?.detail || error.message));
            }
        }
        setLoading(false);
    };

    // Check if logged in on mount
    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            setMessage("Please Login to submit a report.");
        }
    }, []);

    return (
        <div className="flex justify-center items-center min-h-screen bg-slate-50 pt-20 pb-10 px-4">
            <div className="bg-white p-8 rounded-2xl shadow-[0_20px_50px_rgba(8,_112,_184,_0.7)] w-full max-w-2xl border border-slate-100 transform transition-all hover:scale-[1.005]">
                <h2 className="text-3xl font-extrabold mb-8 text-center text-slate-800 tracking-tight">
                    Submit New Report
                </h2>

                {message && (
                    <div className={`p-4 rounded-lg mb-6 text-sm font-medium border ${message.includes('Error')
                        ? 'bg-red-50 text-red-600 border-red-100'
                        : 'bg-green-50 text-green-600 border-green-100'
                        }`}>
                        {message}
                    </div>
                )}

                {/* Similar Reports (Duplicates) */}
                {nearbyReports.length > 0 && (
                    <div className="mb-8 bg-yellow-50 border border-yellow-100 p-6 rounded-xl shadow-sm">
                        <h3 className="font-bold text-yellow-800 mb-3 flex items-center">
                            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                            Similar Reports Nearby
                        </h3>
                        <p className="text-sm text-yellow-700 mb-4">
                            We found similar reports in this area. Click to view details or upvote instead of creating a duplicate.
                        </p>
                        <div className="space-y-3">
                            {nearbyReports.map(dup => (
                                <div
                                    key={dup.report_id}
                                    className="bg-white p-4 rounded-lg border border-yellow-200 shadow-sm hover:shadow-md transition-all cursor-pointer"
                                    onClick={() => viewReportDetails(dup.report_id)}
                                >
                                    <div className="flex justify-between items-center">
                                        <div className="flex-1">
                                            <span className="font-semibold text-slate-800 block">{dup.title}</span>
                                            <div className="flex gap-3 mt-1 text-xs text-slate-500">
                                                <span>Distance: {Math.round(dup.distance_m)}m</span>
                                                <span>•</span>
                                                <span>Similarity: {Math.round(dup.similarity * 100)}%</span>
                                            </div>
                                        </div>
                                        <button
                                            onClick={(e) => { e.stopPropagation(); handleUpvote(dup.report_id); }}
                                            className="bg-yellow-100 text-yellow-700 px-4 py-2 rounded-lg text-sm font-bold hover:bg-yellow-200 transition-colors"
                                        >
                                            Upvote ({dup.upvote_count})
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Other Reports Nearby (Non-duplicates) */}
                {allNearbyReports.length > 0 && (
                    <div className="mb-8 bg-blue-50 border border-blue-100 p-6 rounded-xl shadow-sm">
                        <h3 className="font-bold text-blue-800 mb-3 flex items-center">
                            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                            Other Reports Nearby
                        </h3>
                        <p className="text-sm text-blue-700 mb-4">
                            These reports are within 100m but may be different issues. Click to view details.
                        </p>
                        <div className="space-y-3">
                            {allNearbyReports.map(report => (
                                <div
                                    key={report.report_id}
                                    className="bg-white p-4 rounded-lg border border-blue-200 shadow-sm hover:shadow-md transition-all cursor-pointer"
                                    onClick={() => viewReportDetails(report.report_id)}
                                >
                                    <div className="flex justify-between items-center">
                                        <div className="flex-1">
                                            <span className="font-semibold text-slate-800 block">{report.title}</span>
                                            <div className="flex gap-3 mt-1 text-xs text-slate-500">
                                                <span>Distance: {Math.round(report.distance_m)}m</span>
                                                <span>•</span>
                                                <span className="px-2 py-0.5 bg-slate-100 rounded">{report.category}</span>
                                            </div>
                                        </div>
                                        <button
                                            onClick={(e) => { e.stopPropagation(); handleUpvote(report.report_id); }}
                                            className="bg-blue-100 text-blue-700 px-4 py-2 rounded-lg text-sm font-bold hover:bg-blue-200 transition-colors"
                                        >
                                            Upvote ({report.upvote_count})
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Title</label>
                            <input
                                type="text"
                                name="title"
                                value={formData.title}
                                onChange={handleChange}
                                className="w-full px-4 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all shadow-sm"
                                required
                                placeholder="e.g., Pothole on Main St"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Category</label>
                            <select
                                name="category"
                                value={formData.category}
                                onChange={handleChange}
                                className="w-full px-4 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all shadow-sm bg-white"
                            >
                                <option value="Sanitation">Sanitation</option>
                                <option value="Roadways">Roadways</option>
                                <option value="Other">Other</option>
                            </select>
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Description</label>
                        <textarea
                            name="description"
                            value={formData.description}
                            onChange={handleChange}
                            className="w-full px-4 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all shadow-sm h-32 resize-none"
                            placeholder="Describe the issue in detail..."
                        />
                    </div>

                    <div className="bg-slate-50 p-6 rounded-xl border border-slate-200">
                        <label className="block text-sm font-bold text-slate-700 mb-2">Location</label>
                        <p className="text-xs text-slate-600 mb-4">
                            Search for an address or drag the marker to the exact location.
                        </p>

                        {/* Search Component */}
                        <div className="mb-4">
                            <LocationSearch
                                onLocationSelect={handleMapLocationChange}
                                className="w-full"
                            />
                        </div>

                        {/* Mini Map */}
                        <div className="mb-4">
                            <MiniMap
                                lat={parseFloat(formData.lat)}
                                lon={parseFloat(formData.lon)}
                                userLocation={userLocation}
                                onLocationChange={handleMapLocationChange}
                                showSearch={false}
                            />
                        </div>

                        {/* Hidden Inputs for Form Submission */}
                        <input type="hidden" name="lat" value={formData.lat} />
                        <input type="hidden" name="lon" value={formData.lon} />

                        <div className="flex justify-between items-center text-xs text-slate-500 mb-4 px-1">
                            <span>Lat: {parseFloat(formData.lat || 0).toFixed(6)}</span>
                            <span>Lon: {parseFloat(formData.lon || 0).toFixed(6)}</span>
                        </div>

                        <button
                            type="button"
                            onClick={getLocation}
                            className="w-full bg-white text-blue-600 border border-blue-200 py-2 rounded-lg font-medium hover:bg-blue-50 transition-colors flex justify-center items-center shadow-sm"
                        >
                            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                            Refine with My Current Location
                        </button>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Upload Image</label>

                        {imagePreview ? (
                            <div className="relative">
                                <div className="rounded-xl overflow-hidden border-2 border-slate-200 bg-slate-100">
                                    <img
                                        src={imagePreview}
                                        alt="Preview"
                                        className="w-full h-64 object-cover"
                                    />
                                </div>
                                <div className="mt-3 flex items-center justify-between bg-white p-3 rounded-lg border border-slate-200">
                                    <div className="flex items-center gap-2 text-sm text-slate-600">
                                        <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                        </svg>
                                        <span className="font-medium">{formData.image?.name}</span>
                                        <span className="text-slate-400">({(formData.image?.size / 1024).toFixed(1)} KB)</span>
                                    </div>
                                    <button
                                        type="button"
                                        onClick={removeImage}
                                        className="text-red-600 hover:text-red-800 text-sm font-medium px-3 py-1 rounded-lg hover:bg-red-50 transition-colors"
                                    >
                                        Remove
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-slate-300 border-dashed rounded-xl hover:border-blue-400 transition-colors bg-slate-50">
                                <div className="space-y-1 text-center">
                                    <svg className="mx-auto h-12 w-12 text-slate-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
                                        <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                    <div className="flex text-sm text-slate-600">
                                        <label htmlFor="file-upload" className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500">
                                            <span>Upload a file</span>
                                            <input id="file-upload" name="file-upload" type="file" accept="image/*" className="sr-only" onChange={handleFileChange} />
                                        </label>
                                        <p className="pl-1">or drag and drop</p>
                                    </div>
                                    <p className="text-xs text-slate-500">PNG, JPG, GIF up to 10MB</p>
                                </div>
                            </div>
                        )}
                    </div>

                    <button
                        type="submit"
                        className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 rounded-xl font-bold shadow-lg hover:shadow-blue-500/30 hover:-translate-y-0.5 transition-all duration-200 active:scale-95"
                    >
                        {loading ? 'Submitting...' : 'Submit Report'}
                    </button>
                </form>
            </div>
            {/* Report Detail Modal */}
            {selectedReport && (
                <ReportDetailModal
                    report={selectedReport}
                    onClose={() => setSelectedReport(null)}
                />
            )}
        </div>
    );
};

export default ReportForm;
