
import json
from dataclasses import asdict
from core_logic import (
    IngestionEngine, 
    BlueOceanEngine, 
    HarmonyDiagnosticEngine, 
    CommerceEngine, 
    AIScenarioProducer, 
    CalendarEngine
)

# --- ПЕРЕКЛЮЧАТЕЛЬ РЕЖИМА ---
# True: использовать мок-данные, не обращаясь к AI.
# False: пытаться использовать реальные AI-запросы (потребует API-ключа в .env)
OFFLINE_MODE = True

# ==============================================================================
# --- ГЛАВНЫЙ КОНВЕЙЕР (ТОЧКА ВХОДА) ---
# ==============================================================================
if __name__ == "__main__":
    print(f"🚀 Скрипт запущен в {'ОФФЛАЙН' if OFFLINE_MODE else 'ОНЛАЙН'} режиме!")
    # --- ШАГ 1-3: СТРАТЕГИЧЕСКАЯ ДИАГНОСТИКА ---
    ingestion_engine = IngestionEngine(offline_mode=OFFLINE_MODE)
    client_profile = ingestion_engine.process("""
    Текст из Мастер-Опросника... Моя манера общения - провокационная, но с позиции наставника. 
    Я часто повторяю фразы "Работаем", "Это база". 
    Ненавижу, когда говорят "короче".
    """)
    
    blue_ocean_engine = BlueOceanEngine(offline_mode=OFFLINE_MODE)
    client_profile.positioning_matrix = blue_ocean_engine.process("Текст про конкурентов...", client_profile)
    
    harmony_engine = HarmonyDiagnosticEngine()
    client_profile = harmony_engine.process(client_profile)
    
    # --- ШАГ 4: ПРОЕКТИРОВАНИЕ ПРОДУКТОВОЙ ЛИНЕЙКИ ---
    commerce_engine = CommerceEngine(offline_mode=OFFLINE_MODE)
    product_ladder = commerce_engine.process(client_profile)
    client_profile.products = [asdict(p) for p in [product_ladder.lead_magnet, product_ladder.tripwire, product_ladder.core_offer, product_ladder.high_ticket] if p]
    
    print("\n" + "="*60)
    print("--- Итоговый Client_Profile_Hub (с Продуктами) ---")
    print(json.dumps(asdict(client_profile), indent=2, ensure_ascii=False, default=str))
    
    # --- ШАГ 5: ГЕНЕРАЦИЯ КОНТЕНТА, ПРОДВИГАЮЩЕГО ПРОДУКТ (Product-Led Content) ---
    print("\n" + "="*60)
    print("--- ТАКТИЧЕСКИЙ РЕЖИМ: ГЕНЕРАЦИЯ ПРОДАЮЩЕГО КОНТЕНТА ---")
    print("="*60)
    
    scenario_producer = AIScenarioProducer(offline_mode=OFFLINE_MODE)
    
    # Выбираем продукт для продвижения (например, Трипвайер)
    product_to_promote = product_ladder.tripwire
    
    if product_to_promote:
        selected_points = {
            "idea": f"Продвижение '{product_to_promote.name}' через демонстрацию системного подхода",
            "content_carrier": "Шортс",
        }
        generated_script = scenario_producer.process(client_profile, selected_points, product_to_promote)
        
        print("\n--- ГОТОВЫЙ СЦЕНАРИЙ (Product-Led) ---")
        print(generated_script)
    else:
        print("⚠️ Продукт для продвижения не найден.")

    # --- ШАГ 6: ДЕКОМПОЗИЦИЯ В ЗАДАЧИ (Операционное Ядро) ---
    print("\n" + "="*60)
    print("--- ОПЕРАЦИОННОЕ ЯДРО: ДЕКОМПОЗИЦИЯ В ЗАДАЧИ ---")
    print("="*60)

    calendar_engine = CalendarEngine(offline_mode=OFFLINE_MODE)
    project_tasks = calendar_engine.decompose_script_to_tasks(generated_script, selected_points)

    print("\n--- ПЛАН ПРОЕКТА (СПИСОК ЗАДАЧ) ---")
    for i, task in enumerate(project_tasks, 1):
        print(f"{i}. {task.description} (Статус: {task.status})")
