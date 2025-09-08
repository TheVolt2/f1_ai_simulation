# race_engine.py
import random
import numpy as np
from config import config_editor
from peremennue import TIRE_WEAR_RATE, TIRE_MISMATCH_PENALTY, TIRE_LIFESPAN


class RaceCar:
    """Представляет одну гоночную машину в симуляции."""

    def __init__(self, name, start_position=0):
        self.name = name
        self.current_lap = 0
        self.total_time = 0
        self.current_tire = 'Medium'
        self.tire_wear = 0
        self.tire_age = 0
        self.pit_stop_count = 0
        self.is_dnf = False
        self.dnf_lap = None
        self.last_pit_lap = 0
        self.status = "🟢 Обычный круг"
        self.position = start_position
        self.emergency_pit_stop_used = False


class RaceEngine:
    """Управляет симуляцией гонки для нескольких машин."""

    def __init__(self, car_names, random_seed=None):
        if random_seed is None:
            self.random_seed = random.randint(1, 1000)
        else:
            self.random_seed = random_seed
        random.seed(self.random_seed)

        self.TOTAL_LAPS = config_editor["TOTAL_LAPS"]
        self.PIT_STOP_EXTRA_TIME_AVG = config_editor["PIT_STOP_EXTRA_TIME_AVG"]
        self.TIME_PENALTY_PER_PERCENT_WEAR = config_editor["TIME_PENALTY_PER_PERCENT_WEAR"]

        self.weather_sequence = self.generate_weather_sequence()
        self.cars = [RaceCar(name) for name in car_names]
        self.pit_stop_strategies = {}

    def generate_weather_sequence(self):
        weather = ['dry'] * self.TOTAL_LAPS
        current = 'dry'
        min_rain_duration = config_editor["MIN_RAIN_DURATION"]
        max_rain_duration = config_editor["MAX_RAIN_DURATION"]
        weather_probs = {'dry': {'dry': 0.85, 'light_rain': 0.15},
                         'light_rain': {'dry': 0.1, 'light_rain': 0.5, 'medium_rain': 0.4},
                         'medium_rain': {'light_rain': 0.2, 'medium_rain': 0.5, 'heavy_rain': 0.3},
                         'heavy_rain': {'medium_rain': 0.4, 'heavy_rain': 0.6}}

        rain_start = -1
        for lap in range(self.TOTAL_LAPS):
            if current == 'dry' and random.random() < 0.05 and lap < self.TOTAL_LAPS - 15:
                current = 'light_rain'
                rain_start = lap
            elif current in ['light_rain', 'medium_rain', 'heavy_rain']:
                if (rain_start != -1 and lap - rain_start >= random.randint(min_rain_duration, max_rain_duration)
                        and random.random() < 0.3):
                    current = 'dry'
                    rain_start = -1
                else:
                    probs = weather_probs[current]
                    current = random.choices(list(probs.keys()), weights=list(probs.values()))[0]
            weather[lap] = current
        return weather

    def set_strategy(self, car_name, strategy):
        self.pit_stop_strategies[car_name] = sorted(strategy)

    def run_race_lap_by_lap(self):
        race_data = []
        for lap in range(self.TOTAL_LAPS):
            current_lap_data = []
            for car in self.cars:
                if car.is_dnf:
                    current_lap_data.append({
                        'name': car.name,
                        'lap_num': lap + 1,
                        'total_time': car.total_time,
                        'status': "❌ Сход",
                        'is_dnf': True,
                        'dnf_lap': car.dnf_lap,
                        'lap_time': 0,
                        'current_tire': car.current_tire,  # Добавлено
                        'tire_wear': car.tire_wear  # Добавлено
                    })
                    continue

                lap_time = random.uniform(90, 99)
                pit_time = 0
                status = '🟢 Обычный круг'

                pit_stop_laps = self.pit_stop_strategies.get(car.name, [])

                if car.tire_age > TIRE_LIFESPAN.get(car.current_tire, 50):
                    car.is_dnf = True
                    car.dnf_lap = lap + 1
                    status = "💥 Взрыв шин! Сход!"
                    car.total_time += 5000000

                elif car.tire_wear > 95 and not car.emergency_pit_stop_used:
                    car.current_tire = 'Hard'
                    car.tire_wear = 0
                    car.tire_age = 0
                    pit_time = self.PIT_STOP_EXTRA_TIME_AVG
                    car.pit_stop_count += 1
                    car.last_pit_lap = lap
                    status = "🚨 Аварийный пит-стоп"
                    car.emergency_pit_stop_used = True

                elif (lap + 1) in pit_stop_laps and lap + 1 != self.TOTAL_LAPS:
                    pit_stop_idx = pit_stop_laps.index(lap + 1)
                    stint_laps_remaining = 0
                    if pit_stop_idx < len(pit_stop_laps) - 1:
                        stint_laps_remaining = pit_stop_laps[pit_stop_idx + 1] - (lap + 1)
                    else:
                        stint_laps_remaining = self.TOTAL_LAPS - (lap + 1)

                    forecast_weather = self.weather_sequence[lap + 1:lap + 1 + stint_laps_remaining]

                    if 'dry' in forecast_weather:
                        if 'heavy_rain' in forecast_weather or 'medium_rain' in forecast_weather:
                            car.current_tire = 'Wet'
                        elif 'light_rain' in forecast_weather:
                            car.current_tire = 'Intermediate'
                        else:
                            car.current_tire = 'Soft'
                    elif 'light_rain' in forecast_weather:
                        car.current_tire = 'Intermediate'
                    else:
                        car.current_tire = 'Wet'

                    car.tire_wear = 0
                    car.tire_age = 0
                    pit_time = self.PIT_STOP_EXTRA_TIME_AVG
                    car.pit_stop_count += 1
                    car.last_pit_lap = lap
                    status = "🔄 Плановый пит-стоп"

                lap_time += self.TIME_PENALTY_PER_PERCENT_WEAR * car.tire_wear
                penalty_key = (self.weather_sequence[lap], car.current_tire)
                lap_time += TIRE_MISMATCH_PENALTY.get(penalty_key, 0)

                car.total_time += lap_time + pit_time
                car.tire_wear += TIRE_WEAR_RATE.get(car.current_tire, 0)
                car.tire_age += 1
                car.status = status

                current_lap_data.append({
                    'name': car.name,
                    'lap_num': lap + 1,
                    'total_time': car.total_time,
                    'status': car.status,
                    'is_dnf': car.is_dnf,
                    'dnf_lap': car.dnf_lap,
                    'lap_time': lap_time + pit_time,
                    'current_tire': car.current_tire,  # Добавлено
                    'tire_wear': car.tire_wear  # Добавлено
                })

            sorted_cars = sorted(self.cars, key=lambda c: c.total_time)
            for i, c in enumerate(sorted_cars):
                c.position = i + 1

            race_data.append(current_lap_data)

        return self.cars, race_data