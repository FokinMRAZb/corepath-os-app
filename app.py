# /Users/valentinfokin/Desktop/CorePath OS 2.0/app.py
import streamlit as st
import json
from dataclasses import asdict
import base64
from datetime import date
from core_logic import (
    IngestionEngine, 
    BlueOceanEngine, 
    HarmonyDiagnosticEngine, 
    StrategyEngine,
    CommerceEngine, 
    ClientProfileHub,
    AIScenarioProducer, 
    InterviewEngine,
    ShowPitchEngine,
    FormatEngine,
    ContentPlanEngine,
    SynergyEngine,
    CalendarEngine,
    ANCHOR_POINTS_DATA,
    InfluenceAsset,
    TeamMember,
    Comment,
    Attachment
)
from st_audiorec import st_audiorec

# --- НОВЫЙ БЛОК: Вопросы для опросника ---
# Полный, структурированный опросник на основе предоставленного текста
QUESTIONNAIRE_QUESTIONS = {
    "Блок 0: Идентификация": {
        "q0": "ФИО или Название компании"
    },
    "Блок 1: Тактический Спринт": {
        "q1": "1. Если бы у нас было всего 30 дней на совместную работу, какой один тактический результат (в деньгах, регистрациях, подписчиках) снял бы 80% твоего стресса?"
    },
    "Блок 2: ФАЗА F (Foundation / BSC) — Часть А: Личные Цели": {
        "q2": "1. Три заветные мечты (если отбросить 'реальность')?",
        "q3": "2. Что ты ищешь в любой деятельности? (Признание, любовь, деньги, свобода, безопасность?)",
        "q4": "3. Опиши свой 'идеальный день' через 3 года.",
        "q5": "4. Какие у тебя есть 'Ограничивающие убеждения' о деньгах, успехе, медийности?",
        "q6": "5. Какие у тебя есть 'не-бизнес' навыки? (Эмпатия, дисциплина, юмор?)",
        "q7": "6. Что ты можешь делать бесплатно и с удовольствием?",
        "q8": "7. Без каких процессов ты не готов работать? (Что тебя 'выжигает'?)",
        "q9": "8. Какие у тебя 'вредные' привычки или зависимости, которые блокируют рост?"
    },
    "Блок 2: ФАЗА F (Foundation / BSC) — Часть Б: Бизнес-Цели": {
        "q10": "1. Какая у тебя текущая продуктовая линейка? (Что? По какой цене?)",
        "q11": "2. Какой текущий среднемесячный доход? Какая цель на 1 год?",
        "q12": "3. Как сейчас выглядит твоя воронка продаж? (Откуда приходят люди и как они покупают?)",
        "q13": "4. Какая у тебя бизнес-модель (онлайн-школа, услуги, прод. центр)?",
        "q14": "5. Какие у тебя ключевые активы? (Команда, база клиентов, технология, методология?)"
    },
    "Блок 2: ФАЗА F (Foundation / BSC) — Часть В: Общественные / Миссия": {
        "q15": "1. Какую 'несправедливость' или 'проблему' в мире ты хочешь решить?",
        "q16": "2. Если ты решишь эту проблему, как изменится мир/индустрия?"
    },
    "Блок 2: ФАЗА F (Foundation / BSC) — Часть Г: Медийные": {
        "q17": "1. Что для тебя 'успех' в медиа? (Цифры, статус, влияние?)",
        "q18": "2. Чей уровень медийности для тебя — эталон?"
    },
    "Блок 3: ФАЗА F (Foundation / Blue Ocean) — 'Отмена Конкуренции'": {
        "q19": "1. Назови 3-5 главных 'конкурентов' или 'лидеров' в твоей нише.",
        "q20": "2. Что все они делают одинаково? Какой 'стандарт индустрии' ты считаешь устаревшим или глупым?",
        "q21": "3. Что они делают 'слишком много', на что тратят ресурсы, а клиенту это не нужно?",
        "q22": "4. Что они не делают, но ты считаешь это критически важным?",
        "q23": "5. Что в твоей нише никогда не делали, но это могло бы 'взорвать' рынок?"
    },
    "Блок 4: ФАЗА O (Orchestration / Ecosystem) — 'Карта Стейкхолдеров'": {
        "q24": "1. Опиши своего текущего подписчика (кто уже тебя смотрит, какие у него боли).",
        "q25": "2. Опиши своего идеального клиента, который уже платил тебе (почему он купил, какую реальную проблему решил).",
        "q26": "3. Назови 3-5 'гейткиперов' — ключевых фигур в твоей нише, чье одобрение или коллаборация дадут тебе реальный рост.",
        "q27": "4. Какие компании, платформы, бренды, фестивали или агентства заинтересованы в твоей аудитории или продукте?",
        "q28": "5. Если бы ты мог дотянуться до одного человека (политика, олигарха, топ-менеджера), который изменил бы всё, кто бы это был?"
    }
}


# ==============================================================================
# --- БЛОК 3: ИНТЕРФЕЙС STREAMLIT И ЛОГИКА ЗАПУСКА ---
# ==============================================================================

st.set_page_config(layout="wide")

st.title("🤖 CorePath OS")

# --- Инициализация состояния ---
if 'client_profile' not in st.session_state:
    st.session_state.client_profile = None 
if 'product_ladder' not in st.session_state:
    st.session_state.product_ladder = None
if 'script_history' not in st.session_state:
    st.session_state.script_history = []
if 'current_script' not in st.session_state:
    st.session_state.current_script = None
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
# --- НОВЫЙ БЛОК: Состояние для интерактивного опросника ---
if 'interview_answers' not in st.session_state:
    st.session_state.interview_answers = {}
if 'current_q_index' not in st.session_state:
    st.session_state.current_q_index = 0
if 'current_conversation' not in st.session_state:
    st.session_state.current_conversation = []
if 'profile_generated' not in st.session_state:
    st.session_state.profile_generated = False
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "📊 Дашборд"
if 'processing' not in st.session_state:
    st.session_state.processing = False

# --- УЛУЧШЕНИЕ: ЛОГИКА ОТОБРАЖЕНИЯ СТАРТОВОГО ЭКРАНА ИЛИ РАБОЧЕГО ПРОСТРАНСТВА ---

