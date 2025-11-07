# /Users/valentinfokin/Desktop/CorePath OS 2.0/app.py
import streamlit as st
import json
from dataclasses import asdict
import requests
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
from st_audiorec import st_audiorec # Убедитесь, что этот пакет установлен: pip install streamlit-audiorec
from st_pages import Page

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
if 'offline_mode' not in st.session_state:
    st.session_state.offline_mode = True
if 'producer_view' not in st.session_state:
    st.session_state.producer_view = False
# --- НОВЫЙ БЛОК: Состояние для аутентификации ---
if 'token' not in st.session_state:
    st.session_state.token = None
if 'error_message' not in st.session_state:
    st.session_state.error_message = None
if 'products' not in st.session_state:
    st.session_state.products = []
if 'selected_product_id' not in st.session_state:
    st.session_state.selected_product_id = None
if 'team_members' not in st.session_state:
    st.session_state.team_members = []
if 'influence_assets' not in st.session_state:
    st.session_state.influence_assets = []
if 'strategic_step' not in st.session_state:
    st.session_state.strategic_step = 0 # 0 - не начато, 1-11 - шаги, 99 - завершено
if 'wizard_complete' not in st.session_state:
    st.session_state.wizard_complete = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'channels' not in st.session_state:
    st.session_state.channels = []
if 'selected_channel_id' not in st.session_state:
    st.session_state.selected_channel_id = None
if 'producer_tasks' not in st.session_state:
    st.session_state.producer_tasks = []

def run_offline_processing(status):
    """
    Выполняет весь цикл диагностики в оффлайн-режиме, используя мок-данные.
    """
    # Инициализация движков
    ingestion_engine = IngestionEngine(offline_mode=True)
    blue_ocean_engine = BlueOceanEngine(offline_mode=True)
    strategy_engine = StrategyEngine(offline_mode=True)
    commerce_engine = CommerceEngine(offline_mode=True)
    harmony_engine = HarmonyDiagnosticEngine()
    show_pitch_engine = ShowPitchEngine(offline_mode=True)
    format_engine = FormatEngine(offline_mode=True)
    content_plan_engine = ContentPlanEngine(offline_mode=True)

    # Шаг 1: Поглощение и создание базового профиля
    status.write("🚀 Запуск Движка Поглощения...")
    client_profile = ingestion_engine.process(st.session_state.raw_text)
    if not client_profile:
        raise ValueError("Не удалось создать профиль в оффлайн-режиме.")

    # Шаг 2: Матрица 4-х Действий (Blue Ocean)
    status.write("🌊 Запуск Движка Голубого Океана...")
    client_profile.positioning_matrix = blue_ocean_engine.process("Текст про конкурентов...", client_profile)

    # Шаг 3: Roadmap и 5 Групп ЦА
    status.write("🗺️ Запуск Движка Стратегии...")
    strategy_data = strategy_engine.process(client_profile)
    if strategy_data:
        client_profile.strategic_goals = strategy_data
        client_profile.audience_groups = strategy_data.get("audience_groups", {})

    # Шаг 4: Проектирование продуктовой линейки
    status.write("💰 Запуск Движка Коммерции (ПТУ)...")
    product_ladder = commerce_engine.process(client_profile)
    if product_ladder:
        # Convert Product dataclasses to dicts for ClientProfileHub
        client_profile.products = [asdict(p) for p in [product_ladder.lead_magnet, product_ladder.tripwire, product_ladder.core_offer, product_ladder.high_ticket] if p]

    # Шаг 5: Диагностика Гармонии
    status.write("🧘 Запуск Движка Диагностики Гармонии...")
    client_profile = harmony_engine.process(client_profile)

    # Шаг 6: Питч флагманского шоу
    status.write("🎬 Запуск Движка Драматургии...")
    client_profile.show_pitch = show_pitch_engine.process(client_profile)

    # Шаг 7: Библиотека форматов
    status.write("📚 Запуск Движка Форматов...")
    client_profile.formats = format_engine.process(client_profile)

    # Шаг 8: Контент-план
    status.write("🗓️ Запуск Движка Контент-Плана...")
    client_profile.content_plan = content_plan_engine.process(client_profile)

    return client_profile, product_ladder

# --- УЛУЧШЕНИЕ: ЛОГИКА ОТОБРАЖЕНИЯ СТАРТОВОГО ЭКРАНА ИЛИ РАБОЧЕГО ПРОСТРАНСТВА ---
# Объявляем колонки в самом начале, чтобы они были видны везде

def run_full_diagnostic():
    """Основная функция, запускающая весь конвейер анализа."""
    st.session_state.processing = True
    st.rerun()

def run_demo_mode():
    """Функция для мгновенного запуска в Демо-режиме."""
    st.session_state.offline_mode = True
    # Предоставляем более полный моковый raw_text для демонстрации
    st.session_state.raw_text = """
    Текст из Мастер-Опросника... Моя манера общения - провокационная, но с позиции наставника. 
    Я часто повторяю фразы "Работаем", "Это база". 
    Ненавижу, когда говорят "короче".
    Мои конкуренты - это те, кто продает "успешный успех" без системы. Они делают много шума, но мало реальной ценности.
    Я хочу упразднить ручную "распаковку" экспертов, снизить время на онбординг, повысить глубину стратегической проработки и создать автоматизированный "Стратегический МРТ-сканер".
    """
    st.session_state.processing = True
    st.rerun()

def render_login_screen():
    """Отрисовывает экран входа в систему."""
    st.header("Вход в CorePath OS")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Пароль", type="password")
        submitted = st.form_submit_button("Войти")

        if submitted:
            # URL вашего FastAPI бэкенда
            api_url = "http://127.0.0.1:8000/token"
            try:
                response = requests.post(
                    api_url,
                    data={"username": email, "password": password}
                )
                if response.status_code == 200:
                    token_data = response.json()
                    st.session_state.token = token_data["access_token"] # type: ignore
                    st.session_state.error_message = None

                    # --- НОВЫЙ ШАГ: ПОЛУЧЕНИЕ ДАННЫХ ПОЛЬЗОВАТЕЛЯ ---
                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                    user_info_response = requests.get("http://127.0.0.1:8000/api/v1/users/me", headers=headers)

                    # --- ШАГ 7: ПОПЫТКА ЗАГРУЗИТЬ ПРОФИЛЬ С БЭКЕНДА ---
                    profiles_response = requests.get("http://127.0.0.1:8000/api/v1/profiles/", headers=headers)

                    if profiles_response.status_code == 200 and profiles_response.json():
                        # Профиль существует, загружаем его
                        profile_data = profiles_response.json()[0] # Берем первый профиль
                        st.session_state.client_profile = ClientProfileHub(**profile_data)

                        # --- ШАГ 12: ЗАГРУЗКА ПРОДУКТОВ ---
                        products_response = requests.get(f"http://127.0.0.1:8000/api/v1/profiles/{profile_data['profile_id']}/products", headers=headers)
                        if products_response.status_code == 200:
                            st.session_state.products = products_response.json()

                        # --- ШАГ 14: ЗАГРУЗКА КОМАНДЫ ---
                        team_response = requests.get(f"http://127.0.0.1:8000/api/v1/profiles/{profile_data['profile_id']}/team", headers=headers)
                        if team_response.status_code == 200:
                            st.session_state.team_members = team_response.json()

                        # --- ШАГ 16: ЗАГРУЗКА АКТИВОВ ВЛИЯНИЯ ---
                        assets_response = requests.get(f"http://127.0.0.1:8000/api/v1/profiles/{profile_data['profile_id']}/assets", headers=headers)
                        if assets_response.status_code == 200:
                            st.session_state.influence_assets = assets_response.json()

                        # --- ШАГ 25: ЗАГРУЗКА КАНАЛОВ МЕССЕНДЖЕРА ---
                        channels_response = requests.get(f"http://127.0.0.1:8000/api/v1/profiles/{profile_data['profile_id']}/channels", headers=headers)
                        if channels_response.status_code == 200:
                            st.session_state.channels = channels_response.json()

                        # --- КОНЕЦ ШАГА 16 ---

                        st.session_state.profile_generated = True
                        st.session_state.strategic_step = 1 # Начинаем пошаговый процесс
                        st.rerun()
                    else:
                        # Профиля нет, показываем экран создания
                        st.session_state.profile_generated = False

                    if user_info_response.status_code == 200:
                        st.session_state.current_user = user_info_response.json()
                        # После успешного входа, запускаем демо-режим для заполнения данных
                        run_demo_mode()
                    else:
                        st.session_state.error_message = "Не удалось получить информацию о пользователе."
                        st.rerun()
                else:
                    st.session_state.error_message = "Неверный email или пароль."
                    st.rerun()

            except requests.exceptions.ConnectionError:
                st.session_state.error_message = "Не удалось подключиться к серверу. Убедитесь, что бэкенд запущен."
                st.rerun()

    if st.session_state.error_message:
        st.error(st.session_state.error_message)

    st.info("Для демонстрации используйте email: `user@example.com`, пароль: `string` (требуется запущенный FastAPI сервер и созданный пользователь). Или нажмите кнопку ниже.")
    st.button("🚀 Пропустить и посмотреть Демо-Профиль", on_click=run_demo_mode, use_container_width=True, type="secondary")


