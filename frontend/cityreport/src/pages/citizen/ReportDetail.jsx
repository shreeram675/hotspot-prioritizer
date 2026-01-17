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
    category: 'Road Issues',
    location: '123 Main St, Downtown',
    status: 'In Progress',
    severity: 'Medium',
    priority: 'High',
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
        // For now, just use mock data immediately
        setReport(MOCK_REPORT);
        setLoading(false);

        // Try to fetch real data but don't block on it
        try {
          const response = await axios.get(
            `http://localhost:8005/reports/${id}`,
          );
          console.log("Report fetched:", response.data);
          setReport(response.data);
        } catch (error) {
          console.error("Error fetching report:", error);
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
      <div style={{ padding: '20px' }}>
        <button onClick={() => navigate("/citizen/dashboard")} style={{ marginBottom: '20px' }}>
          ← Back to Dashboard
        </button>
        <h1>{report.title}</h1>
        <p><strong>ID:</strong> {report.id}</p>
        <p><strong>Category:</strong> {report.category}</p>
        <p><strong>Status:</strong> {report.status}</p>
        <p><strong>Location:</strong> {report.location}</p>
        <p><strong>Description:</strong> {report.description}</p>
        <p><strong>Upvotes:</strong> {report.upvotes}</p>
      </div>
    );
};

export default ReportDetail;
