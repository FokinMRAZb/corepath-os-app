from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
import google.generativeai as genai
import json
from datetime import date
from tenacity import retry, stop_after_attempt, wait_exponential

# ==============================================================================
# --- БЛОК 1: ОПРЕДЕЛЕНИЕ СТРУКТУР ДАННЫХ ---
# ==============================================================================

@dataclass
class ClientProfileHub:
    """
    Класс данных, представляющий "Единый Источник Правды" (Client_Profile_Hub)
    согласно Техническому Заданию v8.1.
    """
    client_id: UUID = field(default_factory=uuid4)
    brand_name: Optional[str] = None
    niche: List[str] = field(default_factory=list)
    superpower: Optional[str] = None
    strategic_goals_list: Dict[str, Any] = field(default_factory=dict)
    gz: List[Dict[str, Any]] = field(default_factory=list)
    # --- НОВЫЕ ПОЛЯ ДЛЯ АРХИТЕКТУРЫ «ОБРАЗА» ---
    emotion_matrix: List[Dict[str, str]] = field(default_factory=list)
    verbal_code: Dict[str, Any] = field(default_factory=dict)
    competencies: Dict[str, List[str]] = field(default_factory=dict)
    visual_identity: Dict[str, Any] = field(default_factory=dict)
    peak_emotions: List[str] = field(default_factory=list)
    superpower_application: List[Dict[str, str]] = field(default_factory=list)
    social_capital: List[str] = field(default_factory=list)
    formal_regalia: List[str] = field(default_factory=list)
    reputational_risks: List[Dict[str, Any]] = field(default_factory=list)
    strategic_goals: Dict[str, Any] = field(default_factory=dict)
    audience_groups: Dict[str, Any] = field(default_factory=dict)
    positioning_matrix: Dict[str, Any] = field(default_factory=dict)
    positioning_synth: Optional[str] = None
    values: List[str] = field(default_factory=list)
    enemies: List[str] = field(default_factory=list)
    style_voice: Dict[str, Any] = field(default_factory=dict)
    products: List[Dict[str, Any]] = field(default_factory=list)
    harmony_report: Optional[Dict[str, Any]] = None
    show_pitch: Optional[Dict[str, Any]] = None
    formats: List[Dict[str, Any]] = field(default_factory=list)
    content_plan: List[Dict[str, Any]] = field(default_factory=list)
    regalia_ref: Optional[UUID] = None
    influence_capital: List['InfluenceAsset'] = field(default_factory=list)
    team: List['TeamMember'] = field(default_factory=list)

@dataclass
class InfluenceAsset:
    """
    Представляет один актив в "Капитале Влияния" (Фаза I).
    """
    title: str
    asset_type: str  # "Отзыв", "Кейс", "Упоминание в СМИ", "Выступление"
    description: str
    image_bytes: Optional[bytes] = None
    asset_id: UUID = field(default_factory=uuid4)

@dataclass
class TeamMember:
    """
    Представляет одного члена команды.
    """
    name: str
    role: str
    member_id: UUID = field(default_factory=uuid4)

@dataclass
class Comment:
    """
    Представляет один комментарий к задаче.
    """
    author: str
    text: str
    comment_id: UUID = field(default_factory=uuid4)

@dataclass
class Attachment:
    """
    Представляет один прикрепленный файл к задаче.
    """
    file_name: str
    file_data: bytes
    attachment_id: UUID = field(default_factory=uuid4)

@dataclass
class Product:
    """
    Представляет один продукт в продуктовой линейке клиента.
    """
    name: str
    price: float
    purpose: str
    description: Optional[str] = "" # Для вкладки "Суть"
    target_audience: Optional[str] = "" # Для вкладки "ЦА"
    usp: Optional[str] = "" # Для вкладки "УТП"

@dataclass
class ProductValueLadder:
    """
    Представляет "Лестницу Ценности Продукта" (PVL) из ТЗ 5.3.1.
    """
    lead_magnet: Optional[Product] = None
    tripwire: Optional[Product] = None
    core_offer: Optional[Product] = None
    high_ticket: Optional[Product] = None

@dataclass
class Task:
    """
    Представляет одну задачу в календаре проекта.
    """
    description: str
    status: str = "To Do"
    responsible: Optional[str] = ""
    priority: str = "Средний"  # Низкий, Средний, Высокий
    deadline: Optional[date] = None
    comments: List[Comment] = field(default_factory=list)
    attachments: List[Attachment] = field(default_factory=list)

@dataclass
class Channel:
    """
    Представляет один канал/чат в мессенджере
    """
    profile_id: UUID
    channel_name: str
    channel_id: UUID = field(default_factory=uuid4)
    channel_type: str = "group" # 'group' or 'direct'
    members: List[UUID] = field(default_factory=list)

@dataclass
class Message:
    """
    Представляет одно сообщение в канале
    """
    channel_id: UUID
    sender_id: UUID
    content: str
    message_id: UUID = field(default_factory=uuid4)
    message_type: str = "text"

# ==============================================================================
# --- БЛОК 1.5: ДАННЫЕ ДЛЯ КОНСТРУКТОРА "8 ОПОРНЫХ ТОЧЕК" ---
# ==============================================================================

ANCHOR_POINTS_DATA = {
    "content_carriers": [
        "Пост с фото", "Горизонтальное длинное видео", "Сторитейлинг", 
        "Прямой эфир", "Шортс", "Публичное выступление", "Статья", 
        "Аудио-пост", "Подкаст"
    ],
    "formats": [
        "Экспертный", "Развлекательный", "Продающий", "Личный", "Мотивационный"
    ],
    "blog_genres": [
        "Обзор", "Распаковка", "Сравнение", "Топы / Рейтинги", "Аналитика / Разбор",
        "Критика / Хейтинг", "Скетч / Сценка", "Пранк", "Челлендж / Вызов",
        "Реакция", "Летсплей / Прохождение", "Интервью", "Гайд / Туториал",
        "DIY (Сделай сам)", "Научпоп / Объяснение", "Вопрос-ответ (Q&A)",
        "Влог", "Мой день / Рутина", "Тревел-видео", "Бэкстейдж / Закулисье",
        "Сторителлинг / История из жизни", "Мнение / Монолог"
    ],
    "extras_triggers": [
        "Конкурс/Розыгрыш", "Тест/Викторина", "Загадка/Головоломка", "Опрос/Голосование",
        "Мемы", "Вредные советы", "Кейс/Пример", "Разбор ошибок", "Данные исследований",
        "История из жизни", "Бекстейдж/Закулисье", "До и после", "Флешбек/Ностальгия",
        "Откровение/Признание", "Скрины переписки", "Провокация", "Шок-контент",
        "Милота", "Эстетика", "Ответ на хейт", "Саспенс/Напряжение", "ASMR/Satisfying",
        "Соц. док-во", "Авторитет", "Дедлайн", "Дефицит", "Интрига", "Тизеры"
    ],
    "movie_genres": [
        "Комедия", "Боевик", "Приключения", "Фантастика", "Драма / Мелодрама",
        "Триллер / Психологический", "Хоррор / Ужасы", "Фэнтези", "Детектив",
        "Документальный фильм", "Фильм-катастрофа", "Мюзикл", "Сказка"
    ],
    "tv_genres": [
        "Ток-шоу", "Реалити-шоу", "Игровое шоу", "Шоу талантов",
        "Шоу о преображении", "Дебаты", "Аналитическая программа", "Репортаж",
        "Вечернее шоу", "Сериал", "Ситком"
    ]
}

