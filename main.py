from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import text, Column, String, ForeignKey, TEXT, NUMERIC, DATE, Boolean, TIMESTAMP # Добавляем TIMESTAMP
from datetime import timedelta
from dataclasses import asdict

import schemas, models, auth # Изменяем на абсолютный импорт
from database import SessionLocal, engine, get_db, Base # Импортируем все необходимые объекты
from core_logic import IngestionEngine, BlueOceanEngine, StrategyEngine, CommerceEngine, HarmonyDiagnosticEngine

# Создаем все таблицы в базе данных (при первом запуске)
# В продакшене для этого лучше использовать миграции (Alembic)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="CorePath OS API", version="1.0")

# =============================================================================
# Health Check
# =============================================================================
@app.get("/", response_model=schemas.HealthCheck, tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """
    Проверяет работоспособность API и подключение к базе данных.
    """
    db_status = "OK"
    try:
        db.execute(text('SELECT 1'))
    except Exception as e:
        db_status = f"Error: {e}"
    return schemas.HealthCheck(database_connection=db_status)

# =============================================================================
# API Эндпоинты для Пользователей и Аутентификации
# =============================================================================

@app.post("/api/v1/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Создает нового пользователя (для регистрации).
    """
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, password_hash=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=schemas.Token, tags=["Users"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Эндпоинт для входа. Пользователь отправляет email (в поле username) и пароль.
    Возвращает JWT токен.
    """
    user = auth.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/v1/users/me", response_model=schemas.User, tags=["Users"])
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    """
    Получает информацию о текущем авторизованном пользователе.
    """
    return current_user

# =============================================================================
# API Эндпоинты для Профилей Клиентов
# =============================================================================

@app.get("/api/v1/profiles/", response_model=List[schemas.ClientProfile], tags=["Profiles"])
def get_user_profiles(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """
    Получает все профили, связанные с текущим пользователем.
    Если пользователь - 'client', вернется один профиль.
    Если 'producer' - все профили, где он продюсер.
    """
    if current_user.role == 'client':
        profiles = db.query(models.ClientProfile).filter(models.ClientProfile.user_id == current_user.user_id).all()
    elif current_user.role == 'producer':
        profiles = db.query(models.ClientProfile).filter(models.ClientProfile.producer_id == current_user.user_id).all()
    else:
        profiles = []
    return profiles

@app.post("/api/v1/profiles/", response_model=schemas.ClientProfile, status_code=status.HTTP_201_CREATED, tags=["Profiles"])
def create_profile_from_questionnaire(
    profile_data: schemas.ClientProfileCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Запускает полный конвейер диагностики на сервере и создает ClientProfile.
    """
    # --- ПЕРЕНОС ЛОГИКИ ИЗ app.py НА БЭКЕНД ---
    try:
        # Шаг 1: Поглощение и создание базового профиля
        profile_hub = ingestion_engine.process(profile_data.raw_text)
        if not profile_hub:
            raise HTTPException(status_code=500, detail="AI Ingestion Engine failed to create a profile.")

        # Шаг 2-N: Обогащение профиля другими движками
        profile_hub.positioning_matrix = blue_ocean_engine.process(profile_data.raw_text, profile_hub)
        profile_hub.strategic_goals = strategy_engine.process(profile_hub)
        product_ladder = commerce_engine.process(profile_hub)
        if product_ladder:
            profile_hub.products = [asdict(p) for p in [product_ladder.lead_magnet, product_ladder.tripwire, product_ladder.core_offer, product_ladder.high_ticket] if p]
        profile_hub = harmony_engine.process(profile_hub)
        
        # Преобразование dataclass в dict для сохранения в JSONB
        profile_dict = asdict(profile_hub)
        
        # Создание ORM-модели и сохранение в БД
        db_profile = models.ClientProfile(
            **profile_dict,
            user_id=current_user.user_id
        )
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during profile processing: {e}")

@app.put("/api/v1/profiles/{profile_id}", response_model=schemas.ClientProfile, tags=["Profiles"])
def update_profile(
    profile_id: UUID,
    profile_update: schemas.ClientProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Обновляет существующий профиль клиента.
    Позволяет сохранять изменения, сделанные в конструкторе.
    """
    db_profile = db.query(models.ClientProfile).filter(models.ClientProfile.profile_id == profile_id).first()

    if not db_profile:
        raise HTTPException(status_code=404, detail="Профиль не найден.")

    # Проверка прав: обновлять может только владелец профиля или его продюсер
    if db_profile.user_id != current_user.user_id and db_profile.producer_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Недостаточно прав для обновления этого профиля.")

    # Получаем данные для обновления из Pydantic-схемы
    update_data = profile_update.dict(exclude_unset=True)

    # Обновляем поля модели SQLAlchemy
    for key, value in update_data.items():
        setattr(db_profile, key, value)

    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)

    return db_profile

# =============================================================================
# API Эндпоинты для Задач (Tasks)
# =============================================================================

@app.get("/api/v1/profiles/{profile_id}/tasks", response_model=List[schemas.Task], tags=["Tasks"])
def get_tasks_for_profile(
    profile_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Получает все задачи для указанного профиля."""
    # Здесь также нужна проверка прав, что пользователь имеет доступ к профилю
    tasks = db.query(models.Task).filter(models.Task.profile_id == profile_id).all()
    return tasks

@app.post("/api/v1/profiles/{profile_id}/tasks", response_model=schemas.Task, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
def create_task_for_profile(
    profile_id: UUID,
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Создает новую задачу для профиля."""
    db_task = models.Task(**task.dict(), profile_id=profile_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.put("/api/v1/tasks/{task_id}", response_model=schemas.Task, tags=["Tasks"])
def update_task(
    task_id: UUID,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Обновляет задачу (статус, описание, ответственного и т.д.)."""
    db_task = db.query(models.Task).filter(models.Task.task_id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Задача не найдена.")
    
    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.delete("/api/v1/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Удаляет задачу."""
    db_task = db.query(models.Task).filter(models.Task.task_id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
    return

# =============================================================================
# API Эндпоинты для Мессенджера
# =============================================================================

@app.get("/api/v1/profiles/{profile_id}/channels", response_model=List[schemas.Channel], tags=["Messenger"])
def get_profile_channels(profile_id: UUID, db: Session = Depends(get_db)):
    """
    Получает список всех каналов (чатов), связанных с определенным профилем клиента.
    """
    channels = db.query(models.Channel).filter(models.Channel.profile_id == profile_id).all()
    if not channels:
        raise HTTPException(status_code=404, detail="Для данного профиля каналы не найдены.")
    return channels

@app.get("/api/v1/channels/{channel_id}/messages", response_model=List[schemas.Message], tags=["Messenger"])
def get_channel_messages(channel_id: UUID, db: Session = Depends(get_db), skip: int = 0, limit: int = 100, current_user: models.User = Depends(auth.get_current_user)):
    """
    Поддерживает пагинацию для загрузки истории.
    """
    messages = db.query(models.Message).filter(models.Message.channel_id == channel_id).order_by(models.Message.created_at.desc()).offset(skip).limit(limit).all()
    # Возвращаем в хронологическом порядке для отображения в чате
    return messages[::-1]

@app.post("/api/v1/profiles/{profile_id}/channels", response_model=schemas.Channel, status_code=201, tags=["Messenger"])
def create_channel_for_profile(profile_id: UUID, channel: schemas.ChannelCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """
    Создает новый канал для указанного профиля клиента.
    Автоматически добавляет клиента и продюсера в участники канала.
    """
    db_profile = db.query(models.ClientProfile).filter(models.ClientProfile.profile_id == profile_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Профиль клиента не найден.")

    db_channel = models.Channel(**channel.dict(), profile_id=profile_id)
    db.add(db_channel)
    db.flush() # Используем flush, чтобы получить channel_id для создания участников

    # Автоматически добавляем клиента и продюсера в канал
    members_to_add = []
    if db_profile.user_id:
        members_to_add.append(models.ChannelMember(channel_id=db_channel.channel_id, user_id=db_profile.user_id))
    if db_profile.producer_id:
        # Убедимся, что не добавляем продюсера дважды, если он же и клиент
        if db_profile.producer_id != db_profile.user_id:
            members_to_add.append(models.ChannelMember(channel_id=db_channel.channel_id, user_id=db_profile.producer_id))
    
    db.add_all(members_to_add)
    db.commit()
    db.refresh(db_channel)
    return db_channel

@app.post("/api/v1/channels/{channel_id}/messages", response_model=schemas.Message, status_code=201, tags=["Messenger"])
def create_message_in_channel(channel_id: UUID, message: schemas.MessageCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """
    Создает новое сообщение в указанном канале.
    """
    # Это гораздо безопаснее, чем доверять sender_id из тела запроса
    db_message = models.Message(**message.dict(exclude={"sender_id"}), channel_id=channel_id, sender_id=current_user.user_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

# Проверьте, что все тройные кавычки (""" или ''') в вашем файле main.py закрыты.
# Особенно внимательно посмотрите на строки вокруг 287-290.
    return db_message
