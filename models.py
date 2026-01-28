"""
SQLAlchemy models for PostgreSQL.
Based on the production schema from docs/schema.rb
"""
from sqlalchemy import Column, String, Boolean, DateTime, Date, Integer, Float, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    """User model - matches the 'users' table from schema.rb"""
    __tablename__ = "users"

    # Primary key - UUID as in production
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Core identity
    email = Column(String(255), unique=True, nullable=False, index=True)
    encrypted_password = Column(String, nullable=False, default="")
    name = Column(String)
    last_name = Column(String)
    country = Column(String)
    region = Column(String)
    city = Column(String)
    locale = Column(String(255), nullable=False, default="en")
    
    # Athlete Profile fields
    has_athlete_profile = Column(Boolean, default=False)
    birthdate = Column(Date)
    gender = Column(String)
    bio = Column(Text)
    preferred_discipline = Column(String)  # e.g., 'bike', 'running', 'hiking'
    planning_modality = Column(String)
    planning_date = Column(Date)
    
    # Strava integration
    strava_profile = Column(String)
    strava_refresh_token = Column(String)
    strava_refresh_token_expires_at = Column(DateTime)
    # Additional strava fields for our app
    strava_id = Column(String, index=True)
    strava_access_token = Column(String)
    strava_expires_at = Column(Integer)
    
    # Social profiles
    instagram_profile = Column(String)
    
    # Notification settings
    notify_status_changes = Column(Boolean, default=True, nullable=False)
    notify_user_located = Column(Boolean, default=True, nullable=False)
    allow_mailing = Column(Boolean, default=False, nullable=False)
    
    # Auth tokens (for device_token_auth style)
    provider = Column(String, default="email", nullable=False)
    uid = Column(String, default="", nullable=False)
    
    # Membership
    membership = Column(Integer, default=0, nullable=False)
    stripe_id = Column(String, unique=True)
    
    # Soft delete
    deleted_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    everesting_id = Column(String, unique=True)
    total_elevation = Column(Float, default=0)
    is_active = Column(Boolean, default=True)

class Activity(Base):
    """Activity model - matches the 'activities' table from schema.rb"""
    __tablename__ = "activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    status = Column(String, nullable=False, default="Accepted")
    format = Column(String, nullable=False, default="Strava Sync")
    discipline = Column(String, nullable=False)  # e.g., 'Everesting'
    modality = Column(String, nullable=False)    # e.g., 'Full', '10K'
    date = Column(Date, nullable=False)
    
    elevation = Column(Float, nullable=False)
    distance = Column(Float, nullable=False)
    elapsed_time = Column(Float, nullable=False)
    
    # Integration fields
    strava_id = Column(String, unique=True, index=True)
    strava_url = Column(Text) # Storing as single URL string for simplicity in MVP
    
    climb_name = Column(String)
    location = Column(String)
    country = Column(String)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class Challenge(Base):
    """Challenge model"""
    __tablename__ = "challenges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    foto = Column(String)
    description = Column(Text)
    rules = Column(Text)
    elevation = Column(Float)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    modalidad = Column(ARRAY(String))
    labels = Column(ARRAY(String))


class Collection(Base):
    """Collection model"""
    __tablename__ = "collections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    channel_ids = Column(ARRAY(String))


class UserChallenge(Base):
    """UserChallenge model - matches the 'user_challenges' table"""
    __tablename__ = "user_challenges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    challenge_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    status = Column(String, nullable=False, default="Active")
    accepted_rules = Column(Boolean, default=True, nullable=False)
    progress = Column(Float, default=0.0, nullable=False)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
