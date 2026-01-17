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
          const response = await axios.get(
            `http://localhost:8005/reports/${id}`,
          );
          console.log("Report fetched:", response.data);
          setReport(response.data);
          setLoading(false);
        } catch (error) {
          console.error("Error fetching report:", error);
          console.log("Using mock data as fallback");
          setReport(MOCK_REPORT);
          setLoading(false);
        }
      };
      fetchReport();
    }, [id]);

    if (loading) return <div className="p-lg text-center">Loading...</div>;
    if (!report)
      return <div className="p-lg text-center">Report not found</div>;

    const getStatusVariant = (status) => {
      switch (status.toLowerCase()) {
        case "resolved":
          return "success";
        case "in progress":
          return "warning";
        case "pending":
          return "danger";
        default:
          return "neutral";
      }
    };

    const handleUpvote = () => {
      setUpvoted(!upvoted);
    };

    const handleCommentSubmit = (e) => {
      e.preventDefault();
      // Mock comment submission
      setComment("");
    };

    return (
      <div className="min-h-screen bg-background">
        <Navbar />

        <main className="container py-lg">
          <Button
            variant="ghost"
            icon={ArrowLeft}
            onClick={() => navigate("/citizen/dashboard")}
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
                      <Badge variant={getStatusVariant(report.status)}>
                        {report.status}
                      </Badge>
                    </div>
                  </div>
                </div>

                <div className="report-image-container mb-md">
                  {report.image_url && (
                    <img
                      src={report.image_url}
                      alt={report.title}
                      className="report-detail-image"
                    />
                  )}
                </div>

                <div className="report-meta mb-md">
                  <div className="meta-item">
                    <MapPin size={16} />
                    <span>
                      Location:{" "}
                      {report.latitude && report.longitude
                        ? `${report.latitude}, ${report.longitude}`
                        : report.location || "Unknown"}
                    </span>
                  </div>
                  <div className="meta-item">
                    <Calendar size={16} />
                    <span>
                      Reported on{" "}
                      {new Date(
                        report.created_at || report.createdAt
                      ).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <div className="report-description mb-lg">
                  <h3 className="text-lg mb-sm">Description</h3>
                  <p className="text-secondary">{report.description}</p>
                </div>

                <div className="report-actions">
                  <Button
                    variant={upvoted ? "primary" : "outline"}
                    icon={ThumbsUp}
                    onClick={handleUpvote}
                  >
                    {upvoted ? "Upvoted" : "Upvote"} (
                    {report.upvotes + (upvoted ? 1 : 0)})
                  </Button>
                </div>
              </Card>

              <Card className="mt-lg">
                <h3 className="text-lg mb-md flex items-center gap-sm">
                  <MessageSquare size={20} />
                  Comments ({report.comments ? report.comments.length : 0})
                </h3>

                <form
                  onSubmit={handleCommentSubmit}
                  className="comment-form mb-lg"
                >
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
                  {report.comments &&
                    report.comments.map((c) => (
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
                    <span className="info-label">ID</span>
                    <span className="info-value">{report.id}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Status</span>
                    <span className="info-value">{report.status}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Severity</span>
                    <span className="info-value">{report.severity}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Priority</span>
                    <span className="info-value">{report.priority}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Upvotes</span>
                    <span className="info-value">{report.upvotes}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Last Updated</span>
                    <span className="info-value">
                      {new Date(
                        report.updated_at || report.created_at,
                      ).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </Card>

              {/* AI Analysis Card */}
              <AIAnalysisCard report={report} />
            </div>
          </div>
        </main>
      </div>
    );
};

export default ReportDetail;
