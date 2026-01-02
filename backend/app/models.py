from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, Float, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from .database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(String(20), default="citizen") # Enforced by application logic and DB check constraint
    created_at = Column(DateTime, default=func.now())

    reports = relationship("Report", back_populates="owner")
    upvotes = relationship("Upvote", back_populates="user")

class Report(Base):
    __tablename__ = "reports"

    report_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    category = Column(String(50), nullable=False)
    title = Column(String(200))
    description = Column(Text)
    # image_url removed in favor of ReportImage table
    # SRID 4326 is WGS 84 (standard lat/lon)
    location = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    address = Column(String(255))
    upvote_count = Column(Integer, default=0)
    severity = Column(String(20), default="Medium") # Low, Medium, High
    road_importance = Column(Integer, default=1) # 1=Street, 5=Main Road, 10=Highway
    status = Column(String(30), default="open")
    
    # AI Severity Analysis Fields
    ai_severity_score = Column(Integer)  # 0-100 score from AI analysis
    ai_severity_category = Column(String(20))  # Clean/Low/Medium/High/Extreme
    ai_object_count = Column(Integer)  # Number of garbage objects detected
    ai_coverage_area = Column(Float)  # Garbage coverage ratio (0-1)
    ai_scene_dirtiness = Column(Float)  # Scene dirtiness score (0-1)
    ai_confidence_explanation = Column(Text)  # Human-readable explanation
    
    # Location Context Fields
    location_context = Column(JSONB)  # Nearby sensitive locations
    location_priority_multiplier = Column(Float, default=1.0)  # 0.9-1.5x
    
    # Text Sentiment Analysis Fields
    text_sentiment_score = Column(Float)  # 0-1 sentiment score
    text_urgency_keywords = Column(Text)  # Comma-separated keywords
    text_emotion_category = Column(String(50))  # angry/concerned/neutral
    
    # Waste Type Classification Fields
    waste_primary_type = Column(String(50))  # hazardous/wet/dry/recyclable/e_waste/other
    waste_composition = Column(JSONB)  # Percentage breakdown of waste types
    is_hazardous_waste = Column(Boolean, default=False)  # Hazardous waste flag
    waste_disposal_recommendations = Column(Text)  # Disposal recommendations
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="reports")
    upvotes = relationship("Upvote", back_populates="report")
    images = relationship("ReportImage", back_populates="report", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="report", cascade="all, delete-orphan")
    history = relationship("ReportHistory", back_populates="report", cascade="all, delete-orphan")

class ReportImage(Base):
    __tablename__ = "report_images"

    image_id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.report_id", ondelete="CASCADE"))
    file_path = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime, default=func.now())

    report = relationship("Report", back_populates="images")

class Upvote(Base):
    __tablename__ = "upvotes"

    report_id = Column(Integer, ForeignKey("reports.report_id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    upvoted_at = Column(DateTime, default=func.now())

    report = relationship("Report", back_populates="upvotes")
    user = relationship("User", back_populates="upvotes")

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.report_id", ondelete="CASCADE"))
    staff_name = Column(String(100))
    staff_phone = Column(String(20))
    assigned_by = Column(Integer, ForeignKey("users.user_id"))
    assigned_at = Column(DateTime, default=func.now())
    expected_resolution_date = Column(DateTime, nullable=True)
    status = Column(String(50), default="assigned")

    report = relationship("Report", back_populates="assignments")
    assigner = relationship("User")

class ReportHistory(Base):
    __tablename__ = "report_history"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.report_id", ondelete="CASCADE"))
    old_status = Column(String(50))
    new_status = Column(String(50))
    note = Column(Text)
    changed_by = Column(Integer, ForeignKey("users.user_id"))
    changed_at = Column(DateTime, default=func.now())

    report = relationship("Report", back_populates="history")
    changer = relationship("User")
