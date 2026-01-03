import React, { useEffect, useState } from 'react';
import axios from 'axios';
import AnalyticsWidgets from './AnalyticsWidgets';
import ReportDetailModal from './ReportDetailModal';

const AdminDashboard = () => {
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedReport, setSelectedReport] = useState(null);
    const [filterStatus, setFilterStatus] = useState('all'); // all, open, in_progress, resolved
    const [sortBy, setSortBy] = useState('date_desc'); // date_desc, date_asc, severity_desc, severity_asc

    useEffect(() => {
        fetchReports();
    }, [filterStatus]);

    const fetchReports = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            const params = {};
            if (filterStatus !== 'all') params.status = filterStatus;

            const response = await axios.get('http://localhost:8000/reports/', {
                params,
                headers: { Authorization: `Bearer ${token}` }
            });
            setReports(response.data);
        } catch (error) {
            console.error("Error fetching reports:", error);
        } finally {
            setLoading(false);
        }
    };

    const getSortedReports = () => {
        const sorted = [...reports];
        return sorted.sort((a, b) => {
            if (sortBy === 'date_desc') return new Date(b.created_at) - new Date(a.created_at);
            if (sortBy === 'date_asc') return new Date(a.created_at) - new Date(b.created_at);
            if (sortBy === 'severity_desc') return (b.ai_severity_score || 0) - (a.ai_severity_score || 0);
            if (sortBy === 'severity_asc') return (a.ai_severity_score || 0) - (b.ai_severity_score || 0);
            return 0;
        });
    };

    const handleStatusUpdate = async (reportId, newStatus) => {
        const note = prompt("Enter a note for this status change (optional):");
        try {
            const token = localStorage.getItem('token');
            await axios.patch(`http://localhost:8000/reports/${reportId}/status`,
                { status: newStatus, note },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            fetchReports();
        } catch (error) {
            console.error("Update failed:", error);
            alert("Failed to update status");
        }
    };

    const handleAssign = async (reportId) => {
        const staffName = prompt("Enter Staff Name:");
        if (!staffName) return;
        const staffPhone = prompt("Enter Staff Phone:");

        try {
            const token = localStorage.getItem('token');
            await axios.post(`http://localhost:8000/reports/${reportId}/assign`,
                { staff_name: staffName, staff_phone: staffPhone || "" },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            fetchReports();
        } catch (error) {
            console.error("Assignment failed:", error);
            alert("Failed to assign");
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pt-24">
            <div className="flex justify-between items-center mb-8 relative z-10">
                <h1 className="text-3xl font-bold text-slate-900">Issue Management</h1>
                <div className="flex gap-4">
                    {/* Sort Dropdown */}
                    <div className="relative">
                        <select
                            value={sortBy}
                            onChange={(e) => setSortBy(e.target.value)}
                            className="bg-white border border-slate-300 text-slate-700 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 shadow-sm"
                        >
                            <option value="date_desc">Recent First</option>
                            <option value="date_asc">Oldest First</option>
                            <option value="severity_desc">Highest Severity</option>
                            <option value="severity_asc">Lowest Severity</option>
                        </select>
                    </div>

                    <div className="flex space-x-2">
                        {['all', 'open', 'in_progress', 'resolved'].map(status => (
                            <button
                                key={status}
                                onClick={() => setFilterStatus(status)}
                                className={`px-4 py-2 rounded-lg text-sm font-medium capitalize transition-colors ${filterStatus === status
                                    ? 'bg-blue-600 text-white shadow-md'
                                    : 'bg-white text-slate-600 hover:bg-slate-50 border border-slate-200'
                                    }`}
                            >
                                {status.replace('_', ' ')}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            <AnalyticsWidgets />

            <div className="bg-white shadow-sm rounded-xl overflow-hidden border border-slate-200">
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-slate-200">
                        <thead className="bg-slate-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">ID</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Issue</th>
                                <th className="px-6 py-3 text-center text-xs font-medium text-slate-500 uppercase tracking-wider">Score</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Category</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Status</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Upvotes</th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-slate-200">
                            {loading ? (
                                <tr><td colSpan="7" className="px-6 py-10 text-center text-slate-500">Loading...</td></tr>
                            ) : reports.length === 0 ? (
                                <tr><td colSpan="7" className="px-6 py-10 text-center text-slate-500">No reports found</td></tr>
                            ) : getSortedReports().map((report) => (
                                <tr key={report.report_id} className="hover:bg-slate-50 transition-colors">
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">#{report.report_id}</td>
                                    <td className="px-6 py-4 cursor-pointer hover:bg-slate-100" onClick={() => setSelectedReport(report)}>
                                        <div className="text-sm font-medium text-blue-600 hover:underline">{report.title}</div>
                                        <div className="text-sm text-slate-500 truncate max-w-xs">{report.description}</div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-center">
                                        <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-xs font-bold ${(report.ai_severity_score || 0) >= 75 ? 'bg-red-100 text-red-800' :
                                            (report.ai_severity_score || 0) >= 50 ? 'bg-orange-100 text-orange-800' :
                                                'bg-green-100 text-green-800'
                                            }`}>
                                            {report.ai_severity_score || 0}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{report.category}</td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full capitalize ${report.status === 'resolved' ? 'bg-green-100 text-green-800' :
                                            report.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' :
                                                'bg-red-100 text-red-800'
                                            }`}>
                                            {report.status.replace('_', ' ')}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                                        👍 {report.upvote_count}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                                        <button
                                            onClick={() => handleAssign(report.report_id)}
                                            className="text-indigo-600 hover:text-indigo-900 bg-indigo-50 px-3 py-1 rounded-md hover:bg-indigo-100 transition-colors"
                                        >
                                            Assign
                                        </button>
                                        <select
                                            value={report.status}
                                            onChange={(e) => handleStatusUpdate(report.report_id, e.target.value)}
                                            className="text-sm border-slate-300 rounded-md text-slate-700 focus:ring-blue-500 focus:border-blue-500"
                                        >
                                            <option value="open">Open</option>
                                            <option value="in_progress">In Progress</option>
                                            <option value="resolved">Resolved</option>
                                        </select>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>


            {/* Detail Modal */}
            {
                selectedReport && (
                    <ReportDetailModal
                        report={selectedReport}
                        onClose={() => setSelectedReport(null)}
                    />
                )
            }
        </div >
    );
};

export default AdminDashboard;
