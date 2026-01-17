import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, MapPin, Calendar, ThumbsUp, MessageSquare, Send } from 'lucide-react';
import Navbar from '../../components/shared/Navbar';
import Button from '../../components/shared/Button';
import Card from '../../components/shared/Card';
import Badge from '../../components/shared/Badge';
import AIAnalysisCard from '../../components/AIAnalysisCard';
import './ReportDetail.css';

const MOCK_REPORT = {
    id: 1,
    title: 'Pothole on Main Street',
    category: 'Roads',
    location: '123 Main St, Downtown',
    status: 'In Progress',
    description: 'Large pothole causing traffic issues. Approximately 2 feet in diameter and 6 inches deep. Located near the intersection with Park Avenue.',
    imageUrl: 'https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?auto=format&fit=crop&q=80&w=800',
    upvotes: 12,
    createdAt: '2023-11-20T10:00:00Z',
    updatedAt: '2023-11-21T14:30:00Z',
    reporter: 'John Doe',
    assignedTo: 'Roads Department',
    comments: [
        { id: 1, user: 'Jane Smith', text: 'This is a serious issue, thanks for reporting!', createdAt: '2023-11-20T12:00:00Z' },
        { id: 2, user: 'Roads Dept', text: 'We have assigned a crew to fix this. Expected completion: 2 days.', createdAt: '2023-11-21T09:00:00Z' }
    ]
};

const ReportDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(true);
    const [comment, setComment] = useState('');
    const [upvoted, setUpvoted] = useState(false);

    useEffect(() => {
        const fetchReport = async () => {
            try {
                const response = await axios.get(`http://localhost:8000/reports/${id}`);
                setReport(response.data);
                setLoading(false);
            } catch (error) {
                console.error("Error fetching report:", error);
                // Fallback to mock if needed, or just loading state
                setLoading(false);
            }
        };
        fetchReport();
    }, [id]);

    if (loading) return <div className="p-lg text-center">Loading...</div>;
    if (!report) return <div className="p-lg text-center">Report not found</div>;

    const getStatusVariant = (status) => {
        switch (status.toLowerCase()) {
            case 'resolved': return 'success';
            case 'in progress': return 'warning';
            case 'pending': return 'danger';
            default: return 'neutral';
        }
    };

    const handleUpvote = () => {
        setUpvoted(!upvoted);
    };

    const handleCommentSubmit = (e) => {
        e.preventDefault();
        // Mock comment submission
        setComment('');
    };

    return (
        <div className="min-h-screen bg-background">
            <Navbar />

            <main className="container py-lg">
                <Button
                    variant="ghost"
                    icon={ArrowLeft}
                    onClick={() => navigate('/citizen/dashboard')}
                    className="mb-md"
                >
                    Back to Dashboard
                </Button>

                <div className="report-detail-container">
                    <div className="report-detail-main">
                        <Card>
                            <div className="flex justify-between items-start mb-md">
                                <div>
                                    <h1 className="text-2xl mb-sm">{report.title}</h1>
                                    <div className="flex gap-sm items-center flex-wrap">
                                        <Badge variant="neutral">{report.category}</Badge>
                                        <Badge variant={getStatusVariant(report.status)}>{report.status}</Badge>
                                    </div>
                                </div>
                            </div>

                            <div className="report-image-container mb-md">
                                <img src={report.imageUrl} alt={report.title} className="report-detail-image" />
                            </div>

                            <div className="report-meta mb-md">
                                <div className="meta-item">
                                    <MapPin size={16} />
                                    <span>{report.location}</span>
                                </div>
                                <div className="meta-item">
                                    <Calendar size={16} />
                                    <span>Reported on {new Date(report.createdAt).toLocaleDateString()}</span>
                                </div>
                            </div>

                            <div className="report-description mb-lg">
                                <h3 className="text-lg mb-sm">Description</h3>
                                <p className="text-secondary">{report.description}</p>
                            </div>

                            <div className="report-actions">
                                <Button
                                    variant={upvoted ? 'primary' : 'outline'}
                                    icon={ThumbsUp}
                                    onClick={handleUpvote}
                                >
                                    {upvoted ? 'Upvoted' : 'Upvote'} ({report.upvotes + (upvoted ? 1 : 0)})
                                </Button>
                            </div>
                        </Card>

                        <Card className="mt-lg">
                            <h3 className="text-lg mb-md flex items-center gap-sm">
                                <MessageSquare size={20} />
                                Comments ({report.comments.length})
                            </h3>

                            <form onSubmit={handleCommentSubmit} className="comment-form mb-lg">
                                <textarea
                                    className="form-textarea"
                                    placeholder="Add a comment..."
                                    rows="3"
                                    value={comment}
                                    onChange={(e) => setComment(e.target.value)}
                                />
                                <Button type="submit" icon={Send} disabled={!comment.trim()}>
                                    Post Comment
                                </Button>
                            </form>

                            <div className="comments-list">
                                {report.comments.map(c => (
                                    <div key={c.id} className="comment-item">
                                        <div className="comment-header">
                                            <span className="font-semibold">{c.user}</span>
                                            <span className="text-xs text-muted">
                                                {new Date(c.createdAt).toLocaleDateString()}
                                            </span>
                                        </div>
                                        <p className="comment-text">{c.text}</p>
                                    </div>
                                ))}
                            </div>
                        </Card>
                    </div>

                    <div className="report-detail-sidebar">
                        <Card>
                            <h3 className="text-lg mb-md">Report Information</h3>
                            <div className="info-list">
                                <div className="info-item">
                                    <span className="info-label">Reporter</span>
                                    <span className="info-value">{report.reporter}</span>
                                </div>
                                <div className="info-item">
                                    <span className="info-label">Assigned To</span>
                                    <span className="info-value">{report.assignedTo}</span>
                                </div>
                                <div className="info-item">
                                    <span className="info-label">Last Updated</span>
                                    <span className="info-value">
                                        {new Date(report.updatedAt).toLocaleDateString()}
                                    </span>
                                </div>
                            </div>
                        </Card>
                    </div>
                </Card>

                {/* AI Analysis Card */}
                {(report.final_priority_score || report.ai_details) && (
                    <Card className="mt-md border-l-4 border-l-primary">
                        <h3 className="text-lg mb-md flex items-center gap-sm">
                            <span className="text-primary">✨</span> AI Analysis
                        </h3>
                        <div className="info-list">
                            <div className="info-item">
                                <span className="info-label">Priority Score</span>
                                <Badge variant={report.final_priority_score > 70 ? 'danger' : 'warning'}>
                                    {report.final_priority_score || 'N/A'}/100
                                </Badge>
                            </div>
                            <div className="info-item">
                                <span className="info-label">Visual Severity</span>
                                <span className="info-value">{(report.visual_score * 100).toFixed(0)}%</span>
                            </div>
                            <div className="info-item">
                                <span className="info-label">Est. Depth</span>
                                <span className="info-value">{report.depth_score ? (report.depth_score > 0.7 ? "Deep" : "Shallow") : "N/A"}</span>
                            </div>
                            <div className="info-item">
                                <span className="info-label">Urgency</span>
                                <span className="info-value">{(report.urgency_score * 100).toFixed(0)}%</span>
                            </div>
                            <div className="info-item">
                                <span className="info-label">Location Context</span>
                                <span className="info-value">{(report.location_score * 100).toFixed(0)}%</span>
                            </div>
                        </div>
                    </Card>
                )}
        </div>
                </div >
            </main >
        </div >
    );
};

export default ReportDetail;
