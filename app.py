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

def run_full_diagnostic():
    """Основная функция, запускающая весь конвейер анализа."""
    st.session_state.processing = True
    st.rerun()

def render_startup_screen():
    """Отрисовывает стартовый экран, если профиль не создан."""
    with st.expander("🚀 Диагностика", expanded=True):
        api_key = st.text_input("🔑 Ваш Gemini API Ключ", type="password", help="Ваш ключ будет использован только для этой сессии и нигде не сохраняется.", key="api_key_input", disabled=st.session_state.processing)
        input_mode_tab1, input_mode_tab2 = st.tabs(["Интерактивный Опрос", "Быстрый Ввод (для опытных)"])

        with input_mode_tab1:
            st.markdown("Отвечайте на вопросы в диалоге с AI-ассистентом для максимальной глубины.")
            all_questions = [(k, v) for block in QUESTIONNAIRE_QUESTIONS.values() for k, v in block.items()]
            
            if st.session_state.current_q_index < len(all_questions):
                q_key, q_text = all_questions[st.session_state.current_q_index]
                st.subheader(f"Вопрос {st.session_state.current_q_index + 1} / {len(all_questions)}")
                st.markdown(f"**{q_text}**")

                for speaker, text in st.session_state.current_conversation:
                    st.chat_message(speaker).write(text)

                user_answer = st.text_area("Ваш ответ:", key=f"interview_input_{q_key}", height=150, disabled=st.session_state.processing)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💬 Ответить", key=f"submit_{q_key}", disabled=st.session_state.processing, use_container_width=True):
                        if user_answer:
                            st.session_state.current_conversation.append(("user", user_answer))
                            interview_engine = InterviewEngine(api_key=st.session_state.api_key_input)
                            conversation_str = "\n".join([f"{s}: {t}" for s, t in st.session_state.current_conversation])
                            follow_up = interview_engine.get_follow_up_question(q_text, conversation_str)
                            if follow_up:
                                st.session_state.current_conversation.append(("ai", follow_up))
                            st.rerun()
                with col2:
                    if st.button("✅ Завершить и перейти к следующему", type="primary", disabled=st.session_state.processing, use_container_width=True):
                        final_answer_text = "\n".join([f"{s.capitalize()}: {t}" for s, t in st.session_state.current_conversation])
                        st.session_state.interview_answers[q_key] = final_answer_text
                        st.session_state.current_conversation = []
                        st.session_state.current_q_index += 1
                        st.rerun()
            else:
                st.success("🎉 Опрос завершен! Все ответы собраны.")
                st.info("Теперь вы можете запустить полную диагностику.")

            if st.button("🚀 Запустить Диагностику по ответам", disabled=(st.session_state.current_q_index < len(all_questions) or st.session_state.processing), on_click=run_full_diagnostic, type="primary"):
                # Логика запуска перенесена в on_click
                pass

        with input_mode_tab2:
            st.session_state.raw_text = st.text_area("Шаг 1: Вставьте Единый Контекст", height=250, key="raw_text_area", placeholder="Вставьте сюда весь текст из опросника...", disabled=st.session_state.processing)
            if st.button("🚀 Запустить Диагностику и Проектирование", disabled=st.session_state.processing, on_click=run_full_diagnostic):
                # Логика запуска перенесена в on_click
                pass

    uploaded_file = st.file_uploader("...или загрузите существующий профиль", type=["json"], disabled=st.session_state.processing)
    if uploaded_file is not None:
        # ... (логика загрузки)
        pass

def render_processing_overlay():
    """Отрисовывает оверлей во время анализа."""
    _, mid_col, _ = st.columns([1, 2, 1])
    with mid_col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center;'>Идет глубокий анализ...</h2>", unsafe_allow_html=True)
            st.info("Пожалуйста, подождите. Система F.O.K.I.N. обрабатывает ваши данные. Это может занять несколько минут.")
            
            with st.status("Запускаю полный цикл диагностики...", expanded=True) as status:
                try:
                    # 1. Подготовка текста
                    if not st.session_state.raw_text:
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

                    # 3. Основной конвейер
                    status.write("Шаг 1/7: 🚀 **Движок Поглощения.** Извлекаю ваше ценностное ядро, цели и 'врагов' из ответов, чтобы сформировать основу вашего цифрового ДНК.")
                    profile = ingestion_engine.process(st.session_state.raw_text)
                    if not profile: raise ValueError("Не удалось создать профиль.")

                    status.write("Шаг 2/7: 🌊 **Движок Голубого Океана.** Анализирую конкурентов, чтобы найти свободную нишу и создать уникальное позиционирование, которое выведет вас из 'алого океана' прямой борьбы.")
                    profile.positioning_matrix = blue_ocean_engine.process(st.session_state.raw_text, profile)

                    status.write("Шаг 3/7: 🗺️ **Движок Стратегии.** Проектирую долгосрочную дорожную карту и определяю 5 ключевых групп аудитории (стейкхолдеров), чтобы ваши действия были не хаотичными, а системными.")
                    profile.strategic_goals = strategy_engine.process(profile)

                    status.write("Шаг 4/7: 💰 **Движок Коммерции.** Создаю продуктовую линейку (ПТУ), которая позволит эффективно монетизировать вашу экспертность и снизить риск выгорания.")
                    product_ladder = commerce_engine.process(profile)

                    status.write("Шаг 5/7: 🧘‍♂️ **Движок Гармонии.** Выявляю скрытые конфликты между вашими целями и внутренними установками, чтобы превратить их из слабости в уникальную 'Стратегию Баланса'.")
                    profile = harmony_engine.process(profile)

                    status.write("Шаг 6/7: 🎬 **Движок Драматургии.** Проектирую концепцию вашего флагманского шоу, которое станет ядром вашего контент-маркетинга и будет работать на вашу миссию.")
                    profile.show_pitch = show_pitch_engine.process(profile)

                    status.write("Шаг 7/7: 📚 **Движок Форматов и Плана.** Создаю библиотеку поддерживающего контента и генерирую готовый план на неделю, чтобы вы точно знали, что и когда публиковать.")
                    profile.formats = format_engine.process(profile)
                    profile.content_plan = content_plan_engine.process(profile)

                    status.update(label="✅ Диагностика завершена! Сохраняю результаты...", state="complete", expanded=False)

                    # 4. Сохранение результатов
                    st.session_state.client_profile = profile
                    st.session_state.scenario_producer = AIScenarioProducer(api_key=api_key)
                    st.session_state.calendar_engine = CalendarEngine(api_key=api_key)
                    if product_ladder:
                        st.session_state.client_profile.products = [asdict(p) for p in [product_ladder.lead_magnet, product_ladder.tripwire, product_ladder.core_offer, product_ladder.high_ticket] if p]
                        st.session_state.product_ladder = product_ladder
                    
                    st.session_state.profile_generated = True
                    st.session_state.processing = False
                    st.rerun()

                except Exception as e:
                    st.session_state.processing = False
                    status.update(label=f"Ошибка на этапе диагностики: {e}", state="error")
                    st.error(f"Произошла ошибка: {e}")
                    st.button("Попробовать снова") # Позволяет пользователю сбросить состояние ошибки

def render_main_workspace():
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
        
# --- ГЛАВНЫЙ РОУТЕР ПРИЛОЖЕНИЯ ---
if st.session_state.processing:
    render_processing_overlay()
elif not st.session_state.profile_generated:
    render_startup_screen()
else:
    render_main_workspace()
