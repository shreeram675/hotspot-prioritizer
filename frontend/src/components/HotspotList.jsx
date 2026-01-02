import React, { useEffect, useState } from 'react';
import axios from 'axios';

const HotspotList = () => {
    const [hotspots, setHotspots] = useState([]);
    const [loading, setLoading] = useState(true);
    const [method, setMethod] = useState('kmeans');

    useEffect(() => {
        fetchHotspots();
    }, [method]); // Add method to dependency array

    const fetchHotspots = async () => {
        setLoading(true); // Set loading to true when fetching
        try {
            const response = await axios.get('http://localhost:8000/hotspots/', {
                params: { method: method, k: 5 } // Use the method state
            });
            // Adapt the data structure to match the new JSX expectations
            const adaptedHotspots = response.data.map(h => ({
                ...h,
                count: h.report_count,
                lat: h.center.lat,
                lon: h.center.lon,
                title: h.title,
                description: h.description,
                image: h.image,
                score: Number(h.score)
            }));
            setHotspots(adaptedHotspots);
            setLoading(false);
        } catch (error) {
            console.error("Error fetching hotspots:", error);
            setLoading(false);
        }
    };

    const handleExport = () => {
        window.open(`http://localhost:8000/hotspots/export?method=${method}&k=5`, '_blank'); // Use the method state
    };

    return (
        <div className="pt-20 px-4 max-w-7xl mx-auto min-h-screen">
            <div className="flex justify-between items-center mb-8">
                <h2 className="text-3xl font-extrabold text-slate-800 tracking-tight animate-fade-in-down">
                    Neighborhood Hotspots
                </h2>
                <div className="space-x-4 animate-fade-in-down" style={{ animationDelay: '0.1s' }}>
                    <select
                        value={method}
                        onChange={(e) => setMethod(e.target.value)}
                        className="p-2 rounded-lg border border-slate-300 shadow-sm focus:ring-2 focus:ring-blue-500 outline-none bg-white transition-all hover:border-blue-400"
                    >
                        <option value="kmeans">K-Means Clustering</option>
                        <option value="grid">Grid Aggregation</option>
                    </select>
                    <span className="inline-block group relative">
                        <svg className="w-5 h-5 text-slate-400 hover:text-blue-600 cursor-help transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <div className="invisible group-hover:visible absolute bottom-full right-0 mb-2 w-80 bg-slate-800 text-white text-xs rounded-lg p-3 shadow-xl z-50">
                            <div className="font-semibold mb-1">How Clustering Works</div>
                            <p className="text-slate-200">K-Means groups reports by spatial proximity. If you see "2 Reports" in separate blocks, it means those reports are in different locations (e.g., Street A vs Street B), not duplicates of each other.</p>
                            <div className="absolute top-full right-4 -mt-1 border-4 border-transparent border-t-slate-800"></div>
                        </div>
                    </span>
                    <button
                        onClick={handleExport}
                        className="bg-green-600 text-white px-4 py-2 rounded-lg shadow-md hover:bg-green-700 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200 font-medium active:scale-95"
                    >
                        Export CSV
                    </button>
                </div>
            </div>

            {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[1, 2, 3, 4, 5, 6].map((i) => (
                        <div key={i} className="bg-white rounded-xl p-6 shadow-sm border border-slate-100 animate-pulse">
                            <div className="h-4 bg-slate-200 rounded w-1/4 mb-4"></div>
                            <div className="flex items-center mb-4">
                                <div className="bg-slate-200 h-12 w-12 rounded-full mr-4"></div>
                                <div className="space-y-2">
                                    <div className="h-4 bg-slate-200 rounded w-32"></div>
                                    <div className="h-3 bg-slate-200 rounded w-20"></div>
                                </div>
                            </div>
                            <div className="space-y-2">
                                <div className="h-3 bg-slate-200 rounded w-full"></div>
                                <div className="h-3 bg-slate-200 rounded w-full"></div>
                            </div>
                        </div>
                    ))}
                </div>
            ) : hotspots.length === 0 ? (
                <div className="text-center py-20 bg-white rounded-xl shadow-sm border border-slate-100">
                    <svg className="mx-auto h-12 w-12 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    <h3 className="mt-2 text-sm font-medium text-slate-900">No hotspots found</h3>
                    <p className="mt-1 text-sm text-slate-500">Get started by submitting a new report.</p>
                    <div className="mt-6">
                        <a href="/report/new" className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                            Submit Report
                        </a>
                    </div>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {hotspots.map((hotspot, index) => (
                        <div
                            key={index}
                            className="bg-white rounded-xl p-6 shadow-lg hover:shadow-2xl transition-all duration-500 hover:-translate-y-2 border border-slate-100 relative overflow-hidden group animate-fade-in-up"
                            style={{ animationDelay: `${index * 0.1}s`, animationFillMode: 'both' }}
                        >
                            <div className="absolute top-0 right-0 bg-gradient-to-bl from-blue-600 to-blue-500 text-white px-4 py-1.5 rounded-bl-xl text-sm font-bold shadow-sm z-10">
                                #{index + 1}
                            </div>
                            <div className="absolute inset-0 bg-gradient-to-r from-blue-50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"></div>

                            <div className="flex items-center mb-6 relative z-10">
                                <div className="bg-blue-100 p-2 rounded-2xl text-blue-600 mr-4 group-hover:scale-110 group-hover:rotate-3 transition-transform duration-300 shadow-inner overflow-hidden h-16 w-16 flex-shrink-0">
                                    {hotspot.image ? (
                                        <img src={`http://localhost:8000${hotspot.image}`} alt="Hotspot" className="w-full h-full object-cover rounded-xl" />
                                    ) : (
                                        <div className="w-full h-full flex items-center justify-center">
                                            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                            </svg>
                                        </div>
                                    )}
                                </div>
                                <div>
                                    <h3 className="font-bold text-lg text-slate-800 group-hover:text-blue-700 transition-colors line-clamp-1" title={hotspot.title || "Hotspot Zone"}>
                                        {hotspot.title || "Hotspot Zone"}
                                    </h3>
                                    <div className="flex items-center mt-1 space-x-2">
                                        <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded-full">
                                            {hotspot.count} Reports
                                        </span>
                                        {hotspot.count > 1 && (
                                            <span className="text-xs text-slate-500">
                                                (+{hotspot.count - 1} others)
                                            </span>
                                        )}
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-3 text-sm text-slate-600 relative z-10 bg-slate-50 p-3 rounded-lg group-hover:bg-white transition-colors border border-transparent group-hover:border-slate-100">
                                <p className="text-xs text-slate-500 line-clamp-2 italic mb-2">
                                    "{hotspot.description || "No description available"}"
                                </p>
                                <div className="flex justify-between items-center border-t border-slate-200 pt-2">
                                    <span className="font-medium text-slate-500">Score</span>
                                    <span className="font-bold text-blue-600">{hotspot.score?.toFixed(1) || "N/A"}</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default HotspotList;
