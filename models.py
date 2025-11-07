from sqlalchemy import Column, String, ForeignKey, TEXT, NUMERIC, DATE, Boolean, TIMESTAMP # Изменяем TIMESTAMPTZ на TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from database import Base # Изменяем на абсолютный импорт

# =============================================================================
# Модель 1: Пользователи (Users)
# =============================================================================
class User(Base):
    __tablename__ = "users"
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False) # 'producer', 'client'
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Отношения
    client_profiles = relationship("ClientProfile", foreign_keys="[ClientProfile.user_id]", back_populates="user")
    produced_profiles = relationship("ClientProfile", foreign_keys="[ClientProfile.producer_id]", back_populates="producer")
    sent_messages = relationship("Message", back_populates="sender")
    channel_associations = relationship("ChannelMember", back_populates="user")

# =============================================================================
# Модель 2: Профили Клиентов (Client Profiles)
# =============================================================================
class ClientProfile(Base):
    __tablename__ = "client_profiles"
    profile_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'))
    producer_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='SET NULL'))
    brand_name = Column(String(255))
    
    # Все гибкие поля храним в JSONB
    niche = Column(JSONB)
    superpower = Column(TEXT)
    # ... и так далее для всех полей из ClientProfileHub
    strategic_goals_list = Column(JSONB)
    gz = Column(JSONB)
    emotion_matrix = Column(JSONB)
    verbal_code = Column(JSONB)
    competencies = Column(JSONB)
    visual_identity = Column(JSONB)
    # ...

    # Отношения
    user = relationship("User", foreign_keys=[user_id], back_populates="client_profiles")
    producer = relationship("User", foreign_keys=[producer_id], back_populates="produced_profiles")
    tasks = relationship("Task", back_populates="profile")
    products = relationship("Product", back_populates="profile")
    channels = relationship("Channel", back_populates="profile")
    team = relationship("TeamMember", back_populates="profile", cascade="all, delete-orphan")
    influence_assets = relationship("InfluenceAsset", back_populates="profile", cascade="all, delete-orphan")

# =============================================================================
# Модель 3: Задачи (Tasks)
# =============================================================================
class Task(Base):
    __tablename__ = "tasks"
    task_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('client_profiles.profile_id', ondelete='CASCADE'), nullable=False)
    description = Column(TEXT, nullable=False)
    status = Column(String(50), default='To Do') # 'To Do', 'In Progress', 'Done'
    responsible_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    priority = Column(String(50), default='Средний')
    deadline = Column(DATE, nullable=True)

    
    # Отношения
    profile = relationship("ClientProfile", back_populates="tasks")
    responsible = relationship("User") # Связь для получения информации об ответственном

# =============================================================================
# Модель 4: Продукты (Products)
# =============================================================================
class Product(Base):
    __tablename__ = "products"
    product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('client_profiles.profile_id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    price = Column(NUMERIC(10, 2), default=0.00)
    purpose = Column(TEXT)
    description = Column(TEXT)
    target_audience = Column(TEXT)
    usp = Column(TEXT)
    status = Column(String(50), default='Idea') # 'Idea', 'In Development', 'Active', 'Archived'
    pvl_tier = Column(String(50)) # 'lead_magnet', 'tripwire', 'core_offer', 'high_ticket'

    # Отношения
    profile = relationship("ClientProfile", back_populates="products")

# =============================================================================
# Модель 5: Члены Команды (Team Members)
# =============================================================================
class TeamMember(Base):
    __tablename__ = "team_members"
    member_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('client_profiles.profile_id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    tags = Column(JSONB)

    # Отношения
    profile = relationship("ClientProfile", back_populates="team")

# =============================================================================
# Модель 6: Активы Влияния (Influence Assets)
# =============================================================================
class InfluenceAsset(Base):
    __tablename__ = "influence_assets"
    asset_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('client_profiles.profile_id', ondelete='CASCADE'), nullable=False)
    title = Column(String(255), nullable=False)
    asset_type = Column(String(100))
    description = Column(TEXT)
    image_url = Column(String(1024))

    # Отношения
    profile = relationship("ClientProfile", back_populates="influence_assets")

# =============================================================================
# Модели для Мессенджера (Шаг 2)
# =============================================================================
class Channel(Base):
    __tablename__ = "channels"
    channel_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('client_profiles.profile_id', ondelete='CASCADE'), nullable=False)
    channel_name = Column(String(255), nullable=False)
    channel_type = Column(String(50), nullable=False, default='group')
    
    profile = relationship("ClientProfile", back_populates="channels")
    messages = relationship("Message", back_populates="channel", cascade="all, delete-orphan")
    members = relationship("ChannelMember", back_populates="channel")

class ChannelMember(Base):
    __tablename__ = "channel_members"
    channel_id = Column(UUID(as_uuid=True), ForeignKey('channels.channel_id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    
    user = relationship("User", back_populates="channel_associations")
    channel = relationship("Channel", back_populates="members")

class Message(Base):
    __tablename__ = "messages"
    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    channel_id = Column(UUID(as_uuid=True), ForeignKey('channels.channel_id', ondelete='CASCADE'), nullable=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    content = Column(TEXT, nullable=False)
    message_type = Column(String(50), default='text')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now()) # Используем TIMESTAMP(timezone=True)

    channel = relationship("Channel", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages")
