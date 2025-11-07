-- =============================================================================
-- CorePath OS - Database Schema v1.0
-- =============================================================================
-- Этот файл описывает структуру базы данных для SaaS-платформы CorePath OS.
-- Он основан на дата-классах из core_logic.py.
-- =============================================================================

-- Расширение для использования UUID в качестве первичных ключей
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- Таблица 1: Пользователи (Users)
-- Хранит информацию о всех пользователях системы (Продюсеры и Клиенты).
-- =============================================================================
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('producer', 'client')), -- 'producer' (Admin) или 'client' (User)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- Таблица 2: Профили Клиентов (Client Profiles)
-- Основная таблица, хранящая всю информацию из ClientProfileHub.
-- =============================================================================
CREATE TABLE client_profiles (
    profile_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE, -- Связь с пользователем-клиентом
    producer_id UUID REFERENCES users(user_id) ON DELETE SET NULL, -- Связь с пользователем-продюсером
    brand_name VARCHAR(255),
    -- Для полей-списков и словарей используется JSONB для гибкости
    niche JSONB,
    superpower TEXT,
    strategic_goals_list JSONB,
    gz JSONB,
    emotion_matrix JSONB,
    verbal_code JSONB,
    competencies JSONB,
    visual_identity JSONB,
    peak_emotions JSONB,
    superpower_application JSONB,
    social_capital JSONB,
    formal_regalia JSONB,
    reputational_risks JSONB,
    strategic_goals JSONB,
    audience_groups JSONB,
    positioning_matrix JSONB,
    values JSONB,
    enemies JSONB,
    harmony_report JSONB,
    show_pitch JSONB,
    formats JSONB,
    content_plan JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- Таблица 3: Задачи (Tasks)
-- Реализация CorePath PM. Связана с конкретным профилем клиента.
-- =============================================================================
CREATE TABLE tasks (
    task_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES client_profiles(profile_id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'To Do' CHECK (status IN ('To Do', 'In Progress', 'Done', 'On Approval')),
    responsible_id UUID REFERENCES users(user_id) ON DELETE SET NULL, -- Ответственный может быть любым пользователем
    priority VARCHAR(50) DEFAULT 'Средний',
    deadline DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- Таблица 4: Продукты (Products)
-- Хранит все продукты из "Библиотеки Продуктов".
-- =============================================================================
CREATE TABLE products (
    product_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES client_profiles(profile_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    price NUMERIC(10, 2) DEFAULT 0.00,
    purpose TEXT,
    description TEXT,
    target_audience TEXT,
    usp TEXT,
    -- Статус для Канбан-доски "Библиотеки Продуктов"
    status VARCHAR(50) DEFAULT 'Idea' CHECK (status IN ('Idea', 'In Development', 'Active', 'Archived')),
    -- Тип продукта для "Лестницы Ценности"
    pvl_tier VARCHAR(50) CHECK (pvl_tier IN ('lead_magnet', 'tripwire', 'core_offer', 'high_ticket')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- Таблица 5: Активы Влияния (Influence Assets)
-- =============================================================================
CREATE TABLE influence_assets (
    asset_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES client_profiles(profile_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    asset_type VARCHAR(100), -- "Отзыв", "Кейс", "Упоминание в СМИ"
    description TEXT,
    -- image_url будет хранить ссылку на файл в облачном хранилище (напр., S3)
    image_url VARCHAR(1024),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- Таблица 9: Члены Команды (Team Members)
-- Реализация CorePath Team (RMS).
-- =============================================================================
CREATE TABLE team_members (
    member_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES client_profiles(profile_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL,
    tags JSONB, -- Для тегов типа #монтажер_reels
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- Таблица 6: Каналы Мессенджера (Channels)
-- Хранит чаты, привязанные к проекту клиента.
-- =============================================================================
CREATE TABLE channels (
    channel_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES client_profiles(profile_id) ON DELETE CASCADE,
    channel_name VARCHAR(255) NOT NULL,
    channel_type VARCHAR(50) NOT NULL CHECK (channel_type IN ('group', 'direct')) DEFAULT 'group',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- Таблица 7: Участники Каналов (Channel Members)
-- Промежуточная таблица для связи пользователей и каналов (многие-ко-многим).
-- =============================================================================
CREATE TABLE channel_members (
    channel_id UUID NOT NULL REFERENCES channels(channel_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    -- Составной первичный ключ гарантирует уникальность пары (канал, пользователь)
    PRIMARY KEY (channel_id, user_id)
);

-- =============================================================================
-- Таблица 8: Сообщения (Messages)
-- Хранит все сообщения в рамках каналов.
-- =================================================_============================
CREATE TABLE messages (
    message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    channel_id UUID NOT NULL REFERENCES channels(channel_id) ON DELETE CASCADE,
    sender_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text' CHECK (message_type IN ('text', 'image', 'file', 'system')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);