# ==============================================================================
# --- БЛОК 2: ОПРЕДЕЛЕНИЕ ДВИЖКОВ СИСТЕМЫ (с мок-данными) ---
# ==============================================================================

class IngestionEngine:
    """Реализует "Движок Поглощения" (Шаг 1, Фаза F)."""
    def __init__(self, api_key: Optional[str] = None, offline_mode: bool = False):
        self.api_key = api_key
        self.offline_mode = offline_mode
        if api_key:
            genai.configure(api_key=api_key)
            
    def _get_mock_profile(self) -> ClientProfileHub:
        print("⚠️ API-ключ не предоставлен. Возвращается симулированный профиль.")
        # --- Расширенные моковые данные для демонстрации ---
        mock_verbal_code = {
            "anchor_phrases": "Работаем, Это база, Думай, Какой хороший вопрос",
            "communication_style": "Авторитетный",
            "profanity_use": "В Исключениях",
            "forbidden_words": "короче, как бы, в принципе",
            "professional_jargon": "MVP: Minimum Viable Product - минимально жизнеспособный продукт.\nFOKIN: Foundation, Orchestration, Kinetic, Influence, Nexus - методология.",
            "accent_words": "База, Система, Нексус",
            "favorite_quotes": "Только тот, кто готов рискнуть...",
            "synonym_words": "хорошо: великолепно, мощно, эффективно"
        }
        
        mock_visual_identity = {
            'base_palette': "Черный, Серый, Темно-синий",
            'accent_palette': "Красный",
            'visual_anchors': "Очки определенной оправы\nЧасы (Скрытый Премиум)",
            'clothing_style': "Tech Minimalist",
            'look_collection': [
                {"Название «Лука»": "ЭКСПЕРТ", "Позиционирование / Задача": "Трансляция авторитета, власти", "Ключевые Элементы": "Темно-синий блейзер, качественная футболка", "Акцент / Аксессуар": "Часы", "Когда Использовать": "Вебинары, B2B-переговоры"},
                {"Название «Лука»": "ПРОВОКАТОР", "Позиционирование / Задача": "Трансляция энергии, 'пиковых эмоций'", "Ключевые Элементы": "Черная водолазка, кожаная куртка", "Акцент / Аксессуар": "Красный браслет", "Когда Использовать": "Конфликтный контент, шоу"},
                {"Название «Лука»": "СВОЙ ПАРЕНЬ", "Позиционирование / Задача": "Трансляция эмпатии, аутентичности", "Ключевые Элементы": "Серая футболка, худи, джинсы", "Акцент / Аксессуар": "Отсутствие ярких акцентов", "Когда Использовать": "Лайфстайл-контент, сторис"},
                {"Название «Лука»": "НАСТАВНИК", "Позиционирование / Задача": "Сочетание авторитета и эмпатии", "Ключевые Элементы": "Качественный свитер, светлая рубашка", "Акцент / Аксессуар": "Очки, блокнот", "Когда Использовать": "Обучающие лекции, разбор кейсов"},
            ]
        } # type: ignore

        mock_competencies = {
            "superpowers": ["Системное мышление", "Стратегический анализ", "Создание методологий", "Дар убеждать"],
            "growth_zones": ["Делегирование", "Публичные выступления", "Монтаж видео"]
        }

        mock_superpower_application = [
            {"Инструмент / Суперсила": "Системное мышление", "Связанная Цель": "Автоматизировать онбординг", "Механизм Помощи": "Проектирование архитектуры приложения"},
            {"Инструмент / Суперсила": "Дар убеждать", "Связанная Цель": "Привлечь инвесторов", "Механизм Помощи": "Питчинг, переговоры"},
        ]

        mock_reputational_risks = [
            {"Риск": "Были ли у вас публичные конфликты?", "Есть": True, "Описание/Контр-аргумент": "Конфликт с блогером N. Позиция: отстаивал качество против хайпа. Аргументы готовы."},
            {"Риск": "Существуют ли «неудобные» фото или видео из прошлого?", "Есть": False, "Описание/Контр-аргумент": ""},
            {"Риск": "Были ли у вас проблемы с законом или финансовые споры?", "Есть": False, "Описание/Контр-аргумент": ""},
            {"Риск": "Высказывали ли вы ранее мнения, противоречащие образу?", "Есть": False, "Описание/Контр-аргумент": ""},
            {"Риск": "Есть ли люди, которые могут иметь на вас «зуб»?", "Есть": False, "Описание/Контр-аргумент": ""},
        ]

        mock_influence_capital = [
            InfluenceAsset(title="Кейс 'Запуск CorePath OS'", asset_type="Кейс", description="Успешный запуск SaaS-платформы с выходом на 1000+ пользователей за 3 месяца."),
            InfluenceAsset(title="Отзыв от клиента 'Альфа'", asset_type="Отзыв", description="'Работа с Валентином полностью изменила наш подход к маркетингу...'"),
            InfluenceAsset(title="Упоминание в Forbes", asset_type="Упоминание в СМИ", description="Статья о методологии F.O.K.I.N. в разделе 'Технологии'.")
        ]

        mock_team = [
            TeamMember(name="Иван Петров", role="Монтажер"),
            TeamMember(name="Елена Сидорова", role="Сценарист"),
            TeamMember(name="Дмитрий Козлов", role="Оператор"),
        ]

        profile = ClientProfileHub(
            brand_name="Валентин Фокин (Мок)",
            niche=["Стратегический консалтинг", "Продюсирование экспертов"],
            superpower="Создание авторских методологий и превращение их в технологические продукты.",
            gz=[{"goal": "Запустить 5 пилотных проектов", "stress_reduction": 0.8}, {"goal": "Автоматизировать онбординг", "stress_reduction": 0.6}],
            values=["Системность", "Инновации", "Честность", "Масштабирование"],
            enemies=["Поверхностный подход", "Инфоцыганство", "Выгорание от рутины"],
            style_voice={"tone_of_voice": "Провокационный / Наставнический"}, # Это поле заполняется из verbal_code
            # --- РАСШИРЕННЫЕ ДЕМО-ДАННЫЕ ---
            emotion_matrix=[
                {"Эмоция": "Гнев (Anger)", "Триггер": "Некомпетентность", "Внутреннее Ощущение": "Прилив энергии", "Внешнее Проявление": "Прямая критика", "Якорная Фраза": "Это просто жесть"}
            ],
            peak_emotions=["Гнев (Anger)"], # Заполняется из emotion_matrix
            verbal_code=mock_verbal_code,
            competencies=mock_competencies,
            visual_identity=mock_visual_identity,
            superpower_application=mock_superpower_application,
            formal_regalia=["Высшее образование (МГУ)", "Спикер конференции 'Digital-2024'"],
            social_capital=["Работал с 'Технопарк Сколково'", "Упоминание в Forbes"],
            reputational_risks=mock_reputational_risks,
            influence_capital=mock_influence_capital,
            team=mock_team,
            strategic_goals_list={
                "main_goal": "2 варианта: 1) 5 клиентов на 'Продюсирование' (по 250к/мес). 2) 'стабильный 20 000$ в месяц' с 'Приложения-сценариста'",
                "business_goals": "Текущий доход: 350-400к/мес. Цель на 1 год: 2.5 млн/мес",
                "media_goals": "Приглашения как эксперта, узнаваемость на улице",
                "mission": "Изменить 'образовательную систему', дав детям 'возможность безопасно пробовать нечто новое'"
            }
        )
        return profile

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
    def _call_llm_for_extraction(self, raw_text: str) -> Optional[ClientProfileHub]:
        if self.offline_mode or not self.api_key:
            return self._get_mock_profile() # Используем мок-данные, если нет API-ключа

        print("\n🤖 [Real AI] Извлечение профиля через Gemini API...")
        prompt = f"""
        You are a strategic consultant. Your task is to analyze the provided text from a client's questionnaire and extract key information.
        The output MUST be a valid JSON object with the following structure:
        {{
          "brand_name": "string",
          "niche": ["string", ...],
          "superpower": "string",
          "gz": [{{"goal": "string", "stress_reduction": "float from 0.0 to 1.0"}}, ...],
          "values": ["string", ...],
          "enemies": ["string", ...],
          "style_voice": {{
            "tone_of_voice": "string",
            "anchor_phrases": ["string", ...],
            "forbidden_words": ["string", ...]
          }}
        }}
        Do not add any text or explanations before or after the JSON object.

        ---
        Questionnaire Text:
        "{raw_text}"
        ---
        """
        try:
            safety_settings = {
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_ONLY_HIGH',
            }
            model = genai.GenerativeModel('gemini-pro-latest')
            response = model.generate_content(
                prompt,
                safety_settings=safety_settings)
            # Удаляем "```json" и "```" из ответа Gemini
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            extracted_data = json.loads(cleaned_response)
            return ClientProfileHub(**extracted_data)
        except Exception as e:
            print(f"❌ Ошибка при извлечении профиля через API: {e}")
            raise e # Пробрасываем ошибку наверх для отображения в UI

    def process(self, raw_text: str) -> Optional[ClientProfileHub]:
        print("🚀 Запуск Движка Поглощения...")
        profile = self._call_llm_for_extraction(raw_text)
        if profile:
            print("✅ Профиль успешно создан и заполнен!")
        return profile

