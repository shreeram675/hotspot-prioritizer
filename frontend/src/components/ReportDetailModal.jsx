import React from 'react';

const ReportDetailModal = ({ report, onClose }) => {
    if (!report) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={onClose}>
            <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
                {/* Header */}
                <div className="sticky top-0 bg-white border-b border-slate-200 p-6 flex justify-between items-start">
                    <div>
                        <h2 className="text-2xl font-bold text-slate-800">{report.title}</h2>
                        <div className="flex gap-2 mt-2">
                            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${report.status === 'open' ? 'bg-green-100 text-green-700' :
                                report.status === 'in_progress' ? 'bg-blue-100 text-blue-700' :
                                    'bg-gray-100 text-gray-700'
                                }`}>
                                {report.status}
                            </span>
                            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-purple-100 text-purple-700">
                                {report.category}
                            </span>
                            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${report.severity === 'High' ? 'bg-red-100 text-red-700' :
                                report.severity === 'Medium' ? 'bg-orange-100 text-orange-700' :
                                    'bg-yellow-100 text-yellow-700'
                                }`}>
                                {report.severity}
                            </span>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-slate-400 hover:text-slate-600 transition-colors"
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {/* Description */}
                    <div>
                        <h3 className="text-sm font-semibold text-slate-600 mb-2">Description</h3>
                        <p className="text-slate-700 leading-relaxed">{report.description}</p>
                    </div>

                    {/* Images */}
                    {report.images && report.images.length > 0 && (
                        <div>
                            <h3 className="text-sm font-semibold text-slate-600 mb-3">Images</h3>
                            <div className="grid grid-cols-2 gap-3">
                                {report.images.map((img, idx) => (
                                    <img
                                        key={idx}
                                        src={`http://localhost:8000${img.file_path}`}
                                        alt={`Report image ${idx + 1}`}
                                        className="w-full h-48 object-cover rounded-lg border border-slate-200"
                                    />
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Location */}
                    {report.address && (
                        <div>
                            <h3 className="text-sm font-semibold text-slate-600 mb-2">Location</h3>
                            <p className="text-slate-700 flex items-center">
                                <svg className="w-4 h-4 mr-2 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                </svg>
                                {report.address}
                            </p>
                        </div>
                    )}

                    {/* AI Analysis Section */}
                    <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-4">
                        <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                            <h3 className="font-bold text-slate-800 flex items-center gap-2">
                                <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                                AI Analysis Report
                            </h3>
                            <span className="bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-xs font-bold">
                                Score: {report.ai_severity_score}/100
                            </span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* Severity Metrics */}
                            <div className="space-y-2">
                                <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Severity Metrics</h4>
                                <div className="grid grid-cols-2 gap-2 text-sm">
                                    <div className="bg-white p-2 rounded border border-slate-100">
                                        <div className="text-slate-500 text-xs">Category</div>
                                        <div className="font-medium text-slate-800">{report.ai_severity_category || 'N/A'}</div>
                                    </div>
                                    <div className="bg-white p-2 rounded border border-slate-100">
                                        <div className="text-slate-500 text-xs">Object Count</div>
                                        <div className="font-medium text-slate-800">{report.ai_object_count || 0} items</div>
                                    </div>
                                    <div className="bg-white p-2 rounded border border-slate-100">
                                        <div className="text-slate-500 text-xs">Coverage</div>
                                        <div className="font-medium text-slate-800">{Math.round((report.ai_coverage_area || 0) * 100)}%</div>
                                    </div>
                                    <div className="bg-white p-2 rounded border border-slate-100">
                                        <div className="text-slate-500 text-xs">Dirtiness</div>
                                        <div className="font-medium text-slate-800">{Math.round((report.ai_scene_dirtiness || 0) * 100)}%</div>
                                    </div>
                                </div>
                            </div>

                            {/* Waste Classification */}
                            <div className="space-y-2">
                                <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Waste Classification</h4>
                                <div className="space-y-2 text-sm">
                                    <div className="bg-white p-2 rounded border border-slate-100 flex justify-between items-center">
                                        <span className="text-slate-500">Primary Type</span>
                                        <span className="font-medium text-slate-800 capitalize">{report.waste_primary_type?.replace('_', ' ') || 'Unknown'}</span>
                                    </div>
                                    <div className="bg-white p-2 rounded border border-slate-100 flex justify-between items-center">
                                        <span className="text-slate-500">Hazardous?</span>
                                        <span className={`font-medium ${report.is_hazardous_waste ? 'text-red-600' : 'text-green-600'}`}>
                                            {report.is_hazardous_waste ? 'YES' : 'No'}
                                        </span>
                                    </div>
                                    <div className="bg-white p-2 rounded border border-slate-100">
                                        <span className="text-slate-500 block mb-1">Composition</span>
                                        <div className="flex flex-wrap gap-1">
                                            {report.waste_composition && Object.entries(report.waste_composition).map(([key, val]) => (
                                                <span key={key} className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded">
                                                    {key}: {Math.round(val * 100)}%
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Context & Sentiment */}
                            <div className="space-y-2 md:col-span-2">
                                <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Context & Insights</h4>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                                    <div className="bg-white p-2 rounded border border-slate-100">
                                        <div className="text-slate-500 text-xs">Location Context</div>
                                        <div className="font-medium text-slate-800">
                                            Priority Multiplier: x{report.location_priority_multiplier || 1.0}
                                        </div>
                                        <div className="text-xs text-slate-500 mt-1">
                                            {report.location_context && Object.keys(report.location_context).join(', ')}
                                        </div>
                                    </div>
                                    <div className="bg-white p-2 rounded border border-slate-100">
                                        <div className="text-slate-500 text-xs">Text Analysis</div>
                                        <div className="font-medium text-slate-800 capitalize">
                                            Emotion: {report.text_emotion_category || 'Neutral'}
                                        </div>
                                        <div className="text-xs text-slate-500 mt-1">
                                            Keywords: {report.text_urgency_keywords || 'None'}
                                        </div>
                                    </div>
                                </div>
                                {report.ai_confidence_explanation && (
                                    <div className="bg-blue-50 p-3 rounded text-sm text-blue-800 border border-blue-100 mt-2">
                                        <strong>AI Note:</strong> {report.ai_confidence_explanation}
                                    </div>
                                )}
                                {report.waste_disposal_recommendations && (
                                    <div className="bg-green-50 p-3 rounded text-sm text-green-800 border border-green-100 mt-2">
                                        <strong>Recommendation:</strong> {report.waste_disposal_recommendations}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-200">
                        <div>
                            <h3 className="text-sm font-semibold text-slate-600 mb-1">Upvotes</h3>
                            <p className="text-2xl font-bold text-blue-600">{report.upvote_count || 0}</p>
                        </div>
                        <div>
                            <h3 className="text-sm font-semibold text-slate-600 mb-1">Reported</h3>
                            <p className="text-sm text-slate-700">
                                {new Date(report.created_at).toLocaleDateString('en-US', {
                                    year: 'numeric',
                                    month: 'short',
                                    day: 'numeric'
                                })}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ReportDetailModal;
