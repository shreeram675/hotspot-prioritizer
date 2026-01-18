import { useAuth } from '../../contexts/AuthContext';

const CitizenDashboard = () => {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [reports, setReports] = useState([]);

    // ... (rest of state)

    // ... (fetchReports)

    const handleWithdraw = async (id) => {
        try {
            await api.delete(`/reports/${id}`);
            // Optimistically remove from UI or refetch
            setReports(prev => prev.filter(r => r.id !== id));
        } catch (err) {
            console.error('Error withdrawing report:', err);
            alert("Failed to withdraw report.");
        }
    };

    // ... (rest of handlers)

    return (
        // ... (jsx)
        {!loading && !error && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-lg">
                {reports.length > 0 ? (
                    reports.map(report => (
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
    // ...
    const [loading, setLoading] = useState(true);
                const [error, setError] = useState('');
                const [searchTerm, setSearchTerm] = useState('');
                const [filters, setFilters] = useState({category: '', status: '' });

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

    const handleSearch = (term) => {
                    setSearchTerm(term);
        // Implement search logic here
    };

    const handleFilterChange = (type, value) => {
                    setFilters(prev => ({ ...prev, [type]: value }));
        // Implement filter logic here
    };

    const handleSortChange = (value) => {
                    // Implement sort logic here
                };

    const handleUpvote = async (id) => {
        try {
                    await api.post(`/reports/${id}/upvote`);
                // Refresh reports after upvote
                fetchReports();
        } catch (err) {
                    console.error('Error upvoting report:', err);
        }
    };

    const handleReportClick = (id) => {
                    navigate(`/citizen/report/${id}`);
    };

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
                                {reports.length > 0 ? (
                                    reports.map(report => (
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
                                        <p className="text-muted">No reports found. Be the first to report an issue!</p>
                                    </div>
                                )}
                            </div>
                        )}
                    </main>
                </div>
                );
};

                export default CitizenDashboard;