class BlueOceanEngine:
    """Реализует "Движок Голубого Океана" (Шаг 3, Фаза O)."""
    def __init__(self, api_key: Optional[str] = None, offline_mode: bool = False):
        self.api_key = api_key
        self.offline_mode = offline_mode
        if api_key:
            genai.configure(api_key=api_key)
            
    def _get_mock_matrix(self) -> Dict[str, List[str]]:
        print("⚠️ API-ключ не предоставлен. Возвращается симулированная Матрица 4-х Действий.")
        return {
            "eliminate": ["Ручная 'распаковка' экспертов", "Создание контента без стратегии"],
            "reduce": ["Время на онбординг клиента", "Зависимость от 'вдохновения'"],
            "raise": ["Глубина стратегической проработки", "Контекстуальная релевантность контента"],
            "create": ["Автоматизированный 'Стратегический МРТ-сканер'", "Единый 'Client_Profile_Hub'"]
        }

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
    def _call_llm_for_matrix(self, raw_text: str, client_profile: ClientProfileHub) -> Optional[Dict[str, List[str]]]:
        if self.offline_mode or not self.api_key:
            return self._get_mock_matrix()

        print("\n🤖 [Real AI] Генерация Матрицы 4-х Действий через Gemini API...")
        prompt = f"""
        You are a Blue Ocean Strategy expert. Analyze the client's profile and the description of their competitors.
        Based on this, generate a 4-Actions-Framework matrix.
        The client's own information and the information about competitors are provided in a single text block. Your task is to distinguish between them.
        The output MUST be a valid JSON object with keys: "eliminate", "reduce", "raise", "create". Each key should have a list of strings as its value.
        Do not add any text or explanations before or after the JSON object.

        **Client Profile:**
        - Superpower: {client_profile.superpower}
        - Niche: {', '.join(client_profile.niche)}

        **Context (Client & Competitors):**
        "{raw_text}"
        """
        try:
            safety_settings = {
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_ONLY_HIGH',
            }
            model = genai.GenerativeModel('gemini-pro-latest')
            response = model.generate_content(
                prompt,
                safety_settings=safety_settings)
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(cleaned_response)
        except Exception as e:
            print(f"❌ Ошибка при генерации Матрицы 4-х Действий через API: {e}")
            raise e # Пробрасываем ошибку наверх

    def process(self, raw_text: str, client_profile: ClientProfileHub) -> Optional[Dict[str, List[str]]]:
        print("🌊 Запуск Движка Голубого Океана...")
        matrix = self._call_llm_for_matrix(raw_text, client_profile)
        if matrix:
            print("✅ Матрица 4-х Действий успешно сгенерирована!")
        return matrix

