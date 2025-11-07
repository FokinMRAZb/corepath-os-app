from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from uuid import UUID
import datetime

# Базовая схема для пользователя
class UserBase(BaseModel):
    email: EmailStr

# Схема для создания пользователя
class UserCreate(UserBase):
    password: str
    role: str = 'client'

# Схема для чтения данных пользователя (без пароля)
class User(UserBase):
    user_id: UUID
    role: str
    created_at: datetime.datetime

    class Config:
        orm_mode = True # Позволяет Pydantic работать с объектами SQLAlchemy

# Простая схема для демонстрации
class HealthCheck(BaseModel):
    status: str = "OK"
    database_connection: str

# =============================================================================
# Схемы для Аутентификации
# =============================================================================
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
# =============================================================================
# Схемы для Мессенджера
# =============================================================================

class MessageBase(BaseModel):
    content: str
    message_type: str = 'text'
    # В реальном приложении sender_id будет браться из токена аутентификации
    sender_id: UUID

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    message_id: UUID
    channel_id: UUID
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class ChannelBase(BaseModel):
    channel_name: str

class ChannelCreate(ChannelBase):
    pass

class Channel(ChannelBase):
    channel_id: UUID
    profile_id: UUID

    class Config:
        orm_mode = True

# =============================================================================
# Схемы для Профиля Клиента
# =============================================================================

class ClientProfileBase(BaseModel):
    brand_name: Optional[str] = None
    niche: Optional[List[str]] = []
    superpower: Optional[str] = None
    # Мы используем dict для гибкости JSONB полей
    strategic_goals_list: Optional[dict] = {}
    gz: Optional[List[dict]] = []
    emotion_matrix: Optional[List[dict]] = []
    verbal_code: Optional[dict] = {}
    competencies: Optional[dict] = {}
    visual_identity: Optional[dict] = {}
    # ... и так далее для всех полей

class ClientProfileCreate(BaseModel):
    # Схема для создания профиля. Принимает только сырой текст.
    raw_text: str

class ClientProfileUpdate(ClientProfileBase):
    # Эта схема используется для PUT/PATCH запросов.
    # Она позволяет обновлять любые поля, определенные в ClientProfileBase.
    pass

class ClientProfile(ClientProfileBase):
    profile_id: UUID
    user_id: UUID
    producer_id: Optional[UUID] = None

    class Config:
        orm_mode = True

# =============================================================================
# Схемы для Задач (Tasks)
# =============================================================================

class TaskBase(BaseModel):
    description: str
    status: Optional[str] = "To Do"
    responsible_id: Optional[UUID] = None
    priority: Optional[str] = "Средний"
    deadline: Optional[datetime.date] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[str] = None
    responsible_id: Optional[UUID] = None
    priority: Optional[str] = None
    deadline: Optional[datetime.date] = None

class Task(TaskBase):
    task_id: UUID
    profile_id: UUID

    class Config:
        orm_mode = True

# =============================================================================
# Схемы для Декомпозиции Сценария
# =============================================================================

class ScenarioDecompositionRequest(BaseModel):
    # Схема для запроса на декомпозицию сценария в задачи
    script: dict # Сгенерированный сценарий {"title": ..., "hook": ...}
    anchor_points: dict # 8 опорных точек, использованных для генерации

# =============================================================================
# Схемы для Продуктов (Products)
# =============================================================================

class ProductBase(BaseModel):
    name: str
    price: Optional[float] = 0.0
    purpose: Optional[str] = None
    description: Optional[str] = None
    target_audience: Optional[str] = None
    usp: Optional[str] = None
    status: Optional[str] = 'Idea'
    pvl_tier: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    purpose: Optional[str] = None
    description: Optional[str] = None
    target_audience: Optional[str] = None
    usp: Optional[str] = None
    status: Optional[str] = None

class Product(ProductBase):
    product_id: UUID
    profile_id: UUID

    class Config:
        orm_mode = True

# =============================================================================
# Схемы для Команды (Team)
# =============================================================================

class TeamMemberBase(BaseModel):
    name: str
    role: str
    tags: Optional[List[str]] = []

class TeamMemberCreate(TeamMemberBase):
    pass

class TeamMember(TeamMemberBase):
    member_id: UUID
    profile_id: UUID

    class Config:
        orm_mode = True

# =============================================================================
# Схемы для Активов Влияния (Influence Assets)
# =============================================================================

class InfluenceAssetBase(BaseModel):
    title: str
    asset_type: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class InfluenceAssetCreate(InfluenceAssetBase):
    pass

class InfluenceAsset(InfluenceAssetBase):
    asset_id: UUID
    profile_id: UUID

    class Config:
        orm_mode = True
