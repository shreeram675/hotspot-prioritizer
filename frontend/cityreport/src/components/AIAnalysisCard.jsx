import React from 'react';
import Card from './shared/Card';
import Badge from './shared/Badge';
import './AIAnalysisCard.css';

const AIAnalysisCard = ({ report }) => {
    if (!report.ai_severity_score) {
        return null; // Don't show if no AI analysis
    }

    const isPothole = report.category === 'pothole' || report.category === 'road_issues';
    const isGarbage = report.category === 'garbage' || report.category === 'waste_management';

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

                <div className="score-group">
                    <ScoreBar label="Urgency" value={report.emotion_score} />
                    {report.sentiment_meta && (
                        <div className="meta-explanation text-xs text-muted mt-1 ml-2">
                            {/* Try to parse if string, else use as object */}
                            {(() => {
                                try {
                                    const meta = typeof report.sentiment_meta === 'string' ? JSON.parse(report.sentiment_meta) : report.sentiment_meta;
                                    const keywords = meta.keywords || [];
                                    if (keywords.length > 0) {
                                        return <span className="text-danger">⚠️ Detected: {keywords.join(", ")}</span>;
                                    }
                                } catch (e) { }
                                return null;
                            })()}
                        </div>
                    )}
                </div>

                <div className="score-group">
                    <ScoreBar label="Location Risk" value={report.location_score} />
                    {report.location_meta && (
                        <div className="meta-explanation text-xs text-muted mt-1 ml-2">
                            {(() => {
                                try {
                                    const meta = typeof report.location_meta === 'string' ? JSON.parse(report.location_meta) : report.location_meta;
                                    const parts = [];
                                    if (meta.schools > 0) parts.push(`🏫 ${meta.schools} School(s) nearby`);
                                    if (meta.hospitals > 0) parts.push(`🏥 ${meta.hospitals} Hospital(s) nearby`);

                                    // Show specific names if available
                                    if (meta.critical_names && meta.critical_names.length > 0) {
                                        parts.push(`📍 Found: ${meta.critical_names.join(", ")}`);
                                    } else if (meta.nearby_critical_count > 0 && parts.length === 0) {
                                        parts.push(`📍 ${meta.nearby_critical_count} Critical spots nearby`);
                                    }
                                    if (meta.is_major_road) parts.push("🛣️ Major Road");

                                    if (parts.length > 0) return <span className="text-warning">{parts.join(" • ")}</span>;
                                    return <span className="text-success">✅ Low risk area</span>;
                                } catch (e) { }
                                return null;
                            })()}
                        </div>
                    )}
                </div>

                <ScoreBar label="Upvote Impact" value={report.upvote_score} />

            </div>
        </Card>
    );
};

export default AIAnalysisCard;
