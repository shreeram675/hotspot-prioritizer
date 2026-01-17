import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, CheckCircle, AlertCircle, Filter } from 'lucide-react';
import Navbar from '../../components/shared/Navbar';
import Card from '../../components/shared/Card';
import Badge from '../../components/shared/Badge';
import Button from '../../components/shared/Button';
import api from '../../api';
import './OfficerDashboard.css';

const OfficerDashboard = () => {
    const navigate = useNavigate();
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const [priorityFilter, setPriorityFilter] = useState('');
    const [categoryFilter, setCategoryFilter] = useState('');

    useEffect(() => {
        fetchReports();
    }, [filter, priorityFilter, categoryFilter]);

    const fetchReports = async () => {
        try {
            setLoading(true);
            const params = {
                sort_by: 'priority',
                sort_order: 'desc'
            };

            if (filter !== 'all') {
                params.status = filter;
            }
            if (priorityFilter) {
                params.priority = priorityFilter;
            }
            if (categoryFilter) {
                params.category = categoryFilter;
            }

            const response = await api.get('/reports/', { params });
            setReports(response.data);
        } catch (err) {
            console.error('Error fetching reports:', err);
        } finally {
            setLoading(false);
        }
    };

    const stats = {
        pending: reports.filter(r => r.status === 'pending').length,
        inProgress: reports.filter(r => r.status === 'in_progress').length,
        resolved: reports.filter(r => r.status === 'resolved' || r.status === 'closed').length,
        critical: reports.filter(r => r.priority === 'critical').length
    };

    const getStatusVariant = (status) => {
        switch (status.toLowerCase()) {
            case 'resolved':
            case 'closed':
                return 'success';
            case 'in_progress':
            case 'assigned':
                return 'warning';
            case 'pending':
                return 'danger';
            default:
                return 'neutral';
        }
    };

    const getPriorityVariant = (priority) => {
        switch (priority.toLowerCase()) {
            case 'critical':
                return 'danger';
            case 'high':
                return 'warning';
            case 'medium':
                return 'info';
            default:
                return 'neutral';
        }
    };

    return (
      <div className="min-h-screen bg-background">
        <Navbar />

        <main className="container py-lg">
          <div className="dashboard-header">
            <div>
              <h1 className="text-2xl mb-xs">Officer Dashboard</h1>
              <p className="text-muted">
                Manage assigned reports and update their status
              </p>
            </div>
          </div>

          <div className="stats-grid">
            <Card className="stat-card">
              <div className="stat-icon pending">
                <Clock size={24} />
              </div>
              <div className="stat-content">
                <p className="stat-label">Pending</p>
                <p className="stat-value">{stats.pending}</p>
              </div>
            </Card>

            <Card className="stat-card">
              <div className="stat-icon in-progress">
                <AlertCircle size={24} />
              </div>
              <div className="stat-content">
                <p className="stat-label">In Progress</p>
                <p className="stat-value">{stats.inProgress}</p>
              </div>
            </Card>

            <Card className="stat-card">
              <div className="stat-icon resolved">
                <CheckCircle size={24} />
              </div>
              <div className="stat-content">
                <p className="stat-label">Resolved</p>
                <p className="stat-value">{stats.resolved}</p>
              </div>
            </Card>

            <Card className="stat-card">
              <div className="stat-icon critical">
                <AlertCircle size={24} />
              </div>
              <div className="stat-content">
                <p className="stat-label">Critical</p>
                <p className="stat-value">{stats.critical}</p>
              </div>
            </Card>
          </div>

          {/* Filter Panel */}
          <Card className="mt-lg mb-md" style={{ padding: "1.5rem" }}>
            <div className="flex items-center gap-sm mb-md">
              <Filter size={20} />
              <h3 className="font-semibold">Filters</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-md">
              <div>
                <label className="block text-sm font-medium mb-xs">
                  Priority
                </label>
                <select
                  value={priorityFilter}
                  onChange={(e) => setPriorityFilter(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "0.5rem",
                    border: "1px solid var(--border)",
                    borderRadius: "0.375rem",
                  }}
                >
                  <option value="">All Priorities</option>
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-xs">
                  Category
                </label>
                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "0.5rem",
                    border: "1px solid var(--border)",
                    borderRadius: "0.375rem",
                  }}
                >
                  <option value="">All Categories</option>
                  <option value="road_issues">Road Issues</option>
                  <option value="waste_management">Waste Management</option>
                </select>
              </div>
            </div>
          </Card>

          <Card className="mt-lg">
            <div className="flex justify-between items-center mb-md flex-wrap gap-md">
              <h2 className="text-xl">Assigned Reports</h2>
              <div className="filter-tabs">
                <button
                  className={`filter-tab ${filter === "all" ? "active" : ""}`}
                  onClick={() => setFilter("all")}
                >
                  All
                </button>
                <button
                  className={`filter-tab ${filter === "pending" ? "active" : ""}`}
                  onClick={() => setFilter("pending")}
                >
                  Pending
                </button>
                <button
                  className={`filter-tab ${filter === "in_progress" ? "active" : ""}`}
                  onClick={() => setFilter("in_progress")}
                >
                  In Progress
                </button>
              </div>
            </div>

            {loading ? (
              <div className="text-center py-lg">
                <p>Loading reports...</p>
              </div>
            ) : (
              <div className="reports-table-container">
                <table className="reports-table">
                  <thead>
                    <tr>
                      <th>Title</th>
                      <th>Category</th>
                      <th>Priority</th>
                      <th>Status</th>
                      <th>Created Date</th>
                      <th>Upvotes</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reports.map((report) => (
                      <tr key={report.id}>
                        <td className="font-semibold">{report.title}</td>
                        <td>{report.category}</td>
                        <td>
                          <Badge variant={getPriorityVariant(report.priority)}>
                            {report.priority}
                          </Badge>
                        </td>
                        <td>
                          <Badge variant={getStatusVariant(report.status)}>
                            {report.status}
                          </Badge>
                        </td>
                        <td>
                          {new Date(report.created_at).toLocaleDateString()}
                        </td>
                        <td>{report.upvotes}</td>
                        <td>
                          <Button
                            size="sm"
                            onClick={() =>
                              navigate(`/officer/report/${report.id}`)
                            }
                          >
                            Manage
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </main>
      </div>
    );
};

export default OfficerDashboard;