class StrategyEngine:
    """Реализует "Движок Стратегии" (Шаг 3, Фаза O)."""
    def __init__(self, api_key: Optional[str] = None, offline_mode: bool = False):
        self.api_key = api_key
        self.offline_mode = offline_mode
        if api_key:
            genai.configure(api_key=api_key)
            
    def _get_mock_roadmap(self) -> Dict[str, Any]:
        print("⚠️ API-ключ не предоставлен. Возвращается симулированный Roadmap.")
        return {
            "roadmap": [
                {"step": 1, "title": "Фаза K: Упаковка", "description": "Создать и запустить 3-5 единиц контента, демонстрирующих 'суперсилу'.", "target_groups": ["Г1", "Г2"]},
                {"step": 2, "title": "Фаза I: Сбор Капитала", "description": "Собрать первые 5-10 отзывов и упаковать 1-2 кейса.", "target_groups": ["Г2"]},
                {"step": 3, "title": "Фаза O: Нетворкинг", "description": "Провести 3 коллаборации с экспертами из смежных ниш.", "target_groups": ["Г3"]},
                {"step": 4, "title": "Фаза N: Масштабирование", "description": "Выступить на 1-2 профильных конференциях или бизнес-мероприятиях.", "target_groups": ["Г4", "Г5"]}
            ],
            "audience_groups": {
                "Г1: Потребители контента": "Массовая аудитория, подписчики. Цель: охват и вовлечение.",
                "Г2: Потребители продуктов": "Клиенты, покупатели. Цель: прямой доход, сбор кейсов.",
                "Г3: Инфлюенсеры / Эксперты": "Партнеры по коллаборациям. Цель: социальный капитал, доступ к новой аудитории.",
                "Г4: Площадки / Компании": "Организаторы мероприятий, бренды. Цель: B2B-партнерства.",
                "Г5: ЛПР (Лица, Принимающие Решения)": "Инвесторы, ключевые фигуры. Цель: достижение Глобальной Цели."
            }
        }

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
    def _call_llm_for_roadmap(self, profile: ClientProfileHub) -> Optional[Dict[str, Any]]:
        if self.offline_mode or not self.api_key:
            return self._get_mock_roadmap()

        print("\n🤖 [Real AI] Генерация Roadmap и 5 Групп ЦА через Gemini API...")
        prompt = f"""
        You are a master strategist. Based on the client's profile, generate a strategic roadmap and define the 5 stakeholder groups.
        The output MUST be a valid JSON object with two keys: "roadmap" and "audience_groups".
        - "roadmap" should be a list of objects, each with "step", "title", "description", and "target_groups".
        - "audience_groups" should be an object with 5 keys (Г1 to Г5) and their descriptions.
        Do not add any text or explanations before or after the JSON object.

        **Client Profile:**
        - Brand Name: {profile.brand_name}
        - Superpower: {profile.superpower}
        - Global Goals (GZ): {', '.join([g['goal'] for g in profile.gz])}
        """
        try:
            safety_settings = {
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_ONLY_HIGH',
            }
            model = genai.GenerativeModel('gemini-pro-latest')
            response = model.generate_content(
                prompt,
                safety_settings=safety_settings)
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(cleaned_response)
        except Exception as e:
            print(f"❌ Ошибка при генерации Roadmap через API: {e}")
            raise e # Пробрасываем ошибку наверх

    def process(self, profile: ClientProfileHub) -> Optional[Dict[str, Any]]:
        print("🗺️ Запуск Движка Стратегии...")
        strategy_data = self._call_llm_for_roadmap(profile)
        if strategy_data:
            print("✅ Roadmap и 5 Групп ЦА успешно сгенерированы!")
        return strategy_data

class HarmonyDiagnosticEngine:
    """Реализует "Движок Диагностики Гармонии" (Шаги 5-6, Фаза K)."""
    # Этот движок работает на основе правил, а не LLM, поэтому API-ключ ему не нужен.
    
    def process(self, profile: ClientProfileHub) -> ClientProfileHub:
        print("🧘 Запуск Движка Диагностики Гармонии...")
        
        # --- УЛУЧШЕНИЕ: Логика поиска "Конфликта F.O.K.I.N." ---
        conflicting_goal = None
        non_conflicting_goal = None
        enemy_triggers = []

        # 1. Ищем конфликтующие цели (связанные с масштабированием услуг) и врагов
        service_keywords = ["клиент", "продюсирование", "менторство", "консультации", "услуги"]
        product_keywords = ["приложение", "сервис", "продукт", "автоматизировать", "платформа"]
        enemy_keywords = ["одиночка", "делегировать", "выгорание", "рутин", "впритык"]

        for goal in profile.gz:
            goal_desc = goal.get("goal", "").lower()
            if any(kw in goal_desc for kw in service_keywords):
                conflicting_goal = goal
            elif any(kw in goal_desc for kw in product_keywords):
                non_conflicting_goal = goal

        for enemy in profile.enemies:
            if any(kw in enemy.lower() for kw in enemy_keywords):
                enemy_triggers.append(enemy)
        
        # 2. Если найден конфликт (цель-услуга + враг-сопротивление) и есть альтернативная цель-продукт
        if conflicting_goal and enemy_triggers and non_conflicting_goal:
            print(f"⚠️  Обнаружен Ключевой Конфликт! Цель '{conflicting_goal['goal']}' vs Враги '{', '.join(enemy_triggers)}'")
            
            # 3. Генерируем "Стратегию Баланса"
            report_text = (
                f"**ДИАГНОСТИКА: Обнаружен Ключевой Конфликт.**\n\n"
                f"Ваша цель **«{conflicting_goal['goal']}»** напрямую конфликтует с вашими внутренними установками: *«{', '.join(enemy_triggers)}»*.\n\n"
                f"**РИСК:** Попытка прямого масштабирования услуг приведет к неизбежному выгоранию, саботажу и потере мотивации, так как это противоречит вашей природе 'игрока-одиночки' и нежеланию управлять множеством клиентских проектов.\n\n"
                f"**СТРАТЕГИЯ БАЛАНСА (v2.0):**\n"
                f"1. **Смена Приоритета:** Ваша истинная цель — не масштабирование услуг, а реализация **«{non_conflicting_goal['goal']}»**. \n"
                f"2. **Цель как Ресурс:** Рассматривайте цель «{conflicting_goal['goal']}» не как конечную точку, а как **временный ресурс (топливо)** для финансирования и запуска вашего основного проекта — «{non_conflicting_goal['goal']}»."
            )
            profile.harmony_report = {"report_text": report_text, "conflict_details": {"conflicting_goal": conflicting_goal, "non_conflicting_goal": non_conflicting_goal, "triggers": enemy_triggers}}
            print("✅ Отчет о Гармонии сгенерирован!")
        else:
            # Старая логика, если сложный конфликт не найден
            profile.harmony_report = {"report_text": "**ДИАГНОСТИКА:** Конфликтов не обнаружено. Стратегия сбалансирована."}
            print("✅ Конфликтов не обнаружено. Стратегия сбалансирована.")
        return profile