def render_startup_screen():
    """Отрисовывает стартовый экран, если профиль не создан."""
    with st.expander("🚀 Диагностика", expanded=True):
        api_key = st.text_input("🔑 Ваш Gemini API Ключ", type="password", help="Ваш ключ будет использован только для этой сессии и нигде не сохраняется.", key="api_key_input", disabled=st.session_state.processing)
        
        # --- НОВЫЙ БЛОК: Переключатель режима ---
        st.toggle("Режим Демонстрации (без AI)", value=st.session_state.offline_mode, key="offline_mode", help="В этом режиме приложение использует предзагруженные данные и не обращается к AI. Отключите для реальной генерации.", disabled=st.session_state.processing)

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
                            interview_engine = InterviewEngine(api_key=st.session_state.api_key_input, offline_mode=st.session_state.offline_mode)
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

    st.markdown("---")
    # --- НОВЫЙ БЛОК: Кнопка для пропуска ---
    st.button("🚀 Пропустить и посмотреть Демо-Профиль", on_click=run_demo_mode, use_container_width=True, type="primary", help="Мгновенно загружает полностью заполненный демонстрационный профиль без использования AI.")


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
                    if not st.session_state.raw_text and st.session_state.interview_answers:
                        full_text = ""
                        for block_title, questions in QUESTIONNAIRE_QUESTIONS.items():
                            full_text += f"\n\n--- {block_title} ---\n\n"
                            for q_key, q_text in questions.items():
                                answer = st.session_state.interview_answers.get(q_key, "").strip()
                                if answer:
                                    full_text += f"Вопрос: {q_text}\n\n--- Начало диалога ---\n{answer}\n--- Конец диалога ---\n\n"
                        st.session_state.raw_text = full_text

                    # 2. Выполнение диагностики (онлайн или оффлайн)
                    if st.session_state.offline_mode:
                        profile, product_ladder = run_offline_processing(status)
                        
                        # 3. Сохранение результатов в сессию
                        status.update(label="✅ Диагностика завершена! Сохраняю результаты...", state="complete", expanded=False)
                        st.session_state.client_profile = profile
                        st.session_state.scenario_producer = AIScenarioProducer(offline_mode=True)
                        st.session_state.calendar_engine = CalendarEngine(offline_mode=True)
                        if product_ladder:
                            st.session_state.client_profile.products = [asdict(p) for p in [product_ladder.lead_magnet, product_ladder.tripwire, product_ladder.core_offer, product_ladder.high_ticket] if p]
                            st.session_state.product_ladder = product_ladder
                        
                        st.session_state.profile_generated = True
                        st.session_state.processing = False
                        st.rerun()

                    else: # Онлайн-режим
                        status.write("Отправка данных на сервер для анализа...")
                        headers = {"Authorization": f"Bearer {st.session_state.token}"}
                        payload = {"raw_text": st.session_state.raw_text}
                        response = requests.post("http://127.0.0.1:8000/api/v1/profiles/", headers=headers, json=payload)

                        if response.status_code == 201:
                            profile_data = response.json()
                            st.session_state.client_profile = ClientProfileHub(**profile_data)
                            st.session_state.profile_generated = True
                            st.session_state.processing = False
                            status.update(label="✅ Профиль успешно создан на сервере!", state="complete")
                            st.rerun()
                        else:
                            raise ValueError(f"Ошибка сервера: {response.status_code} - {response.text}")

                except Exception as e:
                    st.session_state.processing = False
                    status.update(label=f"Ошибка на этапе диагностики: {e}", state="error")
                    st.error(f"Произошла ошибка: {e}")
                    if st.button("Попробовать снова"):
                        st.rerun()

def render_strategic_wizard():
    """
    Отрисовывает пошаговый мастер (Режим 1Б) для верификации стратегии.
    """
    st.header("Режим 1Б: Пошаговая Верификация Стратегии")
    st.info("Вы проходите 11 шагов методологии F.O.K.I.N. На каждом этапе ваша задача — верифицировать и утвердить результаты, сгенерированные AI.")

    step = st.session_state.strategic_step
    profile = st.session_state.client_profile

    # Навигация по шагам
    step_titles = [
        "Шаг 1: Верификация Цифрового ДНК",
        "Шаг 2: Анализ Конкурентов",
        "Шаг 3: Утверждение Позиционирования (Blue Ocean)",
        "Шаг 4: Утверждение Дорожной Карты",
        "Шаг 5: Проверка на Гармонию (Критический Момент Истины)",
        # ... и так далее
    ]
    
    # Отображаем текущий шаг
    if step == 1:
        st.subheader(step_titles[0])
        st.write("AI проанализировал ваши ответы и сформировал ваше 'Цифровое ДНК'. Проверьте ключевые параметры:")
        st.json({
            "brand_name": profile.brand_name,
            "niche": profile.niche,
            "superpower": profile.superpower,
            "values": profile.values,
            "enemies": profile.enemies
        })

    elif step == 2:
        st.subheader(step_titles[1])
        st.write("На основе анализа конкурентов AI сформировал 'Матрицу 4-х Действий'. Проверьте и утвердите ее.")
        if profile.positioning_matrix:
            st.json(profile.positioning_matrix)
        else:
            st.warning("Данные о позиционировании отсутствуют.")
    
    elif step == 3:
        st.subheader(step_titles[2])
        st.write("Это ваше уникальное позиционирование, которое выводит вас из 'алого океана' прямой конкуренции. Утвердите его.")
        if profile.positioning_matrix:
            mat_col1, mat_col2 = st.columns(2)
            with mat_col1:
                st.markdown("##### Упразднить")
                st.write("\n".join(f"- {item}" for item in profile.positioning_matrix.get("eliminate", ["-"])))
                st.markdown("##### Повысить")
                st.write("\n".join(f"- {item}" for item in profile.positioning_matrix.get("raise", ["-"])))
            with mat_col2:
                st.markdown("##### Снизить")
                st.write("\n".join(f"- {item}" for item in profile.positioning_matrix.get("reduce", ["-"])))
                st.markdown("##### Создать")
                st.write("\n".join(f"- {item}" for item in profile.positioning_matrix.get("create", ["-"])))
        else:
            st.warning("Данные о позиционировании отсутствуют.")

    elif step == 4:
        st.subheader(step_titles[3])
        st.write("Это последовательность ключевых действий для достижения ваших целей и 5 групп аудитории, с которыми нужно взаимодействовать. Утвердите этот план.")
        if profile.strategic_goals:
            strategy_data = profile.strategic_goals
            st.markdown("#### Дорожная Карта (Roadmap)")
            for item in strategy_data.get("roadmap", []):
                st.markdown(f"- **Шаг {item['step']}: {item['title']}** - {item['description']} (Цель: {', '.join(item['target_groups'])})")
        else:
            st.warning("Данные о дорожной карте отсутствуют.")

    elif step == 5:
        st.subheader(step_titles[4])
        st.warning("ВНИМАНИЕ: Это самый важный шаг. Система проверила вашу стратегию на внутренние противоречия, которые могут привести к выгоранию.")
        
        harmony_report = profile.harmony_report
        if harmony_report and "conflict_details" in harmony_report:
            st.error(harmony_report.get("report_text", "Отчет о гармонии неполный."))
        elif harmony_report:
            st.success(harmony_report.get("report_text", "Конфликтов не обнаружено."))
        else:
            st.warning("Отчет о гармонии не был сгенерирован.")

    # ... здесь будут другие шаги

    else:
        st.success("Все шаги верификации пройдены!")
        if st.button("Перейти к Рабочему Пространству"):
            st.session_state.wizard_complete = True
            st.rerun()

    # Кнопки навигации
    if step < 5: # Замените 5 на 11, когда все шаги будут готовы
        if st.button("✅ Утвердить и перейти к следующему шагу", type="primary"):
            st.session_state.strategic_step += 1
            st.rerun()

