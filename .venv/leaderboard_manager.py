# leaderboard_manager.py
import datetime
import json
import os

LEADERBOARD_FILE = "leaderboard.json"


def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_leaderboard(leaderboard):
    with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
        json.dump(leaderboard, f, indent=4)


def update_leaderboard(winner_name, total_time, best_lap_time, total_laps, strategy):
    """Updates the Hall of Fame with the new winner."""
    leaderboard = load_leaderboard()

    new_entry = {
        "date": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "winner": winner_name,
        "total_time": total_time,
        # "total_time_min" : (total_time-total_time//3600)//60,
        # "total_time_hrs" : total_time//3600,
        "best_lap_time": best_lap_time,
        "total_laps": total_laps,
        "strategy": strategy
    }

    #[total_time//3600, (total_time-total_time//3600)//60, total_time-(total_time-total_time//3600)//60]

    leaderboard.append(new_entry)
    leaderboard.sort(key=lambda x: x.get('best_lap_time', float('inf')))

    if len(leaderboard) > 10:
        leaderboard = leaderboard[:10]

    save_leaderboard(leaderboard)
    print("Результаты победителя обновлены в Зале Славы.")

    print("\n🏆 Зал Славы (Топ-10):")
    for i, entry in enumerate(leaderboard):
        print(f"{i + 1}. Победитель: {entry['winner']}")
        print(f"   Общее время: {entry['total_time']:.2f} сек")
        best_lap_time = entry.get('best_lap_time')
        print(f"   Лучший круг: {best_lap_time:.2f} сек" if best_lap_time is not None else "   Лучший круг: N/A")
        print(f"   Всего кругов: {entry['total_laps']}")
        print(f"   Стратегия: {entry['strategy']}")