class CommerceEngine:
    """Реализует Модуль Коммерции "ПТУ" (Часть V)."""
    def __init__(self, api_key: Optional[str] = None, offline_mode: bool = False):
        self.api_key = api_key
        self.offline_mode = offline_mode
        if api_key:
            genai.configure(api_key=api_key)
            
    def _get_mock_pvl(self) -> ProductValueLadder:
        print("⚠️ API-ключ не предоставлен. Возвращается симулированная Лестница Ценности.")
        return ProductValueLadder(
            lead_magnet=Product(name="Чек-лист '5 грехов в контенте' (Мок)", price=0, purpose="Сбор Лидов", description="PDF-файл с разбором типичных ошибок, которые убивают охваты.", target_audience="Начинающие эксперты", usp="Быстро, бесплатно, полезно."),
            tripwire=Product(name="Мини-курс 'Стратегия первого шага' (Мок)", price=49, purpose="Конверсия в Покупателя", description="Серия из 3-х видео-уроков, помогающая определить свою нишу и УТП.", target_audience="Эксперты с доходом <100к/мес", usp="Низкая цена, высокий результат за короткий срок."),
            core_offer=Product(name="Курс 'CorePath OS' (Мок)", price=1990, purpose="Основная Прибыль", description="Полноценный курс по методологии F.O.K.I.N. с доступом к платформе.", target_audience="Продюсеры, маркетологи, опытные эксперты", usp="Единственная системная методология на рынке."),
            high_ticket=Product(name="Менторство 'Архитектор Наследия' (Мок)", price=15000, purpose="Максимизация LTV", description="Личная работа по построению долгосрочной стратегии и созданию 'Наследия'.", target_audience="Топ-эксперты и владельцы бизнеса", usp="Личный контакт, максимальная кастомизация.")
        )

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
    def _call_llm_for_pvl_design(self, profile: ClientProfileHub) -> Optional[ProductValueLadder]:
        if self.offline_mode or not self.api_key:
            return self._get_mock_pvl()

        print("\n🤖 [Real AI] Проектирование Лестницы Ценности Продукта через Gemini API...")
        prompt = f"""
        You are a product marketing expert. Based on the client's profile, design a Product Value Ladder (PVL).
        The output MUST be a valid JSON object with keys: "lead_magnet", "tripwire", "core_offer", "high_ticket".
        Each key should have an object with "name", "price" (float), and "purpose" as its value.
        Do not add any text or explanations before or after the JSON object.

        **Client Profile:**
        - Brand Name: {profile.brand_name}
        - Superpower: {profile.superpower}
        - Niche: {', '.join(profile.niche)}
        - Enemies (what they fight against): {', '.join(profile.enemies)}
        """
        try:
            safety_settings = {
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_ONLY_HIGH',
            }
            model = genai.GenerativeModel('gemini-pro-latest')
            response = model.generate_content(
                prompt,
                safety_settings=safety_settings)
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            pvl_data = json.loads(cleaned_response)
            
            # Преобразуем JSON в наши объекты Product и ProductValueLadder
            pvl = ProductValueLadder(
                lead_magnet=Product(**pvl_data['lead_magnet']) if 'lead_magnet' in pvl_data else None,
                tripwire=Product(**pvl_data['tripwire']) if 'tripwire' in pvl_data else None,
                core_offer=Product(**pvl_data['core_offer']) if 'core_offer' in pvl_data else None,
                high_ticket=Product(**pvl_data['high_ticket']) if 'high_ticket' in pvl_data else None,
            )
            return pvl
        except Exception as e:
            print(f"❌ Ошибка при проектировании PVL через API: {e}")
            raise e # Пробрасываем ошибку наверх

    def process(self, profile: ClientProfileHub) -> Optional[ProductValueLadder]:
        print("💰 Запуск Движка Коммерции (ПТУ)...")
        pvl = self._call_llm_for_pvl_design(profile)
        if pvl:
            print("✅ 'Лестница Ценности Продукта' успешно спроектирована!")
        return pvl

class AIScenarioProducer:
    """Реализует "AI-Сценарный Продюсер" (Часть IV)."""
    def __init__(self, api_key: Optional[str] = None, offline_mode: bool = False):
        self.api_key = api_key
        self.offline_mode = offline_mode
        if api_key:
            genai.configure(api_key=api_key)
            
    def _get_mock_script(self, profile: ClientProfileHub, product: Optional[Product] = None) -> Dict[str, str]:
        """Возвращает моковый (симулированный) сценарий, если API ключ не предоставлен."""
        print("⚠️ API-ключ не предоставлен. Возвращается симулированный сценарий.")
        product_context = ""
        if product:
            product_context = f"""
        - Product to Promote:
          - Name: {product.name}
          - Price: ${product.price}
          - Purpose: {product.purpose}"""
        
        cta = f"Устали от инфоцыганства? Подпишитесь, здесь про систему."
        if product:
            cta = f"Готовы сделать первый шаг к системе? Забирайте '{product.name}' по ссылке в профиле всего за ${product.price}!"

        anchor_phrase_list = profile.style_voice.get('anchor_phrases', [])
        anchor_phrase = anchor_phrase_list[0] if anchor_phrase_list else ""

        return {
            "title": "Системный Нокаут (Мок)",
            "shock": "*Резкий звук рвущейся бумаги. На экране рвется диплом 'Гуру Маркетинга'.*",
            "hook": f'(Голос, с гневом): "Вам снова продали \'успешный успех\'? Хватит кормиться мусором! {anchor_phrase}".strip()',
            "content": '(Наставнический тон, на фоне схема): "Настоящий рост - это система. Вот 3 шага, как превратить хаос в механизм..."',
            "cta": cta
        }

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
    def _call_llm_for_script_generation(self, profile: ClientProfileHub, anchor_points: Dict, product: Optional[Product] = None) -> Optional[Dict[str, str]]:
        if self.offline_mode or not self.api_key:
            return self._get_mock_script(profile, product)

        print("\n🤖 [Real AI] Генерация сценария через Gemini API...")
        
        product_context = ""
        if product:
            product_context = f"""
        - Product to Promote:
          - Name: {product.name}
          - Price: ${product.price}
          - Purpose: {product.purpose}"""

        prompt = f"""
        You are an expert scriptwriter for social media. Your task is to generate a script for a short video based on the provided context.
        The output MUST be a valid JSON object with the following keys: "title", "shock", "hook", "content", "cta".
        Do not add any text or explanations before or after the JSON object.

        **Context:**
        - Client Profile:
          - Brand Name: {profile.brand_name}
          - Superpower: {profile.superpower}
          - Tone of Voice: {profile.style_voice.get('tone_of_voice', 'Нейтральный')}
          - Enemies: {', '.join(profile.enemies)}
        - 8 Anchor Points:
          - Idea: '{anchor_points.get('idea')}'
          - Content Carrier: {anchor_points.get('content_carrier')}
          - Format: {anchor_points.get('format')}
          - Blog Genre: {anchor_points.get('blog_genre')}
          - Extras/Triggers: {', '.join(anchor_points.get('extras_triggers', []))}
          - Movie Genre: {anchor_points.get('movie_genre')}
          - TV Genre: {anchor_points.get('tv_genre')}
          - Character: {anchor_points.get('character')}{product_context}

        **Task:** Generate a script for a short video.
        **Constraint 1 (Anti-Swipe):** Use: Шок -> Хук -> Контент -> CTA.
        **Constraint 2 (Product-Led):** If a product is mentioned, the CTA must lead to it.
        **Constraint 3 (Verbal Code):** The script MUST include one of these anchor phrases: {profile.style_voice.get('anchor_phrases', [])}. Do not use forbidden words: {profile.style_voice.get('forbidden_words', [])}.
        """ # type: ignore
        print("--- Сформированный Промпт для AI (симуляция) ---")
        print(prompt)

        try:
            safety_settings = {
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_ONLY_HIGH',
            }
            model = genai.GenerativeModel('gemini-pro-latest')
            response = model.generate_content(
                prompt,
                safety_settings=safety_settings)
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(cleaned_response)
        except Exception as e:
            print(f"❌ Ошибка при вызове Gemini API: {e}")
            raise e # Пробрасываем ошибку наверх

    def process(self, profile: ClientProfileHub, anchor_points: Dict, product: Optional[Product] = None) -> Optional[Dict[str, str]]:
        print("🎬 Запуск AI-Сценарного Продюсера...")
        script = self._call_llm_for_script_generation(profile, anchor_points, product)
        if script:
            print("✅ Сценарий успешно сгенерирован!")
        return script

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
    def process_surprise_me(self, profile: ClientProfileHub) -> Optional[Dict[str, str]]:
        """
        Генерирует сценарий в режиме "Удиви меня!", основываясь на ключевых
        аспектах профиля, чтобы побороть творческое выгорание.
        """
        if self.offline_mode or not self.api_key:
            print("⚠️ API-ключ не предоставлен. Возвращается симулированный 'сюрприз'-сценарий.")
            return {
                "title": "Неожиданный Поворот (Мок)",
                "shock": "*Экран темный. Слышен только звук тикающих часов.*",
                "hook": f'(Голос, устало): "Снова дедлайн, а в голове пусто? Знакомо." (пауза) "А что, если я скажу, что ваш главный враг - {profile.enemies[0] if profile.enemies else "рутина"} - это ваше топливо?"',
                "content": f'(Энергично, меняется музыка): "Ваша ценность - {profile.values[0] if profile.values else "системность"}. Перестаньте бороться, начните использовать! Вот как: 1. Найдите в рутине паттерн. 2. Опишите его. 3. Превратите в мем. Вы только что создали контент из ничего!"',
                "cta": "Хотите больше таких 'взломов мозга'? Подпишитесь, здесь мы превращаем выгорание в креатив."
            }

        print("\n🤖 [Real AI] Генерация 'Удиви меня!' сценария через Gemini API...")
        prompt = f"""
        You are a creative producer trying to help a burnt-out client. Your task is to generate a surprising and easy-to-implement script idea for a short video.
        The output MUST be a valid JSON object with keys: "title", "shock", "hook", "content", "cta".
        The idea should be based on the client's core values or their "enemies" (what they fight against). It should feel unexpected and require minimal creative effort from the client.
        Do not add any text or explanations before or after the JSON object.

        **Client Profile:**
        - Core Values: {', '.join(profile.values)}
        - Enemies (what they fight against): {', '.join(profile.enemies)}
        - Superpower: {profile.superpower}

        **Task:** Generate a surprising script idea.
        """
        try:
            safety_settings = {
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_ONLY_HIGH',
            }
            model = genai.GenerativeModel('gemini-pro-latest')
            response = model.generate_content(prompt, safety_settings=safety_settings)
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(cleaned_response)
        except Exception as e:
            print(f"❌ Ошибка при генерации 'Удиви меня!' сценария: {e}")
            raise e

