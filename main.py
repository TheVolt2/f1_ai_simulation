# main.py
from race_engine import RaceEngine
from agent_ga import AgentGA
from race_visualizer import RaceVisualizer
from leaderboard_manager import update_leaderboard
from config import config_editor

if __name__ == "__main__":
    car_names = [f"Agent-{i + 1}" for i in range(10)]
    engine = RaceEngine(car_names)

    print("Шаг 1: Каждая нейросеть разрабатывает свою стратегию...")
    agents = {name: AgentGA(name, engine) for name in car_names}

    strategies = {}
    for name, agent in agents.items():
        best_strategy = agent.find_best_strategy()
        strategies[name] = best_strategy
        print(f"✅ {name}: Стратегия найдена - {best_strategy}")

    print("\nШаг 2: Нейросети выходят на старт!")
    for name, strategy in strategies.items():
        engine.set_strategy(name, strategy)

    cars_final, race_history = engine.run_race_lap_by_lap()

    print("\nШаг 3: Гонка завершена!")
    final_standings = sorted(cars_final, key=lambda c: c.position)

    print("\n🏁 Финальные результаты гонки:")
    for car in final_standings:
        if not car.is_dnf:
            print(f"Позиция {car.position}: {car.name} - Общее время: {car.total_time:.2f} сек.")
        else:
            print(f"Позиция {car.position}: {car.name} - Сход на круге {car.dnf_lap}")

    winner = final_standings[0]

    # Сбор данных для лидерборда
    if not winner.is_dnf:
        winner_race_history = [lap_data for lap_data in race_history[-1] if lap_data['name'] == winner.name]

        # Нахождение лучшего времени круга
        best_lap_time = float('inf')
        for lap_data in race_history:
            for car_data in lap_data:
                if car_data['name'] == winner.name and not car_data['is_dnf']:
                    lap_time = car_data.get('lap_time')
                    if lap_time and lap_time < best_lap_time:
                        best_lap_time = lap_time

        update_leaderboard(
            winner_name=winner.name,
            total_time=winner.total_time,
            best_lap_time=best_lap_time if best_lap_time != float('inf') else None,
            total_laps=winner.current_lap + 1,
            strategy=strategies[winner.name]
        )

    app = RaceVisualizer(car_names, race_history, strategies)
    app.mainloop()