if not st.session_state.profile_generated:
    # --- ЭТАП 1: СТАРТОВЫЙ ЭКРАН ДИАГНОСТИКИ ---
    with st.expander("🚀 Диагностика", expanded=True): # Ракета
        api_key = st.text_input("🔑 Ваш Gemini API Ключ", type="password", help="Ваш ключ будет использован только для этой сессии и нигде не сохраняется.", key="api_key_input")

        # --- УЛУЧШЕНИЕ: Выбор режима ввода ---
        input_mode_tab1, input_mode_tab2 = st.tabs(["Интерактивный Опрос", "Быстрый Ввод (для опытных)"])

        with input_mode_tab1:
            st.markdown("Отвечайте на вопросы в диалоге с AI-ассистентом для максимальной глубины.")
        
        # --- РЕАЛИЗАЦИЯ ИНТЕРАКТИВНОГО ОПРОСА ---
        all_questions = [(k, v) for block in QUESTIONNAIRE_QUESTIONS.values() for k, v in block.items()]
        
        # --- УЛУЧШЕНИЕ: Динамическое раскрытие первого блока ---
        if st.session_state.current_q_index < len(all_questions): # Проверяем, не закончен ли опрос
            q_key, q_text = all_questions[st.session_state.current_q_index]

            st.subheader(f"Вопрос {st.session_state.current_q_index + 1} / {len(all_questions)}")
            st.markdown(f"**{q_text}**")

            # Отображение истории текущего диалога
            for i, (speaker, text) in enumerate(st.session_state.current_conversation):
                if speaker == "user":
                    st.chat_message("user").write(text)
                else:
                    st.chat_message("assistant").write(text)

            # Поле для ответа
            user_answer = st.text_area("Ваш ответ:", key=f"interview_input_{q_key}", height=150, disabled=st.session_state.processing)

            if st.button("💬 Ответить", key=f"submit_{q_key}", disabled=st.session_state.processing):
                if user_answer:
                    # Добавляем ответ пользователя в диалог
                    st.session_state.current_conversation.append(("user", user_answer))
                    
                    # Генерируем уточняющий вопрос
                    interview_engine = InterviewEngine(api_key=st.session_state.api_key_input)
                    conversation_str = "\n".join([f"{s}: {t}" for s, t in st.session_state.current_conversation])
                    follow_up = interview_engine.get_follow_up_question(q_text, conversation_str)
                    
                    if follow_up:
                        st.session_state.current_conversation.append(("ai", follow_up))
                    
                    st.rerun()

            if st.button("✅ Завершить и перейти к следующему вопросу", type="primary", disabled=st.session_state.processing):
                # Сохраняем весь диалог как ответ на основной вопрос
                final_answer_text = "\n".join([f"Пользователь: {t}" if s == "user" else f"AI-Ассистент: {t}" for s, t in st.session_state.current_conversation])
                st.session_state.interview_answers[q_key] = final_answer_text
                
                # Сбрасываем и переходим к следующему
                st.session_state.current_conversation = []
                st.session_state.current_q_index += 1
                st.rerun()
        else:
            st.success("🎉 Опрос завершен! Все ответы собраны.")
            st.info("Теперь вы можете запустить полную диагностику на основе ваших развернутых ответов.")

        run_from_questionnaire = st.button("🚀 Запустить Диагностику по ответам", disabled=(st.session_state.current_q_index < len(all_questions) or st.session_state.processing))

        with input_mode_tab2:
            raw_text_area = st.text_area("Шаг 1: Вставьте Единый Контекст", height=250, key="raw_text", placeholder="Вставьте сюда весь текст из опросника, включая информацию о себе и о конкурентах...", disabled=st.session_state.processing)
            run_from_text = st.button("🚀 Запустить Диагностику и Проектирование", disabled=st.session_state.processing)

    if run_from_questionnaire or run_from_text:
            st.session_state.processing = True
            # --- УЛУЧШЕНИЕ: Поэтапный индикатор процесса ---
            with st.status("Запускаю полный цикл диагностики F.O.K.I.N...", expanded=True) as status:
                try:
                    # 1. Определяем, какой текст использовать
                    if run_from_questionnaire:
                        full_text = ""
                        for block_title, questions in QUESTIONNAIRE_QUESTIONS.items():
                            full_text += f"\n\n--- {block_title} ---\n\n"
                            for q_key, q_text in questions.items():
                                answer = st.session_state.interview_answers.get(q_key, "").strip()
                                if answer:
                                    full_text += f"Вопрос: {q_text}\n\n--- Начало диалога ---\n{answer}\n--- Конец диалога ---\n\n"
                        st.session_state.raw_text = full_text

                    # 2. Инициализация движков
                    api_key = st.session_state.api_key_input
                    ingestion_engine = IngestionEngine(api_key=api_key)
                    blue_ocean_engine = BlueOceanEngine(api_key=api_key)
                    harmony_engine = HarmonyDiagnosticEngine()
                    strategy_engine = StrategyEngine(api_key=api_key)
                    commerce_engine = CommerceEngine(api_key=api_key)
                    show_pitch_engine = ShowPitchEngine(api_key=api_key)
                    format_engine = FormatEngine(api_key=api_key)
                    content_plan_engine = ContentPlanEngine(api_key=api_key)
                
                    # 3. Основной конвейер обработки с пошаговым логированием
                    status.update(label="Шаг 1/7: 🚀 Движок Поглощения. Извлекаю ваше ценностное ядро из ответов...")
                    profile = ingestion_engine.process(st.session_state.raw_text)
                    if not profile: raise ValueError("Не удалось создать профиль. Проверьте API ключ или текст опросника.")

                    status.update(label="Шаг 2/7: 🌊 Движок Голубого Океана. Ищу уникальное позиционирование, анализируя конкурентов...")
                    matrix = blue_ocean_engine.process(st.session_state.raw_text, profile)
                    profile.positioning_matrix = matrix

                    status.update(label="Шаг 3/7: 🗺️ Движок Стратегии. Проектирую дорожную карту и карту аудиторий...")
                    strategy_data = strategy_engine.process(profile)
                    profile.strategic_goals = strategy_data

                    status.update(label="Шаг 4/7: 💰 Движок Коммерции. Создаю продуктовую линейку для монетизации...")
                    product_ladder = commerce_engine.process(profile)

                    status.update(label="Шаг 5/7: 🧘‍♂️ Движок Гармонии. Выявляю ключевые конфликты для создания 'Стратегии Баланса'...")
                    profile = harmony_engine.process(profile)

                    status.update(label="Шаг 6/7: 🎬 Движок Драматургии. Проектирую питч вашего флагманского шоу...")
                    show_pitch = show_pitch_engine.process(profile)
                    profile.show_pitch = show_pitch

                    status.update(label="Шаг 7/7: 📚 Движок Форматов и Плана. Создаю библиотеку контента и план на неделю...")
                    formats = format_engine.process(profile)
                    profile.formats = formats
                    plan = content_plan_engine.process(profile)
                    profile.content_plan = plan

                    status.update(label="✅ Диагностика завершена! Сохраняю результаты...", state="complete")

                    # 4. Сохранение результатов в состояние сессии
                    st.session_state.client_profile = profile
                    st.session_state.scenario_producer = AIScenarioProducer(api_key=api_key)
                    st.session_state.calendar_engine = CalendarEngine(api_key=api_key)
                    if product_ladder:
                        st.session_state.client_profile.products = [asdict(p) for p in [product_ladder.lead_magnet, product_ladder.tripwire, product_ladder.core_offer, product_ladder.high_ticket] if p]
                        st.session_state.product_ladder = product_ladder
                    
                    # 5. Переключаем на основной экран
                    st.session_state.profile_generated = True
                    st.session_state.processing = False
                    st.rerun()

                except Exception as e:
                    st.session_state.processing = False
                    status.update(label=f"Ошибка на этапе диагностики: {e}", state="error")
                    st.error(f"Произошла ошибка: {e}")

    # --- Загрузка профиля на стартовом экране ---
    uploaded_file = st.file_uploader("...или загрузите существующий профиль", type=["json"])
    if uploaded_file is not None:
        data = json.load(uploaded_file)
        # ... (логика десериализации остается той же)
        profile = ClientProfileHub(**data)
        st.session_state.client_profile = profile
        st.session_state.profile_generated = True
        st.rerun()