class InterviewEngine:
    """
    Реализует "AI-Интервьюера" для проведения углубленного диалога с пользователем.
    """
    def __init__(self, api_key: Optional[str] = None, offline_mode: bool = False):
        self.api_key = api_key
        self.offline_mode = offline_mode
        if api_key:
            genai.configure(api_key=api_key)

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
    def get_follow_up_question(self, main_question: str, conversation_history: str) -> Optional[str]:
        """
        Генерирует уточняющий вопрос на основе предыдущего ответа пользователя.
        """
        if self.offline_mode or not self.api_key:
            print("⚠️ API-ключ не предоставлен. Уточняющий вопрос не будет сгенерирован.")
            return "Спасибо, принято. Можете переходить к следующему вопросу."

        print("\n🤖 [AI-Интервьюер] Генерация уточняющего вопроса...")

        prompt = f"""
        You are a thoughtful and empathetic strategic consultant conducting an interview. Your goal is to help the user provide a deep and comprehensive answer.
        A main question was asked, and the user has provided some answers.
        Based on the conversation so far, ask ONE clarifying or deepening follow-up question to encourage the user to elaborate.
        - If the answer is short, ask for more details.
        - If the answer mentions something interesting, ask to expand on that specific point.
        - If the answer is very comprehensive, you can simply say "Спасибо, это очень развернутый ответ. Когда будете готовы, переходите к следующему вопросу."
        - Your question should be polite, encouraging, and in Russian.

        **Main Question:**
        {main_question}

        **Conversation History so far:**
        {conversation_history}

        Now, provide the next follow-up question.
        """
        try:
            model = genai.GenerativeModel('gemini-pro-latest')
            response = model.generate_content(prompt)
            # Убираем лишние символы, если они есть
            follow_up = response.text.strip().replace("*", "")
            return follow_up
        except Exception as e:
            print(f"❌ Ошибка при генерации уточняющего вопроса: {e}")
            raise e # Пробрасываем ошибку наверх

class ShowPitchEngine:
    """Реализует "Движок Драматургии" для создания питча флагманского шоу (Шаг 7)."""
    def __init__(self, api_key: Optional[str] = None, offline_mode: bool = False):
        self.api_key = api_key
        self.offline_mode = offline_mode
        if api_key:
            genai.configure(api_key=api_key)

    def _get_mock_pitch(self) -> Dict[str, Any]:
        print("⚠️ API-ключ не предоставлен. Возвращается симулированный питч шоу.")
        return {
            "show_title": "Архитектор Личностей (Мок)",
            "concept": "YouTube-шоу, в котором ведущий разбирает 'устаревшие' подходы к личному бренду и противопоставляет им свою системную методологию, демонстрируя ее на реальных кейсах.",
            "dramaturgy": {
                "step1_you": "Подписчик, который 'застрял' и не знает, куда двигаться дальше.",
                "step2_need": "Хочет найти себя и свой путь, обрести свободу.",
                "step3_go": "Начинает смотреть шоу 'Архитектор Личностей'.",
                "step4_search": "Изучает методологию, видит системный подход.",
                "step5_find": "Осознает, что ему нужен не просто контент, а система для самоопределения.",
                "step6_take": "Покупает доступ к приложению-диагносту.",
                "step7_return": "Находит 'то, что по-настоящему нравится', получает ясность.",
                "step8_changed": "Превращается в 'увлеченного человека', который строит свой бренд осознанно."
            }
        }

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
    def _call_llm_for_pitch(self, profile: ClientProfileHub) -> Optional[Dict[str, Any]]:
        if self.offline_mode or not self.api_key:
            return self._get_mock_pitch()

        print("\n🤖 [Real AI] Проектирование Питча Шоу через Gemini API...")
        prompt = f"""
        You are a showrunner and producer. Your task is to create a pitch document for a flagship YouTube show based on the client's profile and their balanced strategy.
        The output MUST be a valid JSON object with keys: "show_title", "concept", and "dramaturgy".
        - "dramaturgy" must be an object with 8 keys (step1_you, step2_need, ..., step8_changed) based on Harmon's Story Circle, describing the viewer's journey.
        Do not add any text or explanations before or after the JSON object.

        **Client Profile & Strategy:**
        - Brand Name: {profile.brand_name}
        - Superpower: {profile.superpower}
        - Mission: {profile.values}
        - Balanced Strategy: {profile.harmony_report.get('report_text', 'Не определена')}
        - Target Audience (G1): {profile.audience_groups.get('Г1: Потребители контента', 'Не определена')}
        - Role Models: {profile.style_voice.get('role_models', 'Не указаны')}

        **Task:** Generate the pitch document. The show should aim to solve the audience's main problem and subtly lead to the client's 'non-conflicting' goal (e.g., an app or a product).
        """
        try:
            safety_settings = {
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_ONLY_HIGH',
            }
            model = genai.GenerativeModel('gemini-pro-latest')
            response = model.generate_content(prompt, safety_settings=safety_settings)
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(cleaned_response)
        except Exception as e:
            print(f"❌ Ошибка при генерации Питча Шоу: {e}")
            raise e

    def process(self, profile: ClientProfileHub) -> Optional[Dict[str, Any]]:
        print("🎬 Запуск Движка Драматургии...")
        pitch = self._call_llm_for_pitch(profile)
        if pitch:
            print("✅ Питч флагманского шоу успешно сгенерирован!")
        return pitch

