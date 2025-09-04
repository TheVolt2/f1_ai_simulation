# race_model.py

import random
import numpy as np
import peremennue
from config import config_editor

class RaceModel:
    def __init__(self, random_seed=random.randint(1, 100)):
        self.random_seed = random_seed
        random.seed(self.random_seed)

        # === Параметры гонки ===
        self.TOTAL_LAPS = config_editor["TOTAL_LAPS"]
        self.BASE_LAP_TIME = config_editor["BASE_LAP_TIME"]
        self.TIME_PENALTY_PER_PERCENT_WEAR = config_editor["TIME_PENALTY_PER_PERCENT_WEAR"]
        self.PIT_STOP_EXTRA_TIME_AVG = config_editor["PIT_STOP_EXTRA_TIME_AVG"]
        self.REQUIRED_PIT_STOPS = config_editor["REQUIRED_PIT_STOPS"]
        self.RESERVE_PIT_STOP = config_editor["RESERVE_PIT_STOP"]
        self.MIN_RAIN_DURATION = config_editor["MIN_RAIN_DURATION"]
        self.MAX_RAIN_DURATION = config_editor["MAX_RAIN_DURATION"]
        self.MIN_STINT_LENGTH = config_editor["MIN_STINT_LENGTH"]

        # === Типы шин и их износ ===
        self.TIRE_TYPES = peremennue.TIRE_TYPES
        self.TIRE_WEAR_RATE = peremennue.TIRE_WEAR_RATE
        self.TIRE_LIFESPAN = peremennue.TIRE_LIFESPAN

        # === Штрафы за несоответствие шин и погоды ===
        self.TIRE_MISMATCH_PENALTY = peremennue.TIRE_MISMATCH_PENALTY

        # === Погода ===
        self.WEATHER_TYPES = ['dry', 'light_rain', 'medium_rain', 'heavy_rain']
        self.WEATHER_PROBS_TRANSITION = {
            'dry': {'dry': 0.85, 'light_rain': 0.15},
            'light_rain': {'dry': 0.1, 'light_rain': 0.5, 'medium_rain': 0.4},
            'medium_rain': {'light_rain': 0.2, 'medium_rain': 0.5, 'heavy_rain': 0.3},
            'heavy_rain': {'medium_rain': 0.4, 'heavy_rain': 0.6}
        }
        self.fixed_weather_sequence = self.generate_weather_sequence()

    def generate_weather_sequence(self):
        weather = ['dry'] * self.TOTAL_LAPS
        current = 'dry'
        rain_start = -1
        for lap in range(self.TOTAL_LAPS):
            if current == 'dry' and random.random() < 0.05 and lap < self.TOTAL_LAPS - 15:
                current = 'light_rain'
                rain_start = lap
            elif current in ['light_rain', 'medium_rain', 'heavy_rain']:
                if (rain_start != -1 and lap - rain_start >= random.randint(self.MIN_RAIN_DURATION,
                                                                            self.MAX_RAIN_DURATION)
                        and random.random() < 0.3):
                    current = 'dry'
                    rain_start = -1
                else:
                    probs = self.WEATHER_PROBS_TRANSITION[current]
                    current = random.choices(list(probs.keys()), weights=list(probs.values()))[0]
            weather[lap] = current
        return weather

    def _get_optimal_tire(self, weather_condition):
        optimal_tires = {
            'dry': 'Soft',
            'light_rain': 'Intermediate',
            'medium_rain': 'Wet',
            'heavy_rain': 'Wet'
        }
        return optimal_tires.get(weather_condition, 'Soft')

    def _run_simulation(self, individual):
        total_time = 0
        pit_stop_laps = sorted(individual)

        current_tire = 'Medium'
        tire_wear = 0
        tire_age = 0
        pit_stop_count = 0
        last_pit_lap = 0
        is_dnf = False

        emergency_pit_stop_used = False

        weather = self.fixed_weather_sequence

        lap_data = []

        for lap in range(self.TOTAL_LAPS):
            current_weather = weather[lap]
            lap_time = 0
            pit_time = 0
            status = ''

            # Логика экстренного пит-стопа имеет приоритет
            if tire_wear > 95 and not emergency_pit_stop_used:
                current_tire = 'Hard'
                tire_wear = 0
                tire_age = 0
                pit_time = self.PIT_STOP_EXTRA_TIME_AVG
                pit_stop_count += 1
                last_pit_lap = lap
                status = "🚨 Аварийный пит-стоп"
                emergency_pit_stop_used = True
                emergency_pit_stop_triggered = True

            # Логика планового пит-стопа
            if (lap + 1) in pit_stop_laps:
                pit_stop_count += 1
                pit_time = self.PIT_STOP_EXTRA_TIME_AVG

                next_stint_length = (pit_stop_laps[pit_stop_count - 1] if pit_stop_count - 1 < len(
                    pit_stop_laps) else self.TOTAL_LAPS) - lap

                forecast_weather = weather[lap:lap + next_stint_length]

                if 'dry' in forecast_weather:
                    if 'heavy_rain' in forecast_weather or 'medium_rain' in forecast_weather:
                        current_tire = 'Wet'
                    elif 'light_rain' in forecast_weather:
                        current_tire = 'Intermediate'
                    else:
                        current_tire = 'Soft'
                elif 'light_rain' in forecast_weather:
                    current_tire = 'Intermediate'
                else:
                    current_tire = 'Wet'

                tire_wear = 0
                tire_age = 0
                last_pit_lap = lap
                status = "🔄 Плановый пит-стоп"

            # Проверка на взрыв
            if tire_age > self.TIRE_LIFESPAN.get(current_tire, 50):
                is_dnf = True
                status = "💥 Взрыв шин! Сход!"
                break

            # Динамическое время круга (90-99 секунд)
            lap_time = random.uniform(90, 99)

            # Штраф за износ
            lap_time += self.TIME_PENALTY_PER_PERCENT_WEAR * tire_wear

            # Штраф за несоответствие шин
            penalty_key = (current_weather, current_tire)
            lap_time += self.TIRE_MISMATCH_PENALTY.get(penalty_key, 0)

            # Увеличение износа и возраста шин
            tire_wear += self.TIRE_WEAR_RATE.get(current_tire, 0)
            tire_age += 1

            # Проверка на перегрев (ужесточено)
            if tire_wear >= 100:
                is_dnf = True
                status = "💥 Перегрев шин! Сход!"
                break

            total_time += lap_time + pit_time

            lap_data.append({
                'lap_num': lap + 1,
                'weather': current_weather,
                'tire_type': current_tire,
                'tire_wear': tire_wear,
                'tire_age': tire_age,
                'lap_time': lap_time,
                'pit_time': pit_time,
                'total_time': total_time,
                'pit_stops_count': pit_stop_count,
                'status': status if status else '🟢 Обычный круг'
            })

        # Увеличенные штрафы за несоблюдение правил
        if is_dnf:
            # Штраф в зависимости от того, сколько кругов пройдено
            # Чем больше кругов, тем меньше штраф
            penalty = 5000000 - (10000 * len(lap_data))
            if penalty < 0:
                penalty = 0
            total_time += penalty

        final_pit_stop_target = self.REQUIRED_PIT_STOPS
        if emergency_pit_stop_used:
            final_pit_stop_target += 1

        if pit_stop_count != final_pit_stop_target:
            total_time += 15000 * abs(pit_stop_count - final_pit_stop_target)

        return total_time, pit_stop_count, is_dnf, lap_data

    def evaluate_strategy(self, individual):
        total_time, _, _, _ = self._run_simulation(individual)
        return total_time,