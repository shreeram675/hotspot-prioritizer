import { MapPin, ThumbsUp, MessageSquare, Trash2 } from 'lucide-react';
import Card from '../shared/Card';
import Badge from '../shared/Badge';
import Button from '../shared/Button';
import './ReportCard.css';

const ReportCard = ({ report, onUpvote, onClick, onWithdraw, isOwner }) => {
    const {
        id,
        title,
        category,
        location,
        status,
        image_url,
        imageUrl,
        upvotes,
        commentsCount,
        createdAt,
        created_at
    } = report;

    const getStatusVariant = (status) => {
        switch (status.toLowerCase()) {
            case 'resolved': return 'success';
            case 'in progress': return 'warning';
            case 'pending': return 'danger';
            default: return 'neutral';
        }
    };

    return (
        <Card className="report-card" padding="none" onClick={() => onClick(id)}>
            <div className="report-image-container">
                <img
                    src={image_url ? (image_url.startsWith('/upload') ? `http://localhost:8005${image_url}` : image_url) : (imageUrl ? (imageUrl.startsWith('/upload') ? `http://localhost:8005${imageUrl}` : imageUrl) : 'https://via.placeholder.com/400x200?text=No+Image')}
                    alt={title}
                    className="report-image"
                />
                <div className="report-category-badge">
                    <Badge variant="neutral">{category}</Badge>
                </div>
            </div>

            <div className="report-content p-md">
                <div className="flex justify-between items-start mb-sm">
                    <h3 className="text-lg font-semibold report-title">{title}</h3>
                    <Badge variant={getStatusVariant(status)}>{status}</Badge>
                </div>

                <div className="flex items-center text-muted text-sm mb-md">
                    <MapPin size={14} className="mr-1" />
                    <span className="truncate">{location}</span>
                </div>

                <div className="flex justify-between items-center mt-auto pt-sm border-t">
                    <div className="flex gap-md">
                        <Button
                            variant="ghost"
                            size="sm"
                            className="action-btn"
                            onClick={(e) => {
                                e.stopPropagation();
                                onUpvote(id);
                            }}
                        >
                            <ThumbsUp size={16} />
                            <span>{upvotes}</span>
                        </Button>

                        <div className="flex items-center gap-xs text-muted text-sm">
                            <MessageSquare size={16} />
                            <span>{commentsCount}</span>
                        </div>

                        {isOwner && (
                            <Button
                                variant="ghost"
                                size="sm"
                                className="action-btn text-danger hover:text-danger hover:bg-red-50"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    if (window.confirm("Are you sure you want to withdraw this report?")) {
                                        onWithdraw(id);
                                    }
                                }}
                                title="Withdraw Report"
                            >
                                <Trash2 size={16} />
                            </Button>
                        )}
                    </div>

                    <span className="text-xs text-muted">
                        {new Date(createdAt || created_at).toLocaleDateString()}
                    </span>
                </div>
            </div>
        </Card>
    );
};

export default ReportCard;