class FormatEngine:
    """Реализует "Движок Форматов" для создания библиотеки поддерживающих форматов (Шаг 8)."""
    def __init__(self, api_key: Optional[str] = None, offline_mode: bool = False):
        self.api_key = api_key
        self.offline_mode = offline_mode
        if api_key:
            genai.configure(api_key=api_key)

    def _get_mock_formats(self) -> List[Dict[str, Any]]:
        print("⚠️ API-ключ не предоставлен. Возвращаются симулированные форматы.")
        return [
            {
                "format_name": "Анти-Продюсер (Мок)",
                "idea": "Критика 'устаревших' подходов в индустрии.",
                "content_carrier": "Шортс",
                "format_tone": "Развлекательный",
                "blog_genre": "Критика / Хейтинг",
                "extras_triggers": ["Провокация", "Юмор"]
            },
            {
                "format_name": "Разбор Кейса (Мок)",
                "idea": "Демонстрация методологии на реальном примере.",
                "content_carrier": "Статья",
                "format_tone": "Экспертный",
                "blog_genre": "Аналитика / Разбор",
                "extras_triggers": ["Соц. док-во", "Кейс/Пример"]
            }
        ]

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
    def _call_llm_for_formats(self, profile: ClientProfileHub) -> Optional[List[Dict[str, Any]]]:
        if self.offline_mode or not self.api_key:
            return self._get_mock_formats()

        print("\n🤖 [Real AI] Генерация Библиотеки Форматов через Gemini API...")
        prompt = f"""
        You are a content strategist. Based on the client's profile and their flagship show pitch, generate a list of 3-4 supporting content formats.
        The output MUST be a valid JSON object containing a single key "formats", which is a list of objects.
        Each format object must have a "format_name" and keys corresponding to the 8 Anchor Points (idea, content_carrier, format_tone, blog_genre, extras_triggers, movie_genre, tv_genre, character).
        Do not add any text or explanations before or after the JSON object.

        **Client Profile & Show Pitch:**
        - Brand Name: {profile.brand_name}
        - Superpower: {profile.superpower}
        - Balanced Strategy: {profile.harmony_report.get('report_text', 'Не определена')}
        - Show Pitch: {profile.show_pitch}

        **Task:** Generate the list of content formats.
        """
        try:
            safety_settings = {
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_ONLY_HIGH',
            }
            model = genai.GenerativeModel('gemini-pro-latest')
            response = model.generate_content(prompt, safety_settings=safety_settings)
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(cleaned_response).get("formats", [])
        except Exception as e:
            print(f"❌ Ошибка при генерации Библиотеки Форматов: {e}")
            raise e

    def process(self, profile: ClientProfileHub) -> Optional[List[Dict[str, Any]]]:
        print("📚 Запуск Движка Форматов...")
        formats = self._call_llm_for_formats(profile)
        if formats:
            print(f"✅ Библиотека из {len(formats)} форматов успешно сгенерирована!")
        return formats

class ContentPlanEngine:
    """Реализует "Движок Контент-Плана" для создания недельного плана (Шаг 10)."""
    def __init__(self, api_key: Optional[str] = None, offline_mode: bool = False):
        self.api_key = api_key
        self.offline_mode = offline_mode
        if api_key:
            genai.configure(api_key=api_key)

    def _get_mock_plan(self) -> List[Dict[str, str]]:
        print("⚠️ API-ключ не предоставлен. Возвращается симулированный контент-план.")
        return [
            {"day": "ПН", "theme": "Критика 'устаревших' подходов", "format_used": "Анти-Продюсер (Мок)", "target_audience": "Группа 1 / 2", "goal": "Прогрев к Приложению"},
            {"day": "ВТ", "theme": "Разбор кейса клиента X", "format_used": "Разбор Кейса (Мок)", "target_audience": "Группа 2 (B2B)", "goal": "Соц. док-во, Лиды на аудит"},
            {"day": "СР", "theme": "Закулисье: тестирую новую фичу", "format_used": "Личный (Бэкстейдж)", "target_audience": "Группа 1", "goal": "Лояльность, Прогрев"},
            {"day": "ЧТ", "theme": "Почему дети не хотят учиться?", "format_used": "Экспертная Статья", "target_audience": "Группа 1 / 3 / 5", "goal": "Миссия, Влияние"},
            {"day": "ПТ", "theme": "Прямой эфир: разбор стратегий подписчиков", "format_used": "Флагманское Шоу", "target_audience": "Группа 1 / 2", "goal": "Лиды на Приложение"},
            {"day": "СБ", "theme": "Почему 'долгие согласования' убивают креатив", "format_used": "Анти-Продюсер (Мок)", "target_audience": "Группа 2 (Продюсеры)", "goal": "Влияние"},
            {"day": "ВС", "theme": "Мой новый трек (Личная мечта)", "format_used": "Личный (Аудио-пост)", "target_audience": "Группа 1", "goal": "Баланс, Лояльность"},
        ]

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
    def _call_llm_for_plan(self, profile: ClientProfileHub) -> Optional[List[Dict[str, str]]]:
        if self.offline_mode or not self.api_key:
            return self._get_mock_plan()

        print("\n🤖 [Real AI] Генерация Контент-Плана на неделю через Gemini API...")
        prompt = f"""
        You are a master content strategist. Your task is to create a 7-day content plan.
        The output MUST be a valid JSON object containing a single key "content_plan", which is a list of 7 objects.
        Each object must represent a day and have the keys: "day" (e.g., "ПН"), "theme", "format_used", "target_audience", and "goal".
        Use the provided content formats. The plan should strategically work towards the client's balanced strategy goals.
        Do not add any text or explanations before or after the JSON object.

        **Client Profile & Strategic Assets:**
        - Balanced Strategy: {profile.harmony_report.get('report_text', 'Не определена')}
        - Flagship Show Pitch: {profile.show_pitch}
        - Available Content Formats: {profile.formats}
        - Audience Groups: {profile.audience_groups}

        **Task:** Generate the 7-day content plan.
        """
        try:
            safety_settings = {
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_ONLY_HIGH',
            }
            model = genai.GenerativeModel('gemini-pro-latest')
            response = model.generate_content(prompt, safety_settings=safety_settings)
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(cleaned_response).get("content_plan", [])
        except Exception as e:
            print(f"❌ Ошибка при генерации Контент-Плана: {e}")
            raise e

    def process(self, profile: ClientProfileHub) -> Optional[List[Dict[str, str]]]:
        print("🗓️ Запуск Движка Контент-Плана...")
        plan = self._call_llm_for_plan(profile)
        if plan:
            print(f"✅ Контент-план на {len(plan)} дней успешно сгенерирован!")
        return plan