else:
    # --- ЭТАП 2: ОСНОВНОЕ РАБОЧЕЕ ПРОСТРАНСТВО ---
    col1, col2 = st.columns([1, 3]) # Делаем левую колонку уже

    with col1:
        st.header("Управление")

        # --- Блок сохранения/загрузки ---
        with st.expander("⚙️ Управление Профилем", expanded=True):
            # Функция сохранения
            def render_download_button():
                if st.session_state.client_profile:
                    profile_dict = asdict(st.session_state.client_profile)
                    # ... (логика кодирования данных)
                    profile_json = json.dumps(profile_dict, indent=2, ensure_ascii=False, default=str).encode('utf-8')
                    st.download_button(
                        label="⬇️ Сохранить профиль",
                        data=profile_json,
                        file_name=f"corepath_profile_{st.session_state.client_profile.brand_name}.json",
                        mime="application/json",
                    )
                else:
                    st.button("⬇️ Сохранить профиль", disabled=True)
            
            render_download_button()

        # --- Блок поиска ---
        with st.expander("Поиск по проекту"):
            search_term = st.text_input("Найти...", label_visibility="collapsed")
            # ... (логика поиска)

        # --- Блок редактирования ---
        with st.expander("Редактировать Профиль"):
            profile = st.session_state.client_profile
            # --- ИСПРАВЛЕНИЕ ОШИБКИ: Проверяем, что профиль существует, перед доступом к нему ---
            if not profile:
                st.warning("Профиль еще не создан.")
                st.stop()

            with st.form(key='profile_edit_form'):
                # ... (форма редактирования)
                st.form_submit_button("💾 Сохранить изменения")

    with col2:
        st.header(" ") # Пустой заголовок для выравнивания
        
        # --- ГЛАВНОЕ ИЗМЕНЕНИЕ: НОВАЯ СТРУКТУРА ВКЛАДОК ---
        tab_list = [
            "📊 Дашборд", 
            "👤 ОБРАЗ", 
            "🧭 Стратегия", 
            "🗓️ Контент-План",
            "� Продукты", 
            "🎬 Контент", 
            "📋 Задачи", 
            "🏆 Медийный Капитал", 
            "👥 Команда",
            "🤝 Синергия"
        ]
        
        tabs = st.tabs(tab_list)
        tab_dashboard, tab_obraz, tab_strategy, tab_plan, tab_products, tab_content, tab_tasks, tab_capital, tab_team, tab_synergy = tabs

        def generate_notifications():
            notifications = []
            today = date.today()
            
            for task in st.session_state.tasks:
                # 1. Уведомления о дедлайнах
                if task.deadline and task.status != "Done":
                    delta = (task.deadline - today).days
                    if 0 <= delta <= 3:
                        notifications.append(f"🗓️ Приближается дедлайн задачи «{task.description}» (осталось {delta} дн.)")
                    elif delta < 0:
                        notifications.append(f"🔥 Задача «{task.description}» просрочена на {-delta} дн.")

                # 2. Уведомления о новых комментариях
                for comment in task.comments:
                    if comment.author != "Я": # Предполагаем, что "Я" - это текущий пользователь
                        notifications.append(f"💬 Новый комментарий к задаче «{task.description}» от {comment.author}: {comment.text}")
            return notifications

        # --- НОВЫЙ БЛОК: ОТОБРАЖЕНИЕ УВЕДОМЛЕНИЙ ---
        notifications = generate_notifications()
        if notifications:
            st.subheader("Уведомления")
            for notification in notifications:
                st.warning(notification)
            st.markdown("---")

        # --- НОВЫЙ БЛОК: ВКЛАДКА "ОБРАЗ" ---
        # --- ИСПРАВЛЕНИЕ ОШИБКИ: Добавляем проверку на существование профиля ---
        if not st.session_state.client_profile:
            st.warning("Профиль еще не сгенерирован. Пожалуйста, пройдите диагностику.")
            
        with tab_obraz:
            st.subheader("Архитектура «Образа»")
            st.info("Здесь вы конструируете свой аутентичный образ. Эти данные напрямую влияют на генерацию контента и стратегии.")

            # --- Модуль 1: Эмоциональное Ядро ---
            with st.expander("Блок 1: Эмоциональное Ядро (Матрица 8 Ключевых Эмоций)", expanded=True):
                st.markdown("Зафиксируйте ваши эмоциональные реакции. Это основа драматургии вашего образа.")
                
                # Инициализация матрицы, если она пуста
                if not st.session_state.client_profile.emotion_matrix:
                    st.session_state.client_profile.emotion_matrix = [
                        {"Эмоция": "Гнев (Anger)", "Триггер": "", "Внутреннее Ощущение": "", "Внешнее Проявление": "", "Якорная Фраза": ""},
                        {"Эмоция": "Страх (Fear)", "Триггер": "", "Внутреннее Ощущение": "", "Внешнее Проявление": "", "Якорная Фраза": ""},
                        {"Эмоция": "Радость (Joy)", "Триггер": "", "Внутреннее Ощущение": "", "Внешнее Проявление": "", "Якорная Фраза": ""},
                        {"Эмоция": "Грусть (Sadness)", "Триггер": "", "Внутреннее Ощущение": "", "Внешнее Проявление": "", "Якорная Фраза": ""},
                        {"Эмоция": "Удивление (Surprise)", "Триггер": "", "Внутреннее Ощущение": "", "Внешнее Проявление": "", "Якорная Фраза": ""},
                        {"Эмоция": "Отвращение (Disgust)", "Триггер": "", "Внутреннее Ощущение": "", "Внешнее Проявление": "", "Якорная Фраза": ""},
                        {"Эмоция": "Доверие (Trust)", "Триггер": "", "Внутреннее Ощущение": "", "Внешнее Проявление": "", "Якорная Фраза": ""},
                        {"Эмоция": "Предвкушение (Anticipation)", "Триггер": "", "Внутреннее Ощущение": "", "Внешнее Проявление": "", "Якорная Фраза": ""},
                    ]
                
                edited_emotions = st.data_editor(
                    st.session_state.client_profile.emotion_matrix,
                    num_rows="dynamic",
                    key="emotion_editor"
                )
                st.session_state.client_profile.emotion_matrix = edited_emotions

                # --- УЛУЧШЕНИЕ: Выделение "Пиковых Эмоций" ---
                st.markdown("##### Сигнатурные Эмоции Бренда")
                st.caption("Выберите 3 'пиковые' эмоции, которые станут ядром драматургии вашего образа.")
                emotion_options = [e["Эмоция"] for e in st.session_state.client_profile.emotion_matrix]
                selected_peak_emotions = st.multiselect("Выберите 3 пиковые эмоции:", emotion_options, default=st.session_state.client_profile.peak_emotions, max_selections=3)
                st.session_state.client_profile.peak_emotions = selected_peak_emotions

            # --- Модуль 2: Визуальная Идентичность ---
            with st.expander("Блок 2: Визуальная Идентичность (Стратегия Скрытого Влияния)"):
                st.markdown("Закодируйте ваш образ через цвета, стиль и визуальные якоря.")
                
                if not st.session_state.client_profile.visual_identity:
                    st.session_state.client_profile.visual_identity = {}
                
                vi = st.session_state.client_profile.visual_identity
                vi['base_palette'] = st.text_input("Базовая Палитра (2-3 нейтральных цвета)", vi.get('base_palette', "Черный, Серый, Темно-синий"))
                vi['accent_palette'] = st.text_input("Акцентная Палитра (1-2 ярких цвета)", vi.get('accent_palette', "Красный"))
                vi['visual_anchors'] = st.text_area("Аксессуары и Визуальные Якоря", vi.get('visual_anchors', "Очки определенной оправы\nЧасы (Скрытый Премиум)"))
                vi['clothing_style'] = st.selectbox("Предпочтительный Стиль Одежды", ["Business Casual", "Tech Minimalist", "Smart Casual", "Creative"], index=1)

                st.markdown("##### Коллекция «Луков»")
                st.caption("Ваша 'библиотека образов'. Выберите один из них в зависимости от задачи дня.")
                if 'look_collection' not in vi or not vi['look_collection']:
                    vi['look_collection'] = [
                        {"Название «Лука»": "ЭКСПЕРТ", "Позиционирование / Задача": "Трансляция авторитета, власти", "Ключевые Элементы": "Темно-синий блейзер, качественная футболка", "Акцент / Аксессуар": "Часы", "Когда Использовать": "Вебинары, B2B-переговоры"},
                        {"Название «Лука»": "ПРОВОКАТОР", "Позиционирование / Задача": "Трансляция энергии, 'пиковых эмоций'", "Ключевые Элементы": "Черная водолазка, кожаная куртка", "Акцент / Аксессуар": "Красный браслет", "Когда Использовать": "Конфликтный контент, шоу"},
                        {"Название «Лука»": "СВОЙ ПАРЕНЬ", "Позиционирование / Задача": "Трансляция эмпатии, аутентичности", "Ключевые Элементы": "Серая футболка, худи, джинсы", "Акцент / Аксессуар": "Отсутствие ярких акцентов", "Когда Использовать": "Лайфстайл-контент, сторис"},
                        {"Название «Лука»": "НАСТАВНИК", "Позиционирование / Задача": "Сочетание авторитета и эмпатии", "Ключевые Элементы": "Качественный свитер, светлая рубашка", "Акцент / Аксессуар": "Очки, блокнот", "Когда Использовать": "Обучающие лекции, разбор кейсов"},
                    ]
                
                edited_looks = st.data_editor(
                    vi['look_collection'],
                    num_rows="dynamic",
                    key="looks_editor"
                )
                vi['look_collection'] = edited_looks

            # --- Модуль 3: Вербальный Код ---
            with st.expander("Блок 3: Вербальный и Вокальный Код"):
                st.markdown("Определите ваш 'Голос Бренда'. Что и как вы говорите.")
                
                if not st.session_state.client_profile.verbal_code:
                    st.session_state.client_profile.verbal_code = {}

                vc = st.session_state.client_profile.verbal_code
                vc['anchor_phrases'] = st.text_input("Фразы-Якоря (через запятую)", ", ".join(vc.get('anchor_phrases', [])), key="vc_anchors")
                vc['communication_style'] = st.selectbox("Манера Общения", ["Таинственный", "Провокационный", "Дружелюбный", "Авторитетный", "Наставнический"], key="vc_style")
                vc['profanity_use'] = st.selectbox("Использование Мата", ["Нет", "Да", "В Исключениях"], key="vc_profanity")
                vc['forbidden_words'] = st.text_input("Слова-Паразиты (ЗАПРЕТ)", ", ".join(vc.get('forbidden_words', [])), key="vc_forbidden")
                vc['professional_jargon'] = st.text_area("Профессиональный Жаргон (термин: объяснение)", vc.get('professional_jargon', ""), key="vc_jargon")

                st.markdown("---")
                st.markdown("#### Тренажер: Бесконечный Монолог")
                st.caption("Нажмите на иконку микрофона, чтобы записать монолог на 1-3 минуты на любую тему. Затем прослушайте запись и проведите аудит своей речи.")

                # --- ИСПРАВЛЕНИЕ: Изолируем компонент в контейнер для стабильности ---
                with st.container():
                    wav_audio_data = st_audiorec()
                    if wav_audio_data is not None:
                        st.audio(wav_audio_data, format='audio/wav')
                        st.text_area("Аудит Слов-Паразитов (выпишите все, что заметили)", key="parasite_audit_area")

            # --- Модуль 4: Матрица Компетенций ---
            with st.expander("Блок 4: Матрица Компетенций"):
                st.markdown("Проведите инвентаризацию ваших активов и определите точки роста.")
                
                if not st.session_state.client_profile.competencies:
                    st.session_state.client_profile.competencies = {"superpowers": [], "growth_zones": []}

                comp = st.session_state.client_profile.competencies
                comp['superpowers'] = st.text_area("Мои «Суперсилы» (Инструменты Воздействия)", "\n".join(comp.get('superpowers', [])), key="comp_superpowers", help="Каждый навык с новой строки.")
                comp['growth_zones'] = st.text_area("Мои «Зоны Роста» (Над чем стоит поработать)", "\n".join(comp.get('growth_zones', [])), key="comp_growth", help="Каждый пункт с новой строки.")

                # Преобразуем текст обратно в списки
                st.session_state.client_profile.competencies['superpowers'] = [line.strip() for line in comp['superpowers'].split('\n') if line.strip()]
                st.session_state.client_profile.competencies['growth_zones'] = [line.strip() for line in comp['growth_zones'].split('\n') if line.strip()]

                # --- УЛУЧШЕНИЕ: Матрица Применения «Суперсил» ---
                st.markdown("---")
                st.markdown("#### Матрица Применения «Суперсил»")
                st.caption("Свяжите ваши навыки с конкретными целями, чтобы превратить их в работающие активы.")
                
                if 'superpower_application' not in st.session_state.client_profile or not st.session_state.client_profile.superpower_application:
                     st.session_state.client_profile.superpower_application = [
                         {"Инструмент / Суперсила": "", "Связанная Цель": "", "Механизм Помощи": ""},
                     ]

                edited_superpower_app = st.data_editor(
                    st.session_state.client_profile.superpower_application,
                    num_rows="dynamic",
                    key="superpower_app_editor",
                    use_container_width=True
                )
                st.session_state.client_profile.superpower_application = edited_superpower_app


        with tab_dashboard:
            st.subheader("Дашборд Проекта")

            if 'tasks' in st.session_state and st.session_state.tasks:
                tasks = st.session_state.tasks
                total_tasks = len(tasks)
                done_tasks = len([t for t in tasks if t.status == 'Done'])
                in_progress_tasks = len([t for t in tasks if t.status == 'In Progress'])
                todo_tasks = len([t for t in tasks if t.status == 'To Do'])
                overdue_tasks = len([t for t in tasks if t.deadline and t.deadline < date.today() and t.status != 'Done'])
                
                completion_percentage = done_tasks / total_tasks if total_tasks > 0 else 0

                st.markdown("#### Общий Прогресс")
                st.progress(completion_percentage)
                st.write(f"**Выполнено {done_tasks} из {total_tasks} задач ({completion_percentage:.0%})**")

                st.markdown("---")
                
                st.markdown("#### Ключевые Метрики")
                m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                with m_col1:
                    st.metric("✔️ Выполнено", done_tasks)
                with m_col2:
                    st.metric("⏳ В Работе", in_progress_tasks)
                with m_col3:
                    st.metric("📋 К Выполнению", todo_tasks)
                with m_col4:
                    st.metric("🔥 Просрочено", overdue_tasks, delta=overdue_tasks, delta_color="inverse")

                st.markdown("---")
                st.markdown("#### Распределение Задач")

                try:
                    import pandas as pd
                    
                    # График по статусам
                    status_data = pd.DataFrame({
                        'Статус': ['К Выполнению', 'В Работе', 'Выполнено'],
                        'Количество': [todo_tasks, in_progress_tasks, done_tasks]
                    })
                    st.bar_chart(status_data.set_index('Статус'))

                    # График по ответственным
                    if st.session_state.client_profile.team:
                        responsibles_data = pd.DataFrame([t.responsible for t in tasks if t.responsible], columns=['Ответственный'])
                        if not responsibles_data.empty:
                            st.write("#### Загрузка по исполнителям")
                            st.bar_chart(responsibles_data['Ответственный'].value_counts())

                except ImportError:
                    st.warning("Для отображения графиков необходимо установить библиотеку pandas: `pip install pandas`")
            else:
                st.info("Создайте план проекта на вкладке 'Задачи', чтобы увидеть статистику.")

        with tab_strategy: # Стратегия
            st.subheader("Отчет о Гармонии")
            report_text = st.session_state.client_profile.harmony_report.get("report_text", "Отчет не сгенерирован.")
            if "Конфликт" in report_text:
                st.warning(report_text)
                with st.expander("Что это значит?"):
                    st.info("""
                        **Это не проблема, а точка роста.** Обнаруженный конфликт — это скрытое противоречие между вашими целями и внутренними установками (вашими "врагами").
                        
                        Система подсвечивает его, чтобы вы могли превратить это противоречие в **уникальную стратегию**. Вместо того чтобы бороться с "врагом", мы используем его как топливо для достижения второй, более глобальной цели. Это основа для создания сильного, неконкурентного позиционирования.
                        """)
            else:
                st.success(report_text)
            
            st.markdown("---")
            st.subheader("🎬 Питч Флагманского Шоу")
            if st.session_state.client_profile.show_pitch:
                pitch = st.session_state.client_profile.show_pitch
                st.markdown(f"### {pitch.get('show_title', 'Название не сгенерировано')}")
                st.caption(pitch.get('concept', 'Концепция не сгенерирована.'))

                with st.expander("Драматургия (Круг Хармона)"):
                    dramaturgy = pitch.get('dramaturgy', {})
                    st.markdown(f"**1. ТЫ (Зритель):** {dramaturgy.get('step1_you', '...')}")
                    st.markdown(f"**2. ХОЧЕШЬ (Потребность):** {dramaturgy.get('step2_need', '...')}")
                    st.markdown(f"**3. ИДИ (Зов к приключениям):** {dramaturgy.get('step3_go', '...')}")
                    st.markdown(f"**4. ИЩИ (Испытания):** {dramaturgy.get('step4_search', '...')}")
                    st.markdown(f"**5. НАЙДИ (Откровение):** {dramaturgy.get('step5_find', '...')}")
                    st.markdown(f"**6. ЗАБЕРИ (Цена):** {dramaturgy.get('step6_take', '...')}")
                    st.markdown(f"**7. ВЕРНИСЬ (Возвращение):** {dramaturgy.get('step7_return', '...')}")
                    st.markdown(f"**8. ИЗМЕНИСЬ (Трансформация):** {dramaturgy.get('step8_changed', '...')}")

            st.markdown("---")
            st.subheader("📚 Библиотека Поддерживающих Форматов")
            if st.session_state.client_profile.formats:
                for i, format_item in enumerate(st.session_state.client_profile.formats):
                    with st.expander(f"Формат #{i+1}: {format_item.get('format_name', 'Без названия')}"):
                        st.markdown(f"**Идея:** {format_item.get('idea', '...')}")
                        st.markdown(f"**Носитель:** {format_item.get('content_carrier', '...')}")
                        st.markdown(f"**Тональность:** {format_item.get('format_tone', '...')}")
                        st.markdown(f"**Жанр:** {format_item.get('blog_genre', '...')}")
                        st.markdown(f"**Триггеры:** {', '.join(format_item.get('extras_triggers', []))}")

            st.markdown("---")
            st.subheader("🗺️ Стратегическая Карта")
            with st.expander("Зачем это нужно?"):
                st.info("Эта карта определяет, **что** делать и **для кого**. **Roadmap** — это последовательность ключевых действий для достижения ваших целей. **Карта Стейкхолдеров** — это 5 ключевых групп аудитории, с которыми нужно взаимодействовать на каждом этапе. Это ваш компас в мире контента и нетворкинга.")

            if st.session_state.client_profile.strategic_goals:
                strategy_data = st.session_state.client_profile.strategic_goals
                st.markdown("#### Дорожная Карта (Roadmap)")
                for item in strategy_data.get("roadmap", []):
                    st.checkbox(f"**Шаг {item['step']}: {item['title']}** - {item['description']} (Цель: {', '.join(item['target_groups'])})", key=f"roadmap_{item['step']}")

                with st.expander("👥 Карта Стейкхолдеров (5 Групп ЦА)"):
                    for group, description in strategy_data.get("audience_groups", {}).items():
                        st.markdown(f"**{group}**")
                        st.write(description)
            
            st.markdown("---")
            st.subheader("Матрица 4-х Действий")
            with st.expander("В чем суть этой матрицы?"):
                st.info("""
                    Это инструмент из "Стратегии Голубого Океана", который помогает отстроиться от конкурентов. Вместо того чтобы конкурировать "в лоб", мы анализируем, что в вашей нише можно:
                    - **Упразднить:** От каких общепринятых, но ненужных вещей можно отказаться?
                    - **Снизить:** Что можно делать меньше, чем конкуренты?
                    - **Повысить:** Какие важные для клиента вещи нужно усилить?
                    - **Создать:** Что абсолютно нового можно предложить рынку, чего не делает никто?
                    Ответы на эти вопросы формируют ваше уникальное позиционирование.
                    """)
            if st.session_state.client_profile.positioning_matrix:
                matrix = st.session_state.client_profile.positioning_matrix
                mat_col1, mat_col2 = st.columns(2)
                with mat_col1:
                    st.markdown("##### Упразднить")
                    st.write("\n".join(f"- {item}" for item in matrix.get("eliminate", ["-"])))
                    st.markdown("##### Повысить")
                    st.write("\n".join(f"- {item}" for item in matrix.get("raise", ["-"])))
                with mat_col2:
                    st.markdown("##### Снизить")
                    st.write("\n".join(f"- {item}" for item in matrix.get("reduce", ["-"])))
                    st.markdown("##### Создать")
                    st.write("\n".join(f"- {item}" for item in matrix.get("create", ["-"])))

            with st.expander("Показать итоговый Client_Profile_Hub (JSON)", expanded=False):
                st.json(asdict(st.session_state.client_profile))

        with tab_plan: # Контент-План
            st.subheader("🗓️ Автоматический Контент-План на Неделю")
            st.info("Это стратегический план, сгенерированный AI на основе вашего профиля, целей и форматов. Используйте его как основу для создания сценариев во вкладке 'Контент'.")

            if st.session_state.client_profile.content_plan:
                plan = st.session_state.client_profile.content_plan
                
                # --- УЛУЧШЕНИЕ: Интерактивный план с кнопками ---
                header_cols = st.columns((1, 4, 2, 2, 2, 2))
                headers = ["День", "Тема / Идея", "Формат", "ЦА", "Цель", "Действие"]
                for col, header in zip(header_cols, headers):
                    col.markdown(f"**{header}**")

                for i, item in enumerate(plan):
                    cols = st.columns((1, 4, 2, 2, 2, 2))
                    cols[0].write(item.get("day", "-"))
                    cols[1].write(item.get("theme", "-"))
                    cols[2].write(item.get("format_used", "-"))
                    cols[3].write(item.get("target_audience", "-"))
                    cols[4].write(item.get("goal", "-"))
                    if cols[5].button("🎬 Создать Сценарий", key=f"create_script_{i}"):
                        # Сохраняем данные для автозаполнения
                        st.session_state.prefill_data = {
                            "idea": item.get("theme", ""),
                            "format_name": item.get("format_used", "")
                        }
                        # Переключаемся на вкладку "Контент"
                        # Это хак для Streamlit, прямое переключение вкладок не поддерживается
                        # Мы просто перезапускаем приложение, а на вкладке "Контент" проверим prefill_data
                        st.rerun() 

            else:
                st.warning("Контент-план не был сгенерирован. Пожалуйста, перезапустите диагностику.")

        with tab_products: # Продукты
            if st.session_state.product_ladder:
                st.subheader("💰 Лестница Ценности Продукта (ПТУ)")
                with st.expander("Почему именно такая продуктовая линейка?"):
                    st.info("""
                        "Продуктово-Тактическое Устройство" (ПТУ) проектирует линейку продуктов, которая решает две задачи: **максимизирует прибыль** и **снижает ваше выгорание**.
                        - **Lead Magnet** привлекает внимание.
                        - **Tripwire** превращает подписчика в клиента с минимальным стрессом.
                        - **Core Offer** генерирует основной доход.
                        - **High-Ticket** работает с самыми лояльными клиентами, принося максимальную ценность и вам, и им.
                        Эта система позволяет вам работать меньше, а зарабатывать больше, концентрируясь на создании ценности, а не на постоянных продажах.
                        """)
                with st.expander("💰 Редактировать Лестницу Ценности Продукта (ПТУ)", expanded=True):
                    ladder = st.session_state.product_ladder
                    with st.form(key='pvl_edit_form'):
                        # ... (код формы редактирования ПТУ остается без изменений)
                        st.markdown("#### Lead Magnet (Бесплатник)")
                        lm_name = st.text_input("Название Lead Magnet", value=ladder.lead_magnet.name if ladder.lead_magnet else "")
                        lm_purpose = st.text_input("Цель Lead Magnet", value=ladder.lead_magnet.purpose if ladder.lead_magnet else "")
                        st.markdown("#### Tripwire (Трипвайер)")
                        tw_name = st.text_input("Название Tripwire", value=ladder.tripwire.name if ladder.tripwire else "")
                        tw_price = st.number_input("Цена Tripwire", value=ladder.tripwire.price if ladder.tripwire else 0.0, format="%.2f")
                        tw_purpose = st.text_input("Цель Tripwire", value=ladder.tripwire.purpose if ladder.tripwire else "")
                        st.markdown("#### Core Offer (Основной Продукт)")
                        co_name = st.text_input("Название Core Offer", value=ladder.core_offer.name if ladder.core_offer else "")
                        co_price = st.number_input("Цена Core Offer", value=ladder.core_offer.price if ladder.core_offer else 0.0, format="%.2f")
                        co_purpose = st.text_input("Цель Core Offer", value=ladder.core_offer.purpose if ladder.core_offer else "")
                        st.markdown("#### High-Ticket (Флагман)")
                        ht_name = st.text_input("Название High-Ticket", value=ladder.high_ticket.name if ladder.high_ticket else "")
                        ht_price = st.number_input("Цена High-Ticket", value=ladder.high_ticket.price if ladder.high_ticket else 0.0, format="%.2f")
                        ht_purpose = st.text_input("Цель High-Ticket", value=ladder.high_ticket.purpose if ladder.high_ticket else "")
                        pvl_submitted = st.form_submit_button("💾 Сохранить продуктовую линейку")
                        if pvl_submitted:
                            if ladder.lead_magnet: ladder.lead_magnet.name, ladder.lead_magnet.purpose = lm_name, lm_purpose
                            if ladder.tripwire: ladder.tripwire.name, ladder.tripwire.price, ladder.tripwire.purpose = tw_name, tw_price, tw_purpose
                            if ladder.core_offer: ladder.core_offer.name, ladder.core_offer.price, ladder.core_offer.purpose = co_name, co_price, co_purpose
                            if ladder.high_ticket: ladder.high_ticket.name, ladder.high_ticket.price, ladder.high_ticket.purpose = ht_name, ht_price, ht_purpose
                            st.session_state.client_profile.products = [asdict(p) for p in [ladder.lead_magnet, ladder.tripwire, ladder.core_offer, ladder.high_ticket] if p and p.name]
                            st.success("Лестница Ценности Продукта успешно обновлена!")

                st.markdown("---")
                st.subheader("🧮 Декомпозиция Воронки Продаж")
                # ... (код калькулятора декомпозиции остается без изменений)
                ladder = st.session_state.product_ladder
                target_revenue = st.number_input("Желаемый Доход (в месяц)", min_value=0, value=10000)
                traffic = st.number_input("Трафик (посетители в мес.)", min_value=0, value=5000)
                st.markdown("---")
                c1 = st.slider("Конверсия в лиды (C1, %)", 0, 100, 20) / 100.0
                c2 = st.slider("Конверсия в покупатели трипвайера (C2, %)", 0, 100, 5) / 100.0
                c3 = st.slider("Конверсия в покупатели Core Offer (C3, %)", 0, 100, 20) / 100.0
                leads = traffic * c1
                tripwire_buyers = leads * c2
                core_offer_buyers = tripwire_buyers * c3
                tripwire_revenue = tripwire_buyers * (ladder.tripwire.price if ladder.tripwire else 0)
                core_offer_revenue = core_offer_buyers * (ladder.core_offer.price if ladder.core_offer else 0)
                total_revenue = tripwire_revenue + core_offer_revenue
                st.markdown("---")
                st.subheader("Прогноз Результатов")
                res_col1, res_col2, res_col3 = st.columns(3) 
                with res_col1: st.metric("Лиды", f"{int(leads):,}")
                with res_col2: st.metric("Покупатели (Core Offer)", f"{int(core_offer_buyers):,}")
                with res_col3: st.metric(label="Прогнозируемый Доход", value=f"${int(total_revenue):,}", delta=f"${int(total_revenue - target_revenue):,}")
                st.progress(min(total_revenue / target_revenue, 1.0))
                st.write(f"Достижение цели: {total_revenue / target_revenue:.1%}")
                with st.expander("Показать детальный расчет"):
                    st.write(f"Посетители: {int(traffic):,}")
                    st.write(f"Лиды (C1 = {c1:.1%}): {int(leads):,}")
                    st.write(f"Покупатели Трипвайера (C2 = {c2:.1%}): {int(tripwire_buyers):,}")
                    st.write(f"Доход с Трипвайера: ${int(tripwire_revenue):,}")
                    st.write(f"Покупатели Core Offer (C3 = {c3:.1%}): {int(core_offer_buyers):,}")
                    st.write(f"Доход с Core Offer: ${int(core_offer_revenue):,}")
                    st.write(f"**Итоговый доход:** **${int(total_revenue):,}**")

        with tab_content: # Контент
            with st.form("scenario_constructor_form"):
                st.subheader("🛠️ Конструктор Сценариев")

                # --- УЛУЧШЕНИЕ: ВЫБОР ИЗ БИБЛИОТЕКИ ФОРМАТОВ ---
                # Проверяем, есть ли данные для автозаполнения из контент-плана
                prefill_data = st.session_state.get('prefill_data', None)
                
                format_names = ["(Создать с нуля)"] + [f.get('format_name', f'Формат #{i+1}') for i, f in enumerate(st.session_state.client_profile.formats or [])]
                
                # Устанавливаем значение по умолчанию для selectbox
                default_format_index = 0
                if prefill_data and prefill_data.get("format_name") in format_names:
                    default_format_index = format_names.index(prefill_data.get("format_name"))

                selected_format_name = st.selectbox("Выберите формат из вашей библиотеки (опционально):", format_names, index=default_format_index)

                # Автозаполнение полей на основе выбранного формата
                default_values = {}
                if selected_format_name != "(Создать с нуля)":
                    selected_format = next((f for f in (st.session_state.client_profile.formats or []) if f.get('format_name') == selected_format_name), None)
                    if selected_format:
                        default_values = {
                            "idea": selected_format.get('idea', ''),
                            "content_carrier": selected_format.get('content_carrier', ANCHOR_POINTS_DATA["content_carriers"][0]),
                        }
                
                st.markdown("---")
                idea = st.text_input("1. Идея (О чём?)", value=default_values.get("idea", ""), placeholder="Например: Преодоление творческого ступора")
                content_carrier = st.selectbox("2. Контент-носитель", ANCHOR_POINTS_DATA["content_carriers"], index=ANCHOR_POINTS_DATA["content_carriers"].index(default_values["content_carrier"]) if "content_carrier" in default_values else 0)
                format_tone = st.selectbox("3. Формат-тональность", ANCHOR_POINTS_DATA["formats"])
                # ... (остальные поля конструктора)
                blog_genre = st.selectbox("4. Жанр Блога (Видеоформат)", ANCHOR_POINTS_DATA["blog_genres"])
                extras_triggers = st.multiselect("5. Допы/Триггеры (можно несколько)", ANCHOR_POINTS_DATA["extras_triggers"])
                movie_genre = st.selectbox("6. Жанр Кино (Атмосфера)", ANCHOR_POINTS_DATA["movie_genres"])
                tv_genre = st.selectbox("7. ТВ Жанр (Структура выпуска)", ANCHOR_POINTS_DATA["tv_genres"])
                
                # Улучшение: Автозаполнение поля "Персонаж"
                character_default = st.session_state.client_profile.brand_name if st.session_state.client_profile else ""
                character = st.text_input("8. Персонаж/Ниша", value=character_default)
                
                # Очищаем данные для автозаполнения после использования
                if 'prefill_data' in st.session_state:
                    del st.session_state['prefill_data']

                product_names = ["(Нет продукта)"] + [p['name'] for p in (st.session_state.client_profile.products or [])]
                selected_product_name = st.selectbox("Выберите продукт для продвижения (опционально):", product_names)
                submitted = st.form_submit_button("🎬 Сгенерировать Сценарий")
                if submitted:
                    with st.spinner("Создаю магию по 8 точкам..."):
                        # Получаем scenario_producer из состояния сессии
                        scenario_producer = st.session_state.get('scenario_producer')
                        if not scenario_producer:
                            st.error("Ошибка: генератор сценариев не инициализирован. Пожалуйста, запустите диагностику заново.")
                            st.stop()
                        product_to_promote = None
                        if selected_product_name != "(Нет продукта)" and st.session_state.product_ladder:
                            all_products = [st.session_state.product_ladder.lead_magnet, st.session_state.product_ladder.tripwire, st.session_state.product_ladder.core_offer, st.session_state.product_ladder.high_ticket]
                            product_to_promote = next((p for p in all_products if p and p.name == selected_product_name), None)
                        selected_points = {
                            "idea": idea, "content_carrier": content_carrier, "format": format_tone,
                            "blog_genre": blog_genre, "extras_triggers": extras_triggers,
                            "movie_genre": movie_genre, "tv_genre": tv_genre, "character": character
                        }
                        script = scenario_producer.process(st.session_state.client_profile, selected_points, product_to_promote)
                    if script:
                        # Сохраняем content_carrier для декомпозиции
                        script["content_carrier_ref"] = content_carrier
                        # Добавляем в историю и делаем текущим
                        st.session_state.script_history.append(script)
                        st.session_state.current_script = script
                    else:
                        st.error("Не удалось сгенерировать сценарий. Проверьте API ключ или попробуйте еще раз.")

            if st.session_state.current_script:
                script_data = st.session_state.current_script
                st.subheader(f"Сценарий: «{script_data.get('title', 'Без названия')}»")
                st.markdown("##### ⚡️ 1. ШОК (0.5с)"); st.info(script_data.get('shock', ''))
                st.markdown("##### 🎣 2. ХУК (3с)"); st.info(script_data.get('hook', ''))
                st.markdown("##### 📦 3. КОНТЕНТ (15с)"); st.info(script_data.get('content', ''))
                st.markdown("##### 4. CTA (Призыв к действию)"); st.success(script_data.get('cta', ''))

        with tab_tasks: # Задачи
            st.subheader("Декомпозиция в Задачи")

            # --- НОВЫЙ БЛОК: ВЫБОР СЦЕНАРИЯ ДЛЯ ДЕКОМПОЗИЦИИ ---
            if st.session_state.script_history:
                history_options = {f"Сценарий #{i+1}: {s.get('title', 'Без названия')}": i for i, s in enumerate(st.session_state.script_history)}
                selected_script_title = st.selectbox("Выберите сценарий для создания плана:", options=history_options.keys())
                
                # Обновляем текущий сценарий для декомпозиции
                selected_script_index = history_options[selected_script_title]
                script_to_decompose = st.session_state.script_history[selected_script_index]

                if st.button("📅 Создать План Проекта"):
                    try:
                        with st.spinner("Планирую задачи..."):
                            calendar_engine = st.session_state.get('calendar_engine')
                            if not calendar_engine:
                                st.error("Ошибка: календарный движок не инициализирован. Пожалуйста, запустите диагностику заново.")
                                st.stop()

                            # Ищем оригинальные "8 точек" для этого сценария
                            original_anchor_points = st.session_state.script_history[selected_script_index].get('anchor_points_ref', {})
                            
                            tasks = calendar_engine.decompose_script_to_tasks(script_to_decompose, original_anchor_points)
                            st.session_state.tasks = tasks
                            if tasks:
                                st.success(f"AI сгенерировал {len(tasks)} задач для проекта!")
                    except Exception as e:
                        st.error(f"Произошла ошибка при создании плана: {e}")
            else:
                st.warning("Сначала сгенерируйте сценарий во вкладке 'Контент'.")

            if 'tasks' in st.session_state and st.session_state.tasks:
                st.markdown("---")
                st.subheader("Канбан-доска")
                # ... (код Канбан-доски остается без изменений)
                if 'editing_task_index' not in st.session_state:
                    st.session_state.editing_task_index = None
                def display_task(task, index):
                    # Список ответственных теперь формируется из командного модуля
                    team_members = st.session_state.client_profile.team
                    if team_members:
                        responsibles = [""] + [member.name for member in team_members]
                    else:
                        responsibles = [""]
                    
                    # --- ИСПРАВЛЕНИЕ ОШИБКИ: Блоки комментариев и файлов перенесены сюда ---
                    with st.expander(f"💬 Комментарии ({len(task.comments)})"):
                        for comment in task.comments:
                            st.markdown(f"**{comment.author}:** {comment.text}")
                        
                        comment_text = st.text_input("Добавить комментарий:", key=f"comment_{index}", label_visibility="collapsed", placeholder="Ваш комментарий...")
                        if st.button("Отправить", key=f"send_comment_{index}"):
                            if comment_text:
                                # В реальном приложении автора нужно брать из сессии пользователя
                                author_name = "Я" 
                                new_comment = Comment(author=author_name, text=comment_text) # type: ignore
                                st.session_state.tasks[index].comments.append(new_comment) # Ошибка здесь, исправим
                                st.rerun()

                    with st.expander(f"📎 Файлы ({len(task.attachments)})", expanded=False):
                        for att_index, attachment in enumerate(task.attachments):
                            st.download_button(
                                label=f"📄 {attachment.file_name}",
                                data=attachment.file_data,
                                file_name=attachment.file_name,
                                key=f"download_{index}_{att_index}"
                            )
                        
                        uploaded_files = st.file_uploader("Прикрепить файлы", accept_multiple_files=True, key=f"uploader_{index}", label_visibility="collapsed")
                        if uploaded_files:
                            for uploaded_file in uploaded_files:
                                new_attachment = Attachment(file_name=uploaded_file.name, file_data=uploaded_file.getvalue())
                                st.session_state.tasks[index].attachments.append(new_attachment)
                            st.rerun()
                    # --- КОНЕЦ ИСПРАВЛЕНИЯ ---

                    if task.status == "To Do":
                        if st.button("В работу →", key=f"move_{index}"):
                            st.session_state.tasks[index].status = "In Progress"
                            st.rerun()
                    elif task.status == "In Progress":
                        if st.button("✓ Завершить", key=f"move_{index}"):
                            st.session_state.tasks[index].status = "Done"
                            st.rerun()

                    if st.session_state.editing_task_index == index:
                        new_description = st.text_area("Редактировать:", value=task.description, key=f"edit_area_{index}")
                        if st.button("Сохранить", key=f"save_{index}"):
                            st.session_state.tasks[index].description = new_description
                            st.session_state.editing_task_index = None
                            st.rerun()

                    else:
                        col_desc, col_actions = st.columns([3, 1])
                        with col_desc: st.markdown(f"> {task.description}")
                        
                        # Отображение дедлайна
                        today = date.today()
                        if task.deadline:
                            delta = (task.deadline - today).days
                            if delta < 0 and task.status != "Done":
                                st.caption(f"🔥 Дедлайн: {task.deadline.strftime('%d.%m.%Y')} (Просрочено на {-delta} д.)")
                            else:
                                st.caption(f"🗓️ Дедлайн: {task.deadline.strftime('%d.%m.%Y')}")


                        with col_actions:
                            # Выбор ответственного
                            responsible = st.selectbox("Ответственный", responsibles, key=f"responsible_{index}", index=responsibles.index(task.responsible) if task.responsible in responsibles else 0)
                            st.session_state.tasks[index].responsible = responsible


                            # Установка дедлайна
                            priorities = ["Низкий", "Средний", "Высокий"]
                            new_deadline = st.date_input("Дедлайн", value=task.deadline, key=f"deadline_{index}") # type: ignore
                            st.session_state.tasks[index].deadline = new_deadline
                            if st.button("✏️", key=f"edit_{index}"):
                                st.session_state.editing_task_index = index
                                st.rerun()
                            if st.button("🗑️", key=f"delete_{index}"):
                                del st.session_state.tasks[index]
                                st.rerun()
                todo_col, in_progress_col, done_col = st.columns(3) 
                
                with todo_col:
                    st.subheader("To Do") 
                    for i, task in enumerate(st.session_state.tasks):
                        if task.status == "To Do": 
                            with st.container(border=True):
                                display_task(task, i)
                with in_progress_col:
                    st.subheader("In Progress")
                    for i, task in enumerate(st.session_state.tasks):
                        if task.status == "In Progress": display_task(task, i)
                with done_col:
                    st.subheader("Done")
                    for i, task in enumerate(st.session_state.tasks):
                        if task.status == "Done": 
                            with st.container(border=True):
                                st.markdown(f"✅ ~~_{task.description}_~~")
                
                # --- НОВЫЙ БЛОК: ЭКСПОРТ В CSV ---
                st.markdown("---")
                st.subheader("Экспорт Плана")
                
                try:
                    import pandas as pd
                    
                    tasks_data = [{
                        "Задача": task.description,
                        "Статус": task.status,
                        "Ответственный": task.responsible,
                        "Дедлайн": task.deadline.strftime('%Y-%m-%d') if task.deadline else ""
                    } for task in st.session_state.tasks]
                    
                    df = pd.DataFrame(tasks_data)
                    csv = df.to_csv(index=False).encode('utf-8')
                    
                    st.download_button("📥 Экспортировать План в CSV", csv, "corepath_project_plan.csv", "text/csv")
                except ImportError:
                    st.warning("Для экспорта в CSV необходимо установить библиотеку pandas: `pip install pandas`")

        with tab_capital: # Медийный Капитал
            st.subheader("🏆 Медийный Капитал (Аудит Репутации)")
            st.info("Ваша репутация — это актив для работы с партнерами, инвесторами и ключевыми фигурами (ЦА 3-5). Здесь мы проводим его инвентаризацию.")

            # --- Модуль 6.1: Инвентаризация Медийного Веса ---
            with st.expander("Блок 6.1: Инвентаризация Медийного Веса", expanded=True):
                st.markdown("#### Формальные Регалии (Фундамент)")
                st.session_state.client_profile.formal_regalia = st.text_area(
                    "Образование, награды, звания, официальные титулы.",
                    "\n".join(st.session_state.client_profile.formal_regalia),
                    key="formal_regalia_input", help="Каждая регалия с новой строки."
                ).splitlines() # type: ignore

                st.markdown("#### Социальный Капитал (Сеть)")
                st.session_state.client_profile.social_capital = st.text_area(
                    "Список известных людей/брендов, с которыми вы работали или которые вас упоминают.",
                    "\n".join(st.session_state.client_profile.social_capital),
                    key="social_capital_input", help="Каждый пункт с новой строки."
                ).splitlines() # type: ignore

                st.markdown("#### «Живые Регалии» (Портфель Активов)")
                st.caption("Ваши измеримые достижения: кейсы, отзывы, упоминания в СМИ, выступления. Добавляются через форму ниже.")
            
            # --- Модуль 6.2: Протокол «Аудита Прошлого» ---
            with st.expander("Блок 6.2: Протокол «Аудита Прошлого» (Конфиденциально)"):
                st.warning("Будьте абсолютно честны с собой. То, что мы знаем, мы можем контролировать.")
                
                if not st.session_state.client_profile.reputational_risks:
                    st.session_state.client_profile.reputational_risks = [
                        {"Риск": "Были ли у вас публичные конфликты?", "Есть": False, "Описание/Контр-аргумент": ""},
                        {"Риск": "Существуют ли «неудобные» фото или видео из прошлого?", "Есть": False, "Описание/Контр-аргумент": ""},
                        {"Риск": "Были ли у вас проблемы с законом или финансовые споры?", "Есть": False, "Описание/Кон-аргумент": ""},
                        {"Риск": "Высказывали ли вы ранее мнения, противоречащие образу?", "Есть": False, "Описание/Контр-аргумент": ""},
                        {"Риск": "Есть ли люди, которые могут иметь на вас «зуб»?", "Есть": False, "Описание/Контр-аргумент": ""},
                    ]
                
                edited_risks = st.data_editor(st.session_state.client_profile.reputational_risks, key="risks_editor")
                st.session_state.client_profile.reputational_risks = edited_risks

            st.markdown("---")
            st.subheader("💼 Управление Портфелем Активов")
            with st.expander("➕ Добавить новый актив влияния"):
                with st.form("influence_asset_form", clear_on_submit=True):
                    asset_type = st.selectbox("Тип актива", ["Отзыв", "Кейс", "Упоминание в СМИ", "Выступление"])
                    asset_title = st.text_input("Заголовок актива", placeholder="Например: 'Отзыв от клиента X о курсе'")
                    uploaded_image = st.file_uploader("Загрузить изображение (опционально)", type=["png", "jpg", "jpeg"])
                    asset_description = st.text_area("Описание / Текст актива", placeholder="Вставьте сюда текст отзыва, описание кейса или ссылку на публикацию.")
                    asset_submitted = st.form_submit_button("Добавить в капитал")
                    if asset_submitted:
                        if asset_title and asset_description:
                            image_data = None
                            if uploaded_image is not None:
                                image_data = uploaded_image.getvalue()
                            
                            new_asset = InfluenceAsset(title=asset_title, asset_type=asset_type, description=asset_description, image_bytes=image_data)
                            st.session_state.client_profile.influence_capital.append(new_asset)
                            st.success(f"Актив «{asset_title}» успешно добавлен!")
                        else:
                            st.error("Заголовок и описание актива не могут быть пустыми.")

            if st.session_state.client_profile.influence_capital:
                for asset in reversed(st.session_state.client_profile.influence_capital):
                    with st.container(border=True):
                        st.markdown(f"**{asset.title}**")
                        if asset.image_bytes:
                            st.image(asset.image_bytes, width=300)
                        st.caption(f"Тип: {asset.asset_type}")
                        st.write(asset.description)
            else:
                st.info("В вашем портфеле пока нет активов. Добавьте первый, используя форму выше.")

        with tab_team: # Команда
            st.subheader("Командный Модуль")

            with st.expander("➕ Добавить нового члена команды"):
                with st.form("team_member_form", clear_on_submit=True):
                    member_name = st.text_input("Имя члена команды")
                    member_role = st.text_input("Роль в проекте", placeholder="Например: Сценарист, Монтажер")
                    
                    member_submitted = st.form_submit_button("Добавить в команду")
                    if member_submitted:
                        if member_name and member_role:
                            new_member = TeamMember(name=member_name, role=member_role)
                            st.session_state.client_profile.team.append(new_member)
                            st.success(f"Участник «{member_name}» добавлен в команду!")
                            st.rerun()
                        else:
                            st.error("Имя и роль не могут быть пустыми.")
            
            st.subheader("Состав команды")
            if st.session_state.client_profile.team:
                for i, member in enumerate(st.session_state.client_profile.team):
                    col_name, col_role, col_action = st.columns([2, 2, 1])
                    col_name.write(member.name)
                    col_role.write(member.role)
                    if col_action.button("🗑️ Удалить", key=f"del_member_{i}"):
                        st.session_state.client_profile.team.pop(i)
                        st.rerun()
            else:
                st.info("В вашей команде пока нет участников.")

        with tab_synergy:
            st.subheader("🤝 Модуль «Синергия»")
            st.info("Найдите точки для взаимовыгодных коллабораций между вашими клиентами. Загрузите 2 или более файла профиля (`.json`) для анализа.")

            uploaded_profiles = st.file_uploader(
                "Загрузите профили клиентов для анализа", 
                type=["json"], 
                accept_multiple_files=True,
                key="synergy_uploader"
            )

            if st.button("🚀 Найти Синергию", disabled=(not uploaded_profiles or len(uploaded_profiles) < 2)):
                profiles_to_analyze = []
                for file in uploaded_profiles:
                    try:
                        data = json.load(file)
                        profiles_to_analyze.append(ClientProfileHub(**data))
                    except Exception as e:
                        st.error(f"Не удалось прочитать файл {file.name}: {e}")
                
                if len(profiles_to_analyze) >= 2:
                    with st.spinner("Анализирую профили и ищу точки соприкосновения..."):
                        synergy_engine = SynergyEngine(api_key=st.session_state.api_key_input)
                        synergy_pitch = synergy_engine.process(profiles_to_analyze)
                        if synergy_pitch:
                            st.success("Найдена потенциальная коллаборация!")
                            st.json(synergy_pitch)
