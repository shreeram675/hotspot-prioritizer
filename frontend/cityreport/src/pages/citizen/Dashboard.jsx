import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus } from 'lucide-react';
import api from '../../api';
import Navbar from '../../components/shared/Navbar';
import Button from '../../components/shared/Button';
import ReportCard from '../../components/citizen/ReportCard';
import FilterBar from '../../components/shared/FilterBar';
import { useAuth } from '../../contexts/AuthContext';

const CitizenDashboard = () => {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [searchTerm, setSearchTerm] = useState('');
    const [filters, setFilters] = useState({ category: '', status: '' });

    useEffect(() => {
        fetchReports();
    }, []);

    const fetchReports = async () => {
        try {
            setLoading(true);
            const response = await api.get('/reports/');
            setReports(response.data);
            setError('');
        } catch (err) {
            console.error('Error fetching reports:', err);
            setError('Failed to load reports. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleWithdraw = async (id) => {
        try {
            await api.delete(`/reports/${id}`);
            setReports(prev => prev.filter(r => r.id !== id));
        } catch (err) {
            console.error('Error withdrawing report:', err);
            alert("Failed to withdraw report.");
        }
    };

    const handleSearch = (term) => {
        setSearchTerm(term);
        // Implement client-side filtering if needed, or API call
    };

    const handleFilterChange = (type, value) => {
        setFilters(prev => ({ ...prev, [type]: value }));
    };

    const handleSortChange = (value) => {
        // Implement sort
    };

    const handleUpvote = async (id) => {
        try {
            await api.post(`/reports/${id}/upvote`);
            fetchReports();
        } catch (err) {
            console.error('Error upvoting report:', err);
        }
    };

    const handleReportClick = (id) => {
        navigate(`/citizen/report/${id}`);
    };

    // Filter logic
    const filteredReports = reports.filter(report => {
        const matchesSearch = report.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
            report.description.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesCategory = filters.category ? report.category === filters.category : true;
        const matchesStatus = filters.status ? report.status === filters.status : true;
        return matchesSearch && matchesCategory && matchesStatus;
    });

    return (
        <div className="min-h-screen bg-background">
            <Navbar />

            <main className="container py-lg">
                {/* Hero / Action Section */}
                <div className="flex flex-col md:flex-row justify-between items-center mb-lg gap-md">
                    <div>
                        <h1 className="text-2xl mb-xs">Welcome Back, Citizen</h1>
                        <p className="text-muted">Report issues and track their progress in your city.</p>
                    </div>
                    <Button
                        variant="primary"
                        size="lg"
                        icon={Plus}
                        onClick={() => navigate('/citizen/report/new')}
                    >
                        Report an Issue
                    </Button>
                </div>

                {/* Filters */}
                <FilterBar
                    onSearch={handleSearch}
                    onFilterChange={handleFilterChange}
                    onSortChange={handleSortChange}
                />

                {/* Error Message */}
                {error && (
                    <div style={{
                        padding: '1rem',
                        marginBottom: '1rem',
                        backgroundColor: '#fee',
                        color: '#c00',
                        borderRadius: '0.5rem'
                    }}>
                        {error}
                    </div>
                )}

                {/* Loading State */}
                {loading && (
                    <div className="text-center py-lg">
                        <p>Loading reports...</p>
                    </div>
                )}

                {/* Reports Grid */}
                {!loading && !error && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-lg">
                        {filteredReports.length > 0 ? (
                            filteredReports.map(report => (
                                <ReportCard
                                    key={report.id}
                                    report={report}
                                    onUpvote={handleUpvote}
                                    onClick={handleReportClick}
                                    onWithdraw={handleWithdraw}
                                    isOwner={user && user.id === report.user_id}
                                />
                            ))
                        ) : (
                            <div className="col-span-full text-center py-lg">
                                <p className="text-muted">No reports found via search/filter.</p>
                            </div>
                        )}
                    </div>
                )}
            </main>
        </div>
    );
};

export default CitizenDashboard;