class SynergyEngine:
    """
    Реализует "Движок Синергии" для поиска коллабораций между клиентами (Фаза O).
    """
    def __init__(self, api_key: Optional[str] = None, offline_mode: bool = False):
        self.api_key = api_key
        self.offline_mode = offline_mode
        if api_key:
            genai.configure(api_key=api_key)

    def _get_mock_pitch(self) -> Dict[str, str]:
        print("⚠️ API-ключ не предоставлен. Возвращается симулированный питч коллаборации.")
        return {
            "collaboration_title": "Системный Подход vs. Творческий Хаос (Мок)",
            "concept": "Совместный прямой эфир, где два эксперта с разными подходами (системный и креативный) разбирают одну и ту же проблему, показывая силу синергии.",
            "benefit_for_all": "Обмен аудиториями, демонстрация глубины экспертизы через диалог, создание уникального контента.",
            "format": "Совместный прямой эфир / Панельная дискуссия."
        }

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
    def _call_llm_for_synergy(self, profiles: List[ClientProfileHub]) -> Optional[Dict[str, str]]:
        if self.offline_mode or not self.api_key:
            return self._get_mock_pitch()

        print("\n🤖 [Real AI] Поиск синергии между профилями через Gemini API...")
        
        profiles_summary = ""
        for i, p in enumerate(profiles):
            profiles_summary += f"""
            ---
            **Профиль #{i+1}: {p.brand_name}**
            - Ниша: {p.niche}
            - Суперсила: {p.superpower}
            - ЦА (Потребители): {p.audience_groups.get('Г1: Потребители контента', 'Не указана')}
            - Враги (с чем борется): {p.enemies}
            - Ценности/Миссия: {p.values}
            ---
            """

        prompt = f"""
        You are a master networker and producer. Your task is to find a powerful collaboration opportunity between the following client profiles.
        Analyze their strengths, weaknesses, target audiences, and values to propose a single, compelling collaboration idea.
        The output MUST be a valid JSON object with keys: "collaboration_title", "concept", "benefit_for_all", and "format".
        Do not add any text or explanations before or after the JSON object.

        **Client Profiles Data:**
        {profiles_summary}

        **Task:** Find a point of synergy and generate a collaboration pitch. Look for complementary skills, overlapping audiences, or common enemies.
        """
        try:
            safety_settings = {
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_ONLY_HIGH',
            }
            model = genai.GenerativeModel('gemini-pro-latest')
            response = model.generate_content(prompt, safety_settings=safety_settings)
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(cleaned_response)
        except Exception as e:
            print(f"❌ Ошибка при поиске Синергии: {e}")
            raise e

    def process(self, profiles: List[ClientProfileHub]) -> Optional[Dict[str, str]]:
        print("🤝 Запуск Движка Синергии...")
        if len(profiles) < 2:
            print("❌ Для поиска синергии необходимо как минимум два профиля.")
            return None
        pitch = self._call_llm_for_synergy(profiles)
        if pitch:
            print("✅ Питч коллаборации успешно сгенерирован!")
        return pitch
class CalendarEngine:
    """
    Реализует "Интеллектуальный Календарь" (Часть VII.2) и декомпозицию (Часть VI.1.3).
    Превращает артефакты (сценарии) в конкретные задачи.
    """
    def __init__(self, api_key: Optional[str] = None, offline_mode: bool = False):
        self.api_key = api_key
        self.offline_mode = offline_mode
        if api_key:
            genai.configure(api_key=api_key)

    def _get_mock_tasks(self) -> List[Task]:
        print("⚠️ API-ключ не предоставлен. Возвращаются симулированные задачи.")
        return [
            Task(description="Написать финальный текст сценария (Мок)"),
            Task(description="Подготовить реквизит: диплом 'Гуру Маркетинга' (Мок)"),
            Task(description="Настроить камеру и свет для съемки (Мок)"),
            Task(description="Снять основную часть с 'говорящей головой' (Мок)"),
            Task(description="Смонтировать и добавить эффекты (Мок)")
        ]

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
    def decompose_script_to_tasks(self, generated_script: Dict[str, str], anchor_points: Dict) -> List[Task]:
        """
        Декомпозирует сценарий в список задач с помощью AI.
        """
        if self.offline_mode or not self.api_key:
            return self._get_mock_tasks()

        print("️  Запуск Движка Календаря: AI-декомпозиция сценария в задачи...")
        
        script_text = "\n".join([f"- {key.capitalize()}: {value}" for key, value in generated_script.items() if key != 'title'])

        prompt = f"""
        You are an experienced producer and project manager. Your task is to decompose a video script into a detailed list of actionable tasks required for its production.
        Analyze the provided script and its context. The output MUST be a valid JSON object containing a single key "tasks", which is a list of strings. Each string is a task description.
        The tasks should be logical, sequential, and cover pre-production, production, and post-production.
        Be specific. If the script mentions props, locations, or specific actions, include them in the tasks.

        **Script Context:**
        - Title: {generated_script.get('title', 'N/A')}
        - Content Carrier: {anchor_points.get('content_carrier', 'short video')}
        - Atmosphere (Movie Genre): {anchor_points.get('movie_genre', 'not specified')}

        **Script Body:**
        {script_text}

        Generate the task list now.
        """
        try:
            safety_settings = {
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_ONLY_HIGH',
            }
            model = genai.GenerativeModel('gemini-pro-latest')
            response = model.generate_content(prompt, safety_settings=safety_settings)
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            task_data = json.loads(cleaned_response)
            tasks = [Task(description=desc) for desc in task_data.get("tasks", [])]
            print(f"✅ AI сгенерировал {len(tasks)} задач для проекта.")
            return tasks
        except Exception as e:
            print(f"❌ Ошибка при AI-декомпозиции задач: {e}")
            raise e # Пробрасываем ошибку наверх
