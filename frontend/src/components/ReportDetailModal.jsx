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

                    {/* Metadata */}
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
