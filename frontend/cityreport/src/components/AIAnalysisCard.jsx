import React from 'react';
import Card from './shared/Card';
import Badge from './shared/Badge';
import './AIAnalysisCard.css';

const AIAnalysisCard = ({ report }) => {
    if (!report.ai_severity_score) {
        return null; // Don't show if no AI analysis
    }

    const isPothole = report.category === 'pothole';
    const isGarbage = report.category === 'garbage';

    const getSeverityColor = (score) => {
        if (score > 75) return 'danger';
        if (score > 50) return 'warning';
        if (score > 25) return 'neutral';
        return 'success';
    };

    const ScoreBar = ({ label, value }) => {
        if (value === null || value === undefined) return null;

        const percentage = Math.round(value * 100);

        return (
            <div className="score-bar-container">
                <div className="score-bar-header">
                    <span className="score-label">{label}</span>
                    <span className="score-value">{percentage}%</span>
                </div>
                <div className="score-bar-track">
                    <div
                        className="score-bar-fill"
                        style={{ width: `${percentage}%` }}
                    />
                </div>
            </div>
        );
    };

    return (
        <Card className="ai-analysis-card">
            <div className="ai-analysis-header">
                <h3>🤖 AI Severity Analysis</h3>
                <Badge variant={getSeverityColor(report.ai_severity_score)}>
                    {report.ai_severity_level?.toUpperCase() || 'UNKNOWN'}
                </Badge>
            </div>

            <div className="severity-score-display">
                <div className="circular-progress">
                    <svg viewBox="0 0 100 100">
                        <circle cx="50" cy="50" r="45" className="progress-bg" />
                        <circle
                            cx="50"
                            cy="50"
                            r="45"
                            className="progress-fill"
                            style={{
                                strokeDasharray: `${report.ai_severity_score * 2.827} 282.7`,
                                stroke: report.ai_severity_score > 75 ? '#ef4444' :
                                    report.ai_severity_score > 50 ? '#f59e0b' :
                                        report.ai_severity_score > 25 ? '#6b7280' : '#10b981'
                            }}
                        />
                    </svg>
                    <div className="progress-text">
                        <span className="progress-value">{Math.round(report.ai_severity_score)}</span>
                        <span className="progress-label">/100</span>
                    </div>
                </div>
            </div>

            <div className="score-breakdown">
                <h4>Score Breakdown</h4>

                {isPothole && (
                    <>
                        <ScoreBar label="Depth" value={report.pothole_depth_score} />
                        <ScoreBar label="Spread" value={report.pothole_spread_score} />
                    </>
                )}

                {isGarbage && (
                    <>
                        <ScoreBar label="Volume" value={report.garbage_volume_score} />
                        <ScoreBar label="Hazard Level" value={report.garbage_waste_type_score} />
                    </>
                )}

                <ScoreBar label="Urgency" value={report.emotion_score} />
                <ScoreBar label="Location Risk" value={report.location_score} />
            </div>
        </Card>
    );
};

export default AIAnalysisCard;