def render_main_workspace():
    # --- ЭТАП 2: ОСНОВНОЕ РАБОЧЕЕ ПРОСТРАНСТВО ---
    # Переносим определение колонок сюда для надежности
    col1, col2 = st.columns([1, 3])

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
        with st.expander("🚪 Сессия"):
            if st.session_state.current_user:
                st.caption(f"Вы вошли как:")
                st.success(st.session_state.current_user.get('email'))

            if st.button("Выйти из системы", use_container_width=True):
                st.session_state.token = None
                st.rerun()
        
        # --- НОВЫЙ БЛОК: Уведомления ---
        notifications = generate_notifications()
        if notifications:
            st.subheader("🔔 Уведомления")

        with st.expander("Поиск по проекту"):
            search_term = st.text_input("Найти...", label_visibility="collapsed")
            
        # --- ШАГ 22: РЕАЛЬНАЯ ЛОГИКА ДЛЯ ВИДА ПРОДЮСЕРА ---
        if st.session_state.current_user and st.session_state.current_user.get('role') == 'producer':
            producer_mode = st.toggle("👁️ Master Dashboard (Вид Продюсера)", value=st.session_state.producer_view, key="producer_view", help="Агрегирует задачи со всех ваших проектов.")
            if producer_mode and not st.session_state.producer_tasks:
                # Загружаем данные для дашборда продюсера, если они еще не загружены
                with st.spinner("Загрузка данных со всех проектов..."):
                    api_url = "http://127.0.0.1:8000/api/v1/producer/dashboard-tasks"
                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                    response = requests.get(api_url, headers=headers)
                    if response.status_code == 200:
                        st.session_state.producer_tasks = response.json()
                        st.rerun()
        else:
            st.markdown("##### Симуляция Будущих Модулей")
            st.info("💬 Защищенный Мессенджер (в разработке)")
            if st.toggle("👁️ Переключиться на вид Продюсера", value=st.session_state.producer_view, key="producer_view", help="Симулирует Master Dashboard, показывая задачи со всех проектов."):
                st.rerun()
            # ... (логика поиска)

        # --- Блок редактирования ---
        with st.expander("Редактировать Профиль"):

            with st.form(key='profile_edit_form'):
                # ... (форма редактирования)
                st.form_submit_button("💾 Сохранить изменения")

    with col2:
        st.header(" ") # Пустой заголовок для выравнивания
        
        # --- ГЛАВНОЕ ИЗМЕНЕНИЕ: НОВАЯ СТРУКТУРА ВКЛАДОК ---
        tab_list = [
            "📊 Дашборд", 
            "👤 Конструктор Образа",
            "🧭 Стратегия", 
            "🗓️ Контент-План",
            "📦 Продукты", 
            "🎬 Контент", 
            "📋 Задачи", 
            "💬 Мессенджер",
            "🤝 Синергия"
        ]
        
        tabs = st.tabs(tab_list)
        tab_dashboard, tab_obraz_constructor, tab_strategy, tab_plan, tab_products, tab_content, tab_tasks, tab_capital, tab_team, tab_synergy = tabs


        with tab_dashboard:
            if st.session_state.producer_view:
                st.subheader("Master Dashboard (Вид Продюсера)")
                st.info("На этом экране вы видите **реальные** агрегированные данные и задачи со всех ваших проектов. Это ваш 'Пункт Управления Полетами'.")

            else:
                st.subheader("Дашборд Проекта")

            tasks_to_display = st.session_state.producer_tasks if st.session_state.producer_view else st.session_state.tasks

            if tasks_to_display:
                tasks = [Task(**t) for t in tasks_to_display] # Преобразуем dict в dataclass
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
            # --- НОВЫЙ БЛОК: Отображение целей ---
            st.subheader("🎯 Стратегические Цели")
            st.caption("Ваши цели — это компас для всех действий. Здесь они собраны в едином месте.")
            
            if st.session_state.client_profile and st.session_state.client_profile.strategic_goals_list: # type: ignore
                goals = st.session_state.client_profile.strategic_goals_list
                st.markdown(f"**ГЛАВНЫЙ ЗАПРОС (ГЦ):** {goals.get('main_goal', 'Не определен')}")
                st.markdown(f"**Бизнес-цели:** {goals.get('business_goals', 'Не определены')}")
                st.markdown(f"**Медийные цели:** {goals.get('media_goals', 'Не определены')}")
                st.markdown(f"**Миссия:** {goals.get('mission', 'Не определена')}")
            else:
                st.info("Цели пока не определены. Запустите Демо-режим для просмотра.")

            # --- НОВЫЙ БЛОК: Отображение карты конфликтов ---
            st.markdown("---")
            st.subheader("🔥 Карта Конфликтов и Стратегия Баланса")
            st.caption("Здесь показаны противоречия, которые мешают вам двигаться вперед, и стратегия их решения.")
            
            harmony_report = st.session_state.client_profile.harmony_report if st.session_state.client_profile else None # type: ignore
            if harmony_report and "conflict_details" in harmony_report:
                conflict_details = harmony_report["conflict_details"]
                report_text = harmony_report.get("report_text", "")
                
                # Используем новые колонки, чтобы не конфликтовать с глобальными col1, col2
                conflict_col1, conflict_col2 = st.columns(2)
                with conflict_col1:
                    st.error(f"**Конфликтующая Цель:** {conflict_details['conflicting_goal']['goal']}")
                    st.warning(f"**Внутренние 'Враги':** {', '.join(conflict_details['triggers'])}")
                with conflict_col2:
                    st.success(f"**Альтернативная Цель (Решение):** {conflict_details['non_conflicting_goal']['goal']}")
                
                st.markdown("---")
                st.subheader("Стратегия Баланса")
                st.info(report_text)
                
                # Добавляем детали стратегии баланса из вашего документа
                st.markdown("##### Ключевые аспекты:")
                st.markdown("- **Смена Приоритета ГЦ:** Тактический Спринт используется как ресурс для ГЦ №2 (Запуск Приложения).")
                st.markdown("- **Решение 'Игрока-Одиночки':** Фокус на одном проекте (Приложение), а не на 5 клиентских.")
                
                with st.expander("Что это значит?"):
                    st.info("""
                        **Это не проблема, а точка роста.** Обнаруженный конфликт — это скрытое противоречие между вашими целями и внутренними установками (вашими "врагами").
                        
                        Система подсвечивает его, чтобы вы могли превратить это противоречие в **уникальную стратегию**. Вместо того чтобы бороться с "врагом", мы используем его как топливо для достижения второй, более глобальной цели. Это основа для создания сильного, неконкурентного позиционирования.
                        """)
            else:
                st.success("Конфликтов не обнаружено. Ваша стратегия сбалансирована.")
            
            st.markdown("---")
            st.subheader("Матрица 4-х Действий (Blue Ocean)")
            with st.expander("Редактировать Матрицу Позиционирования"):
                st.info("""
                    Это инструмент из "Стратегии Голубого Океана", который помогает отстроиться от конкурентов. Вместо того чтобы конкурировать "в лоб", мы анализируем, что в вашей нише можно:
                    - **Упразднить:** От каких общепринятых, но ненужных вещей можно отказаться?
                    - **Снизить:** Что можно делать меньше, чем конкуренты?
                    - **Повысить:** Какие важные для клиента вещи нужно усилить?
                    - **Создать:** Что абсолютно нового можно предложить рынку, чего не делает никто?
                    Ответы на эти вопросы формируют ваше уникальное позиционирование.
                    """) # type: ignore
                if st.session_state.client_profile and st.session_state.client_profile.positioning_matrix:
                    matrix = st.session_state.client_profile.positioning_matrix
                    mat_col1, mat_col2 = st.columns(2)
                    with mat_col1:
                        matrix['eliminate'] = st.text_area("Упразднить", "\n".join(matrix.get("eliminate", [])), key="matrix_eliminate").splitlines()
                        matrix['raise'] = st.text_area("Повысить", "\n".join(matrix.get("raise", [])), key="matrix_raise").splitlines()
                    with mat_col2:
                        matrix['reduce'] = st.text_area("Снизить", "\n".join(matrix.get("reduce", [])), key="matrix_reduce").splitlines()
                        matrix['create'] = st.text_area("Создать", "\n".join(matrix.get("create", [])), key="matrix_create").splitlines()

            st.markdown("---")
            st.subheader("🗺️ Стратегическая Карта")
            with st.expander("Редактировать Дорожную Карту и Группы ЦА"):
                st.info("Эта карта определяет, **что** делать и **для кого**. **Roadmap** — это последовательность ключевых действий для достижения ваших целей. **Карта Стейкхолдеров** — это 5 ключевых групп аудитории, с которыми нужно взаимодействовать на каждом этапе. Это ваш компас в мире контента и нетворкинга.")

                if st.session_state.client_profile and st.session_state.client_profile.strategic_goals:
                    strategy_data = st.session_state.client_profile.strategic_goals # type: ignore
                    st.markdown("#### Дорожная Карта (Roadmap)")
                    
                    edited_roadmap = st.data_editor(
                        strategy_data.get("roadmap", []),
                        num_rows="dynamic",
                        key="roadmap_editor",
                        use_container_width=True
                    )
                    strategy_data["roadmap"] = edited_roadmap

                    st.markdown("#### Карта Стейкхолдеров (5 Групп ЦА)")
                    edited_audience = st.data_editor(
                        strategy_data.get("audience_groups", {}),
                        key="audience_editor",
                        use_container_width=True
                    )
                    strategy_data["audience_groups"] = edited_audience
            
            st.markdown("---")
            # --- ШАГ 21: КНОПКА СОХРАНЕНИЯ ---
            if st.button("💾 Сохранить изменения в Стратегии", type="primary", use_container_width=True):
                if st.session_state.client_profile and not st.session_state.offline_mode:
                    with st.spinner("Сохранение стратегии..."):
                        profile_id = st.session_state.client_profile.profile_id
                        api_url = f"http://127.0.0.1:8000/api/v1/profiles/{profile_id}"
                        headers = {"Authorization": f"Bearer {st.session_state.token}"}
                        
                        # Отправляем только те части, которые редактировали на этой вкладке
                        payload = {
                            "positioning_matrix": st.session_state.client_profile.positioning_matrix,
                            "strategic_goals": st.session_state.client_profile.strategic_goals
                        }
                        
                        response = requests.put(api_url, headers=headers, json=payload)
                        if response.status_code == 200:
                            st.toast("✅ Стратегия успешно сохранена на сервере!")
                        else:
                            st.error(f"Ошибка сохранения: {response.status_code} - {response.text}")
                else:
                    st.toast("Сохранение доступно только в онлайн-режиме.")

            with st.expander("Показать итоговый Client_Profile_Hub (JSON)", expanded=False):
                st.json(asdict(st.session_state.client_profile))

        with tab_plan: # Контент-План
            st.subheader("🗓️ Автоматический Контент-План на Неделю") # type: ignore
            st.info("Это стратегический план, сгенерированный AI на основе вашего профиля, целей и форматов. Используйте его как основу для создания сценариев во вкладке 'Контент'.")

            if st.session_state.client_profile and st.session_state.client_profile.content_plan:
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
            def render_product_workspace(product_id):
                """Отрисовывает детальное рабочее пространство для одного продукта."""
                product = next((p for p in st.session_state.products if p['product_id'] == product_id), None)
                if not product:
                    st.error("Продукт не найден.")
                    st.session_state.selected_product_id = None
                    st.rerun()
                    return

                if st.button("← Назад к Библиотеке Продуктов"):
                    st.session_state.selected_product_id = None
                    st.rerun()

                st.header(f"Product Workspace: «{product.get('name')}»")

                ws_tab1, ws_tab2, ws_tab3, ws_tab4, ws_tab5 = st.tabs([
                    "1. Суть (PVL)", "2. ЦА", "3. УТП", "4. Декомпозиция", "5. Контент (PLC)"
                ])

                with ws_tab1:
                    st.subheader("Вкладка 1: Суть Продукта и Лестница Ценности (PVL)")
                    st.info("В разработке. Здесь будет UI для редактирования основной информации о продукте (описание, цель) и его места в 'Лестнице Ценности'.")

                with ws_tab2:
                    st.subheader("Вкладка 2: Определение Целевой Аудитории")
                    st.info("В разработке. Здесь будет UI для привязки этого продукта к одной или нескольким из 5-ти групп ЦА, определенных на вкладке 'Стратегия'.")

                with ws_tab3:
                    st.subheader("Вкладка 3: Уникальное Торговое Предложение (УТП)")
                    st.info("В разработке. Здесь будет AI-генератор УТП для этого продукта на основе вашей 'Blue Ocean' стратегии.")

                with ws_tab4:
                    st.subheader("🧮 Декомпозиция Воронки Продаж")
                    st.caption("Этот калькулятор поможет спрогнозировать доход от воронки, ведущей к этому и последующим продуктам.")
                    # --- ПЕРЕНОС СУЩЕСТВУЮЩЕГО КАЛЬКУЛЯТОРА ---
                    active_products = [p for p in st.session_state.products if p.get('status') == 'Active']
                    tripwire_product = next((p for p in active_products if p.get('pvl_tier') == 'tripwire'), None)
                    core_offer_product = next((p for p in active_products if p.get('pvl_tier') == 'core_offer'), None)

                    target_revenue = st.number_input("Желаемый Доход (в месяц)", min_value=0, value=10000, key="ws_target_revenue")
                    traffic = st.number_input("Трафик (посетители в мес.)", min_value=0, value=5000, key="ws_traffic")
                    st.markdown("---")
                    c1 = st.slider("Конверсия в лиды (C1, %)", 0, 100, 20, key="ws_c1") / 100.0
                    c2 = st.slider("Конверсия в покупатели трипвайера (C2, %)", 0, 100, 5, key="ws_c2") / 100.0
                    c3 = st.slider("Конверсия в покупатели Core Offer (C3, %)", 0, 100, 20, key="ws_c3") / 100.0
                    leads = traffic * c1
                    tripwire_buyers = leads * c2
                    core_offer_buyers = tripwire_buyers * c3
                    tripwire_revenue = tripwire_buyers * float(tripwire_product.get('price', 0) if tripwire_product else 0)
                    core_offer_revenue = core_offer_buyers * float(core_offer_product.get('price', 0) if core_offer_product else 0)
                    total_revenue = tripwire_revenue + core_offer_revenue
                    st.markdown("---")
                    st.subheader("Прогноз Результатов")
                    res_col1, res_col2, res_col3 = st.columns(3) 
                    with res_col1: st.metric("Лиды", f"{int(leads):,}")
                    with res_col2: st.metric("Покупатели (Core Offer)", f"{int(core_offer_buyers):,}") # type: ignore
                    with res_col3: st.metric(label="Прогнозируемый Доход", value=f"${int(total_revenue):,}", delta=f"${int(total_revenue - target_revenue):,}")
                    st.progress(min(total_revenue / target_revenue, 1.0))
                    st.write(f"Достижение цели: {total_revenue / target_revenue:.1%}")

                with ws_tab5:
                    st.subheader("Вкладка 5: Контент для Продукта (Product-Led Content)")
                    st.info("В разработке. Здесь будет генератор сценариев, который автоматически использует этот продукт в качестве цели (CTA).")

            # --- ГЛАВНЫЙ РОУТЕР ДЛЯ ВКЛАДКИ "ПРОДУКТЫ" ---
            if st.session_state.selected_product_id:
                render_product_workspace(st.session_state.selected_product_id)
            else:
                st.subheader("Библиотека Продуктов (ПТУ)")
                st.info("Управляйте жизненным циклом ваших продуктов. Кликните на название продукта, чтобы открыть его рабочее пространство.")

                with st.expander("➕ Добавить новый продукт"):
                    with st.form("new_product_form", clear_on_submit=True):
                        new_name = st.text_input("Название продукта")
                        new_price = st.number_input("Цена", min_value=0.0, format="%.2f")
                        new_pvl_tier = st.selectbox("Уровень в воронке (PVL)", ["lead_magnet", "tripwire", "core_offer", "high_ticket"])
                        
                        submitted = st.form_submit_button("Создать продукт")
                        if submitted:
                            if new_name and st.session_state.client_profile and not st.session_state.offline_mode:
                                profile_id = st.session_state.client_profile.profile_id
                                api_url = f"http://127.0.0.1:8000/api/v1/profiles/{profile_id}/products"
                                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                                payload = {"name": new_name, "price": new_price, "pvl_tier": new_pvl_tier, "status": "Idea"}
                                
                                response = requests.post(api_url, headers=headers, json=payload)
                                if response.status_code == 201:
                                    st.session_state.products.append(response.json())
                                    st.toast("✅ Продукт успешно создан!")
                                    st.rerun()
                                else:
                                    st.error(f"Ошибка создания продукта: {response.text}")
                            else:
                                st.warning("Название продукта не может быть пустым. Создание доступно только в онлайн-режиме.")

                p_col1, p_col2, p_col3, p_col4 = st.columns(4)
                columns = {"Idea": p_col1, "In Development": p_col2, "Active": p_col3, "Archived": p_col4}
                column_titles = {"Idea": "💡 Идея", "In Development": "⚙️ В разработке", "Active": "✅ Активен", "Archived": "🗄️ Архив"}

                for status, col in columns.items():
                    with col:
                        st.markdown(f"##### {column_titles[status]}")
                        products_in_column = [p for p in st.session_state.products if p.get('status') == status]
                        for product in products_in_column:
                            with st.container(border=True):
                                if st.button(product.get('name'), key=f"open_{product['product_id']}", use_container_width=True):
                                    st.session_state.selected_product_id = product['product_id']
                                    st.rerun()
                                
                                st.caption(f"Цена: ${product.get('price', 0):.2f} | Уровень: {product.get('pvl_tier', 'N/A')}")
                                
                                with st.expander("Быстрое редактирование статуса"):
                                    new_status = st.selectbox("Статус", options=column_titles.keys(), index=list(column_titles.keys()).index(product.get('status')), key=f"status_{product['product_id']}", label_visibility="collapsed")
                                    if new_status != product.get('status'):
                                        if not st.session_state.offline_mode:
                                            api_url = f"http://127.0.0.1:8000/api/v1/products/{product['product_id']}"
                                            headers = {"Authorization": f"Bearer {st.session_state.token}"}
                                            payload = {"status": new_status}
                                            response = requests.put(api_url, headers=headers, json=payload)
                                            if response.status_code == 200:
                                                product.update(response.json())
                                                st.toast("✅ Статус продукта обновлен!")
                                                st.rerun()
                                            else:
                                                st.error(f"Ошибка: {response.text}")
                                        else:
                                            st.warning("Редактирование доступно только в онлайн-режиме.")

        with tab_content: # Контент
            st.header("🎬 AI-Сценарист")
            
            mode_constructor, mode_surprise, mode_project, mode_formats = st.tabs(["🛠️ Конструктор", "🔥 Удиви меня!", "🗂️ Создать проект", "📚 Рабочие форматы"])

            with mode_constructor:
                with st.form("scenario_constructor_form"):
                    st.subheader("🛠️ Конструктор Сценариев")
                    st.caption("Заполните 8 опорных точек, чтобы получить предсказуемый и управляемый результат.")

                    prefill_data = st.session_state.get('prefill_data', None)
                    format_names = ["(Создать с нуля)"] + [f.get('format_name', f'Формат #{i+1}') for i, f in enumerate(st.session_state.client_profile.formats or [])]
                    default_format_index = 0
                    if prefill_data and prefill_data.get("format_name") in format_names:
                        default_format_index = format_names.index(prefill_data.get("format_name"))

                    selected_format_name = st.selectbox("Выберите формат из вашей библиотеки (опционально):", format_names, index=default_format_index)

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
                    blog_genre = st.selectbox("4. Жанр Блога (Видеоформат)", ANCHOR_POINTS_DATA["blog_genres"])
                    extras_triggers = st.multiselect("5. Допы/Триггеры (можно несколько)", ANCHOR_POINTS_DATA["extras_triggers"])
                    movie_genre = st.selectbox("6. Жанр Кино (Атмосфера)", ANCHOR_POINTS_DATA["movie_genres"])
                    tv_genre = st.selectbox("7. ТВ Жанр (Структура выпуска)", ANCHOR_POINTS_DATA["tv_genres"])
                    character_default = st.session_state.client_profile.brand_name if st.session_state.client_profile else ""
                    character = st.text_input("8. Персонаж/Ниша", value=character_default)
                    
                    if 'prefill_data' in st.session_state:
                        del st.session_state['prefill_data']

                    product_names = ["(Нет продукта)"] + [p['name'] for p in (st.session_state.products or [])]
                    selected_product_name = st.selectbox("Выберите продукт для продвижения (опционально):", product_names)
                    
                    submitted = st.form_submit_button("🎬 Сгенерировать Сценарий")
                    if submitted:
                        # ... (логика генерации остается той же)
                        pass

            with mode_surprise:
                st.subheader("🔥 Удиви меня!")
                st.info("Этот режим создан для борьбы с творческим выгоранием. AI проанализирует ваши ценности и 'врагов' и предложит неожиданную идею, не требующую долгих раздумий.")
                if st.button("⚡️ Сгенерировать неожиданную идею!", type="primary", use_container_width=True):
                    scenario_producer = st.session_state.get('scenario_producer')
                    if scenario_producer and st.session_state.client_profile:
                        with st.spinner("Ищу вдохновение в вашем ДНК..."):
                            script = scenario_producer.process_surprise_me(st.session_state.client_profile)
                            if script:
                                script["anchor_points_ref"] = {"idea": script.get("title")} # Добавляем заглушку для совместимости
                                st.session_state.script_history.append(script)
                                st.session_state.current_script = script
                                st.toast("✅ Неожиданная идея сгенерирована!")
                            else:
                                st.error("Не удалось сгенерировать сценарий.")
                    else:
                        st.warning("Для работы этого режима необходимо сначала сгенерировать профиль.")

            with mode_project:
                st.subheader("🗂️ Создать проект")
                st.info("В разработке. Этот режим позволит создавать целые контентные проекты (например, запуск продукта) с автоматической генерацией серии сценариев.")

            with mode_formats:
                st.subheader("📚 Рабочие форматы")
                st.info("В разработке. Этот режим позволит быстро генерировать контент на основе вашей библиотеки форматов, созданной на вкладке 'Стратегия'.")

            if st.session_state.current_script:
                script_data = st.session_state.current_script
                st.subheader(f"Сценарий: «{script_data.get('title', 'Без названия')}»")
                st.markdown("##### ⚡️ 1. ШОК (0.5с)"); st.info(script_data.get('shock', ''))
                st.markdown("##### 🎣 2. ХУК (3с)"); st.info(script_data.get('hook', ''))
                st.markdown("##### 📦 3. КОНТЕНТ (15с)"); st.info(script_data.get('content', ''))
                st.markdown("##### 4. CTA (Призыв к действию)"); st.success(script_data.get('cta', ''))

        with tab_tasks: # Задачи
            st.subheader("Декомпозиция в Задачи") # type: ignore

            # --- НОВЫЙ БЛОК: ВЫБОР СЦЕНАРИЯ ДЛЯ ДЕКОМПОЗИЦИИ ---
            if st.session_state.script_history:
                history_options = {f"Сценарий #{i+1}: {s.get('title', 'Без названия')}": i for i, s in enumerate(st.session_state.script_history)}
                selected_script_title = st.selectbox("Выберите сценарий для создания плана:", options=history_options.keys())
                

                # Обновляем текущий сценарий для декомпозиции
                selected_script_index = history_options[selected_script_title]
                script_to_decompose = st.session_state.script_history[selected_script_index]

                if st.button("📅 Создать План Проекта"):
                    if st.session_state.offline_mode:
                        st.warning("Декомпозиция сценариев доступна только в онлайн-режиме.")
                    elif st.session_state.client_profile:
                        with st.spinner("Отправка сценария на сервер для декомпозиции..."):
                            profile_id = st.session_state.client_profile.profile_id
                            api_url = f"http://127.0.0.1:8000/api/v1/profiles/{profile_id}/decompose"
                            headers = {"Authorization": f"Bearer {st.session_state.token}"}
                            
                            original_anchor_points = script_to_decompose.get('anchor_points_ref', {})
                            payload = {
                                "script": script_to_decompose,
                                "anchor_points": original_anchor_points
                            }

                            response = requests.post(api_url, headers=headers, json=payload)

                            if response.status_code == 201:
                                new_tasks = response.json()
                                st.success(f"✅ Сервер успешно сгенерировал и сохранил {len(new_tasks)} задач!")
                                # Мы не сохраняем задачи в session_state, а просто перезапускаем, чтобы они загрузились с сервера
                                st.rerun()
                            else:
                                st.error(f"Ошибка сервера при декомпозиции: {response.status_code} - {response.text}")
            else:
                st.warning("Сначала сгенерируйте сценарий во вкладке 'Контент'.")

            if 'tasks' in st.session_state and st.session_state.tasks:
                st.markdown("---")
                st.subheader("Канбан-доска")
                # ... (код Канбан-доски остается без изменений)
                if 'editing_task_index' not in st.session_state:
                    st.session_state.editing_task_index = None # type: ignore
                def display_task(task, index):
                    # Список ответственных теперь формируется из командного модуля
                    team_members = st.session_state.client_profile.team if st.session_state.client_profile else []
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
                                new_comment = Comment(author=author_name, text=comment_text)
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
                                new_attachment = Attachment(file_name=uploaded_file.name, file_data=uploaded_file.getvalue()) # type: ignore
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
                            st.rerun() # type: ignore

                    else:
                        col_desc, col_actions = st.columns([3, 1])
                        with col_desc: st.markdown(f"> {task.description}")
                        
                        with col_actions:
                            # Выбор ответственного
                            new_responsible = st.selectbox("Ответственный", responsibles, key=f"responsible_{index}", index=responsibles.index(task.responsible) if task.responsible in responsibles else 0, label_visibility="collapsed") # type: ignore


                            # Установка дедлайна
                            new_deadline = st.date_input("Дедлайн", value=task.deadline, key=f"deadline_{index}") # type: ignore
                            
                            # --- НОВЫЙ БЛОК: СИМУЛЯЦИЯ "КОНФЛИКТА РЕСУРСОВ" ---
                            conflict_detected = False
                            if new_responsible and new_deadline:
                                # Ищем другие задачи с тем же ответственным и тем же дедлайном
                                for i, other_task in enumerate(st.session_state.tasks):
                                    if i != index and other_task.responsible == new_responsible and other_task.deadline == new_deadline:
                                        st.warning(f"🔥 Конфликт! {new_responsible} уже занят в этот день задачей «{other_task.description}».")
                                        conflict_detected = True
                                        break # Достаточно одного конфликта для предупреждения
                            
                            # Обновляем данные только если нет конфликта или пользователь все равно решил сохранить
                            if not conflict_detected:
                                st.session_state.tasks[index].responsible = new_responsible
                                st.session_state.tasks[index].deadline = new_deadline

                        # Отображение дедлайна после всех проверок
                        today = date.today()
                        if task.deadline:
                            delta = (task.deadline - today).days
                            if delta < 0 and task.status != "Done":
                                col_desc.caption(f"🔥 Дедлайн: {task.deadline.strftime('%d.%m.%Y')} (Просрочено на {-delta} д.)")
                            else:
                                col_desc.caption(f"🗓️ Дедлайн: {task.deadline.strftime('%d.%m.%Y')}")

                        with col_actions:
                            if st.button("✏️", key=f"edit_{index}"):
                                st.session_state.editing_task_index = index
                                st.rerun()
                            if st.button("🗑️", key=f"delete_{index}"): # type: ignore
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

        with tab_capital: # Медийный Капитал
            st.subheader("🏆 Медийный Капитал (Аудит Репутации)") # type: ignore

            st.info("Ваша репутация — это актив для работы с партнерами, инвесторами и ключевыми фигурами (ЦА 3-5). Здесь мы проводим его инвентаризацию.")

            # --- Модуль 6.1: Инвентаризация Медийного Веса ---
            with st.expander("Блок 6.1: Инвентаризация Медийного Веса", expanded=True):
                st.markdown("#### Формальные Регалии (Фундамент)")
                st.session_state.client_profile.formal_regalia = st.text_area( # type: ignore # type: ignore
                    "Образование, награды, звания, официальные титулы.",
                    "\n".join(st.session_state.client_profile.formal_regalia),
                    key="formal_regalia_input", help="Каждая регалия с новой строки."
                ).splitlines() # type: ignore

                st.markdown("#### Социальный Капитал (Сеть)") # type: ignore
                st.session_state.client_profile.social_capital = st.text_area(
                    "Список известных людей/брендов, с которыми вы работали или которые вас упоминают.",
                    "\n".join(st.session_state.client_profile.social_capital),
                    key="social_capital_input", help="Каждый пункт с новой строки."
                ).splitlines() # type: ignore

                st.markdown("#### «Живые Регалии» (Портфель Активов)")
                st.caption("Ваши измеримые достижения: кейсы, отзывы, упоминания в СМИ, выступления. Добавляются через форму ниже.")
            
            # --- Модуль 6.2: Протокол «Аудита Прошлого» ---
            with st.expander("Блок 6.2: Протокол «Аудита Прошлого» (Конфиденциально)"): # type: ignore
                st.warning("Будьте абсолютно честны с собой. То, что мы знаем, мы можем контролировать.")
                
                if not st.session_state.client_profile.reputational_risks:
                    st.session_state.client_profile.reputational_risks = [
                        {"Риск": "Были ли у вас публичные конфликты?", "Есть": False, "Описание/Контр-аргумент": ""},
                        {"Риск": "Существуют ли «неудобные» фото или видео из прошлого?", "Есть": False, "Описание/Контр-аргумент": ""},
                        {"Риск": "Были ли у вас проблемы с законом или финансовые споры?", "Есть": False, "Описание/Кон-аргумент": ""},
                        {"Риск": "Высказывали ли вы ранее мнения, противоречащие образу?", "Есть": False, "Описание/Контр-аргумент": ""},
                        {"Риск": "Есть ли люди, которые могут иметь на вас «зуб»?", "Есть": False, "Описание/Контр-аргумент": ""},
                    ]
                

                edited_risks = st.data_editor(st.session_state.client_profile.reputational_risks, key="risks_editor") # type: ignore
                st.session_state.client_profile.reputational_risks = edited_risks

            st.markdown("---")
            st.subheader("💼 Управление Портфелем Активов")
            with st.expander("➕ Добавить новый актив влияния"):
                with st.form("influence_asset_form", clear_on_submit=True):
                    asset_type_input = st.selectbox("Тип актива", ["Отзыв", "Кейс", "Упоминание в СМИ", "Выступление"])
                    asset_title_input = st.text_input("Заголовок актива", placeholder="Например: 'Отзыв от клиента X о курсе'")
                    uploaded_image_input = st.file_uploader("Загрузить изображение (опционально)", type=["png", "jpg", "jpeg"])
                    asset_description_input = st.text_area("Описание / Текст актива", placeholder="Вставьте сюда текст отзыва, описание кейса или ссылку на публикацию.")
                    asset_submitted = st.form_submit_button("Добавить в капитал")
                    if asset_submitted:
                        if asset_title_input and asset_description_input and st.session_state.client_profile and not st.session_state.offline_mode:
                            profile_id = st.session_state.client_profile.profile_id
                            api_url = f"http://127.0.0.1:8000/api/v1/profiles/{profile_id}/assets"
                            headers = {"Authorization": f"Bearer {st.session_state.token}"}
                            # В реальном приложении здесь была бы логика загрузки файла в S3
                            # и получения image_url. Сейчас мы его просто проигнорируем.
                            payload = {
                                "title": asset_title_input,
                                "asset_type": asset_type_input,
                                "description": asset_description_input
                            }
                            
                            response = requests.post(api_url, headers=headers, json=payload)
                            if response.status_code == 201:
                                st.session_state.influence_assets.append(response.json())
                                st.toast(f"✅ Актив «{asset_title_input}» успешно добавлен!")
                                st.rerun()
                            else:
                                st.error(f"Ошибка добавления: {response.text}")
                        else:
                            st.warning("Заголовок и описание не могут быть пустыми. Добавление доступно только в онлайн-режиме.")

            if st.session_state.influence_assets:
                for asset in reversed(st.session_state.influence_assets):
                    with st.container(border=True):
                        st.markdown(f"**{asset.get('title')}**")
                        if asset.get('image_url'):
                            st.image(asset.get('image_url'), width=300)
                        st.caption(f"Тип: {asset.get('asset_type')}")
                        st.write(asset.get('description'))
                        if st.button("🗑️ Удалить актив", key=f"del_asset_{asset['asset_id']}", type="secondary"):
                            api_url = f"http://127.0.0.1:8000/api/v1/assets/{asset['asset_id']}"
                            headers = {"Authorization": f"Bearer {st.session_state.token}"}
                            response = requests.delete(api_url, headers=headers)
                            if response.status_code == 204:
                                st.session_state.influence_assets = [a for a in st.session_state.influence_assets if a['asset_id'] != asset['asset_id']]
                                st.toast(f"🗑️ Актив «{asset.get('title')}» удален.")
                                st.rerun()
                            else:
                                st.error(f"Ошибка удаления: {response.text}")
            else:
                st.info("В вашем портфеле пока нет активов. Добавьте первый, используя форму выше.")

        with tab_team: # Команда
            st.subheader("👥 Командный Модуль (CorePath Team)")
            st.info("Управляйте составом вашей проектной команды. Эти данные используются для назначения ответственных в модуле 'Задачи'.")

            with st.expander("➕ Добавить нового члена команды"):
                with st.form("team_member_form", clear_on_submit=True):
                    member_name = st.text_input("Имя члена команды")
                    member_role = st.text_input("Роль в проекте", placeholder="Например: Сценарист, Монтажер")
                    member_tags = st.text_input("Теги (через запятую)", placeholder="#монтажер_reels, #сценарист_подкаст")
                    
                    member_submitted = st.form_submit_button("Добавить в команду")
                    if member_submitted:
                        if member_name and member_role and st.session_state.client_profile and not st.session_state.offline_mode:
                            profile_id = st.session_state.client_profile.profile_id
                            api_url = f"http://127.0.0.1:8000/api/v1/profiles/{profile_id}/team"
                            headers = {"Authorization": f"Bearer {st.session_state.token}"}
                            tags_list = [tag.strip() for tag in member_tags.split(',') if tag.strip()]
                            payload = {"name": member_name, "role": member_role, "tags": tags_list}

                            response = requests.post(api_url, headers=headers, json=payload)
                            if response.status_code == 201:
                                st.session_state.team_members.append(response.json())
                                st.toast(f"✅ Участник «{member_name}» добавлен в команду!")
                                st.rerun()
                            else:
                                st.error(f"Ошибка добавления: {response.text}")
                        else:
                            st.warning("Имя и роль не могут быть пустыми. Добавление доступно только в онлайн-режиме.")
            
            st.subheader("Состав команды")
            if st.session_state.team_members:
                for member in st.session_state.team_members:
                    col_name, col_role, col_action = st.columns([2, 2, 1])
                    col_name.write(member.get('name'))
                    col_role.write(member.get('role'))
                    if col_action.button("🗑️ Удалить", key=f"del_member_{member['member_id']}"):
                        api_url = f"http://127.0.0.1:8000/api/v1/team/{member['member_id']}"
                        headers = {"Authorization": f"Bearer {st.session_state.token}"}
                        response = requests.delete(api_url, headers=headers)
                        if response.status_code == 204:
                            st.session_state.team_members = [m for m in st.session_state.team_members if m['member_id'] != member['member_id']]
                            st.toast(f"🗑️ Участник «{member.get('name')}» удален.")
                            st.rerun()
                        else:
                            st.error(f"Ошибка удаления: {response.text}")
            else:
                st.info("В вашей команде пока нет участников.")

        with tab_synergy:
            st.subheader("🤝 Модуль «Синергия»") # type: ignore

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
                        synergy_engine = SynergyEngine(api_key=st.session_state.api_key_input, offline_mode=st.session_state.offline_mode)
                        synergy_pitch = synergy_engine.process(profiles_to_analyze)
                        if synergy_pitch:
                            st.success("Найдена потенциальная коллаборация!")
                            st.json(synergy_pitch)

        # --- НОВЫЙ БЛОК: УГЛУБЛЕННЫЙ ОПРОСНИК ДЛЯ ОБРАЗА ---
        with tab_obraz_constructor:
            st.header("👤 Конструктор «Образа»")
            st.info("Это ваше интерактивное рабочее пространство для проектирования всех аспектов вашего медийного образа. Заполните эти блоки, чтобы система генерировала максимально точный и аутентичный контент.")

            if not st.session_state.client_profile:
                st.warning("Сначала запустите Демо-режим, чтобы загрузить профиль для редактирования.")
                return # Используем return вместо st.stop() в функциях

            # Используем вкладки для каждого блока, как в вашем документе
            obraz_tab1, obraz_tab2, obraz_tab3, obraz_tab4, obraz_tab5, obraz_tab6 = st.tabs([
                "1. Эмоциональное Ядро", 
                "2. Визуальная Идентичность", 
                "3. Вербальный Код", 
                "4. Матрица Компетенций", 
                "5. Медийный Капитал",
                "6. Командный Модуль"
            ])

            with obraz_tab1:
                st.subheader("Блок 1: Эмоциональное Ядро (Матрица 8 Ключевых Эмоций)")
                st.caption("Опишите ваши эмоциональные реакции. Это основа драматургии вашего образа.")
                
                # Инициализация матрицы, если она пуста (для демо-режима уже заполнена)
                if not st.session_state.client_profile.emotion_matrix: # type: ignore
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
                
                edited_emotions = st.data_editor(st.session_state.client_profile.emotion_matrix, num_rows="dynamic", key="obraz_constructor_emotion_editor", use_container_width=True) # type: ignore
                st.session_state.client_profile.emotion_matrix = edited_emotions
                st.session_state.client_profile.peak_emotions = st.multiselect("Выберите 3 'пиковые' эмоции:", [e["Эмоция"] for e in edited_emotions], default=st.session_state.client_profile.peak_emotions, max_selections=3, key="obraz_constructor_peak_emotions") # type: ignore

            with obraz_tab2:
                st.subheader("Блок 2: Визуальная Идентичность (Стратегия Скрытого Влияния)")
                st.caption("Закодируйте ваш образ через цвета, стиль и визуальные якоря.")
                
                if not st.session_state.client_profile.visual_identity: # type: ignore
                    st.session_state.client_profile.visual_identity = {} # type: ignore
                
                vi = st.session_state.client_profile.visual_identity # type: ignore
                vi['base_palette'] = st.text_input("Базовая Палитра (2-3 нейтральных цвета)", vi.get('base_palette', "Черный, Серый, Темно-синий"), key="obraz_vi_base_palette")
                vi['accent_palette'] = st.text_input("Акцентная Палитра (1-2 ярких цвета)", vi.get('accent_palette', "Красный"), key="obraz_vi_accent_palette")
                vi['visual_anchors'] = st.text_area("Аксессуары и Визуальные Якоря", vi.get('visual_anchors', "Очки определенной оправы\nЧасы (Скрытый Премиум)"), key="obraz_vi_visual_anchors")
                vi['clothing_style'] = st.selectbox("Предпочтительный Стиль Одежды", ["Business Casual", "Tech Minimalist", "Smart Casual", "Creative"], index=["Business Casual", "Tech Minimalist", "Smart Casual", "Creative"].index(vi.get('clothing_style', "Tech Minimalist")), key="obraz_vi_clothing_style")

                st.markdown("##### Коллекция «Луков»")
                st.caption("Ваша 'библиотека образов'. Выберите один из них в зависимости от задачи дня.")
                if 'look_collection' not in vi or not vi['look_collection']:
                    vi['look_collection'] = [
                        {"Название «Лука»": "ЭКСПЕРТ", "Позиционирование / Задача": "Трансляция авторитета, власти", "Ключевые Элементы": "Темно-синий блейзер, качественная футболка", "Акцент / Аксессуар": "Часы", "Когда Использовать": "Вебинары, B2B-переговоры"},
                        {"Название «Лука»": "ПРОВОКАТОР", "Позиционирование / Задача": "Трансляция энергии, 'пиковых эмоций'", "Ключевые Элементы": "Черная водолазка, кожаная куртка", "Акцент / Аксессуар": "Красный браслет", "Когда Использовать": "Конфликтный контент, шоу"},
                        {"Название «Лука»": "СВОЙ ПАРЕНЬ", "Позиционирование / Задача": "Трансляция эмпатии, аутентичности", "Ключевые Элементы": "Серая футболка, худи, джинсы", "Акцент / Аксессуар": "Отсутствие ярких акцентов", "Когда Использовать": "Лайфстайл-контент, сторис"},
                        {"Название «Лука»": "НАСТАВНИК", "Позиционирование / Задача": "Сочетание авторитета и эмпатии", "Ключевые Элементы": "Качественный свитер, светлая рубашка", "Акцент / Аксессуар": "Очки, блокнот", "Когда Использовать": "Обучающие лекции, разбор кейсов"},
                    ]
                
                edited_looks = st.data_editor(vi['look_collection'], num_rows="dynamic", key="obraz_constructor_looks_editor", use_container_width=True)
                vi['look_collection'] = edited_looks

            with obraz_tab3:
                st.subheader("Блок 3: Вербальный и Вокальный Код")
                st.caption("Определите ваш 'Голос Бренда'. Что и как вы говорите.")
                
                if not st.session_state.client_profile.verbal_code: # type: ignore
                    st.session_state.client_profile.verbal_code = {} # type: ignore

                vc = st.session_state.client_profile.verbal_code # type: ignore
                vc['anchor_phrases'] = st.text_input("Фразы-Якоря (через запятую)", vc.get('anchor_phrases', ""), key="obraz_vc_anchors")
                vc['communication_style'] = st.selectbox("Манера Общения", ["Таинственный", "Провокационный", "Дружелюбный", "Авторитетный", "Наставнический"], index=["Таинственный", "Провокационный", "Дружелюбный", "Авторитетный", "Наставнический"].index(vc.get('communication_style', "Авторитетный")), key="obraz_vc_style")
                vc['profanity_use'] = st.selectbox("Использование Мата", ["Нет", "Да", "В Исключениях"], index=["Нет", "Да", "В Исключениях"].index(vc.get('profanity_use', "В Исключениях")), key="obraz_vc_profanity")
                vc['foreign_words_use'] = st.selectbox("Иностранщина / Англицизмы", ["Нет", "Да", "Только Проф."], index=["Нет", "Да", "Только Проф."].index(vc.get('foreign_words_use', "Да")), key="obraz_vc_foreign")
                vc['professional_jargon'] = st.text_area("Профессиональный Жаргон (термин: объяснение)", vc.get('professional_jargon', ""), key="obraz_vc_jargon")
                vc['accent_words'] = st.text_input("Акцентные Слова", vc.get('accent_words', ""), key="obraz_vc_accent_words")
                vc['favorite_quotes'] = st.text_area("Любимые Цитаты", vc.get('favorite_quotes', ""), key="obraz_vc_quotes")
                vc['forbidden_words'] = st.text_input("Слова-Паразиты (ЗАПРЕТ)", vc.get('forbidden_words', ""), key="obraz_vc_forbidden")
                vc['synonym_words'] = st.text_area("Слова-Синонимы (АКТИВ)", vc.get('synonym_words', ""), key="obraz_vc_synonyms")

                st.markdown("---")
                st.markdown("#### Тренажер: Бесконечный Монолог")
                st.caption("Нажмите на иконку микрофона, чтобы записать монолог на 1-3 минуты на любую тему. Затем прослушайте запись и проведите аудит своей речи.")
                with st.container():
                    wav_audio_data = st_audiorec()
                    if wav_audio_data is not None:
                        st.audio(wav_audio_data, format='audio/wav')
                        st.text_area("Аудит Слов-Паразитов (выпишите все, что заметили)", key="obraz_parasite_audit_area")

            with obraz_tab4:
                st.subheader("Блок 4: Матрица Компетенций")
                st.caption("Проведите инвентаризацию ваших активов и определите точки роста.")
                
                if not st.session_state.client_profile.competencies: # type: ignore
                    st.session_state.client_profile.competencies = {"superpowers": [], "growth_zones": []} # type: ignore

                comp = st.session_state.client_profile.competencies # type: ignore
                comp['superpowers'] = st.text_area("Мои «Суперсилы» (Инструменты Воздействия)", "\n".join(comp.get('superpowers', [])), key="obraz_comp_superpowers", help="Каждый навык с новой строки.")
                comp['growth_zones'] = st.text_area("Мои «Зоны Роста» (Над чем стоит поработать)", "\n".join(comp.get('growth_zones', [])), key="obraz_comp_growth", help="Каждый пункт с новой строки.")

                st.session_state.client_profile.competencies['superpowers'] = [line.strip() for line in comp['superpowers'].split('\n') if line.strip()] # type: ignore
                st.session_state.client_profile.competencies['growth_zones'] = [line.strip() for line in comp['growth_zones'].split('\n') if line.strip()] # type: ignore

                st.markdown("---")
                st.markdown("#### Матрица Применения «Суперсил»")
                st.caption("Свяжите ваши навыки с конкретными целями, чтобы превратить их в работающие активы.")
                
                if not st.session_state.client_profile.superpower_application: # type: ignore
                     st.session_state.client_profile.superpower_application = [ # type: ignore
                         {"Инструмент / Суперсила": "", "Связанная Цель": "", "Механизм Помощи": ""},
                     ]

                edited_superpower_app = st.data_editor(st.session_state.client_profile.superpower_application, num_rows="dynamic", key="obraz_superpower_app_editor", use_container_width=True) # type: ignore
                st.session_state.client_profile.superpower_application = edited_superpower_app # type: ignore

            with obraz_tab5:
                st.subheader("Блок 5: Медийный Капитал (Аудит Репутации)")
                st.info("Ваша репутация — это актив для работы с партнерами, инвесторами и ключевыми фигурами (ЦА 3-5). Здесь мы проводим его инвентаризацию.")

                with st.expander("Блок 5.1: Инвентаризация Медийного Веса", expanded=True):
                    st.markdown("#### Формальные Регалии (Фундамент)")
                    st.session_state.client_profile.formal_regalia = st.text_area( # type: ignore
                        "Образование, награды, звания, официальные титулы.",
                        "\n".join(st.session_state.client_profile.formal_regalia), # type: ignore
                        key="obraz_formal_regalia_input", help="Каждая регалия с новой строки."
                    ).splitlines() # type: ignore

                    st.markdown("#### Социальный Капитал (Сеть)")
                    st.session_state.client_profile.social_capital = st.text_area( # type: ignore
                        "Список известных людей/брендов, с которыми вы работали или которые вас упоминают.",
                        "\n".join(st.session_state.client_profile.social_capital), # type: ignore
                        key="obraz_social_capital_input", help="Каждый пункт с новой строки."
                    ).splitlines() # type: ignore

                    st.markdown("#### «Живые Регалии» (Портфель Активов)")
                    st.caption("Ваши измеримые достижения: кейсы, отзывы, упоминания в СМИ, выступления. Добавляются через форму ниже.")
                
                with st.expander("Блок 5.2: Протокол «Аудита Прошлого» (Конфиденциально)"):
                    st.warning("Будьте абсолютно честны с собой. То, что мы знаем, мы можем контролировать.")
                    
                    if not st.session_state.client_profile.reputational_risks: # type: ignore
                        st.session_state.client_profile.reputational_risks = [ # type: ignore
                            {"Риск": "Были ли у вас публичные конфликты?", "Есть": False, "Описание/Контр-аргумент": ""},
                            {"Риск": "Существуют ли «неудобные» фото или видео из прошлого?", "Есть": False, "Описание/Контр-аргумент": ""},
                            {"Риск": "Были ли у вас проблемы с законом или финансовые споры?", "Есть": False, "Описание/Кон-аргумент": ""},
                            {"Риск": "Высказывали ли вы ранее мнения, противоречащие образу?", "Есть": False, "Описание/Контр-аргумент": ""},
                            {"Риск": "Есть ли люди, которые могут иметь на вас «зуб»?", "Есть": False, "Описание/Контр-аргумент": ""},
                        ]
                    
                    edited_risks = st.data_editor(st.session_state.client_profile.reputational_risks, key="obraz_risks_editor", use_container_width=True) # type: ignore
                    st.session_state.client_profile.reputational_risks = edited_risks # type: ignore

                st.markdown("---")
                st.subheader("💼 Управление Портфелем Активов")
                with st.expander("➕ Добавить новый актив влияния"):
                    with st.form("obraz_influence_asset_form", clear_on_submit=True):
                        asset_type = st.selectbox("Тип актива", ["Отзыв", "Кейс", "Упоминание в СМИ", "Выступление"], key="obraz_asset_type")
                        asset_title = st.text_input("Заголовок актива", placeholder="Например: 'Отзыв от клиента X о курсе'", key="obraz_asset_title")
                        uploaded_image = st.file_uploader("Загрузить изображение (опционально)", type=["png", "jpg", "jpeg"], key="obraz_uploaded_image")
                        asset_description = st.text_area("Описание / Текст актива", placeholder="Вставьте сюда текст отзыва, описание кейса или ссылку на публикацию.", key="obraz_asset_description")
                        asset_submitted = st.form_submit_button("Добавить в капитал")
                        if asset_submitted:
                            if asset_title and asset_description:
                                image_data = None
                                if uploaded_image is not None:
                                    image_data = uploaded_image.getvalue()
                                
                                new_asset = InfluenceAsset(title=asset_title, asset_type=str(asset_type), description=asset_description, image_bytes=image_data)
                                st.session_state.client_profile.influence_capital.append(new_asset) # type: ignore
                                st.success(f"Актив «{asset_title}» успешно добавлен!")
                            else:
                                st.error("Заголовок и описание актива не могут быть пустыми.")

                if st.session_state.client_profile.influence_capital: # type: ignore
                    for asset in reversed(st.session_state.client_profile.influence_capital): # type: ignore
                        with st.container(border=True):
                            st.markdown(f"**{asset.title}**")
                            if asset.image_bytes:
                                st.image(asset.image_bytes, width=300)
                            st.caption(f"Тип: {asset.asset_type}")
                            st.write(asset.description)
                else:
                    st.info("В вашем портфеле пока нет активов. Добавьте первый, используя форму выше.")

            with obraz_tab6:
                # --- ШАГ 8: КНОПКА СОХРАНЕНИЯ ---
                st.markdown("---")
                if st.button("💾 Сохранить все изменения в Образе на сервере", type="primary", use_container_width=True):
                    if st.session_state.client_profile and not st.session_state.offline_mode:
                        with st.spinner("Сохранение данных..."):
                            profile_id = st.session_state.client_profile.profile_id # type: ignore
                            api_url = f"http://127.0.0.1:8000/api/v1/profiles/{profile_id}"
                            headers = {"Authorization": f"Bearer {st.session_state.token}"}
                            
                            # Преобразуем dataclass в dict для отправки
                            payload = asdict(st.session_state.client_profile)
                            
                            response = requests.put(api_url, headers=headers, json=payload)
                            
                            if response.status_code == 200:
                                st.toast("✅ Профиль успешно сохранен на сервере!")
                            else:
                                st.error(f"Ошибка сохранения: {response.status_code} - {response.text}")
                    else:
                        st.toast("Сохранение доступно только в онлайн-режиме.")
                st.subheader("Блок 6: Командный Модуль")
                st.caption("Управляйте вашей командой. Эти данные используются для назначения задач и предотвращения конфликтов ресурсов.")

                with st.expander("➕ Добавить нового члена команды"):
                    with st.form("obraz_team_member_form", clear_on_submit=True):
                        member_name = st.text_input("Имя члена команды", key="obraz_member_name")
                        member_role = st.text_input("Роль в проекте", placeholder="Например: Сценарист, Монтажер", key="obraz_member_role")
                        
                        member_submitted = st.form_submit_button("Добавить в команду")
                        if member_submitted:
                            if member_name and member_role:
                                new_member = TeamMember(name=str(member_name), role=str(member_role))
                                st.session_state.client_profile.team.append(new_member) # type: ignore
                                st.success(f"Участник «{member_name}» добавлен в команду!")
                                st.rerun()
                            else:
                                st.error("Имя и роль не могут быть пустыми.")
                
                st.subheader("Состав команды")
                if st.session_state.client_profile.team: # type: ignore
                    for i, member in enumerate(st.session_state.client_profile.team): # type: ignore
                        col_name, col_role, col_action = st.columns([2, 2, 1])
                        col_name.write(member.name)
                        col_role.write(member.role)
                        if col_action.button("🗑️ Удалить", key=f"obraz_del_member_{i}"):
                            st.session_state.client_profile.team.pop(i) # type: ignore
                            st.rerun()
                else:
                    st.info("В вашей команде пока нет участников.")


# --- ГЛАВНЫЙ РОУТЕР ПРИЛОЖЕНИЯ ---
if not st.session_state.token and not st.session_state.offline_mode:
    render_login_screen()
elif st.session_state.processing:
    render_processing_overlay()
elif not st.session_state.profile_generated:
    # Если профиль не сгенерирован (и мы не в процессе), показываем стартовый экран
    render_startup_screen()
elif not st.session_state.wizard_complete:
    render_strategic_wizard()
else:
    render_main_workspace()
