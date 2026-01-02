from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
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
