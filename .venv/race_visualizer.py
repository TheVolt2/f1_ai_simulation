# race_visualizer.py
import tkinter as tk
from tkinter import ttk
import random
import json
import os
from config import config_editor
import peremennue


class RaceVisualizer(tk.Tk):
    def __init__(self, car_names, lap_data, strategies):
        super().__init__()
        self.title("Гонка 10 нейросетей")
        self.geometry("1000x800")

        self.car_colors = {
            'Agent-1': '#FF0000', 'Agent-2': '#0000FF', 'Agent-3': '#FFFF00',
            'Agent-4': '#00FF00', 'Agent-5': '#FFA500', 'Agent-6': '#800080',
            'Agent-7': '#00FFFF', 'Agent-8': '#FFC0CB', 'Agent-9': '#A52A2A',
            'Agent-10': '#FFFFFF'
        }
        self.tire_names = {'Soft': 'S', 'Medium': 'M', 'Hard': 'H', 'Intermediate': 'I', 'Wet': 'W'}

        self.lap_data = lap_data
        self.strategies = strategies
        self.current_lap_index = 0
        self.total_laps = config_editor["TOTAL_LAPS"]

        self.dnf_agents = {}
        self.pit_stop_elements = {name: [] for name in car_names}

        # Фрейм для гонки
        race_frame = ttk.Frame(self)
        race_frame.pack(side=tk.TOP, pady=10)
        self.canvas = tk.Canvas(race_frame, bg="black", width=950, height=150)
        self.canvas.pack()

        self.car_dots = {}
        self._draw_track_with_laps()
        self._create_car_dots(car_names)

        self.info_label = ttk.Label(self, text="Круг: 0 из 150", font=("Arial", 12))
        self.info_label.pack(side=tk.TOP, pady=5)

        # Фрейм для стратегий
        strategy_frame = ttk.Frame(self)
        strategy_frame.pack(pady=10)
        self.strategy_canvas = tk.Canvas(strategy_frame, bg="gray", width=950, height=250)
        self.strategy_canvas.pack()

        self.strategy_bars = {}
        self._draw_strategy_bars()

        # Фрейм для таблицы лидерборда
        self.leaderboard_frame = ttk.Frame(self)
        self.leaderboard_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        self.leaderboard_frame.pack_forget()  # Сначала скрываем

        ttk.Label(self.leaderboard_frame, text="🏆 Зал Славы (leaderboard.json)", font=("Arial", 12, "bold")).pack()

        columns = ("date", "winner", "total_time", "best_lap", "total_laps")
        self.tree = ttk.Treeview(self.leaderboard_frame, columns=columns, show="headings")

        self.tree.heading("date", text="Дата")
        self.tree.heading("winner", text="Победитель")
        self.tree.heading("total_time", text="Общее время", command=lambda: self.sort_by_column("total_time", False))
        self.tree.heading("best_lap", text="Лучший круг", command=lambda: self.sort_by_column("best_lap", False))
        self.tree.heading("total_laps", text="Кругов")

        self.tree.column("date", width=150, anchor=tk.CENTER)
        self.tree.column("winner", width=100, anchor=tk.W)
        self.tree.column("total_time", width=100, anchor=tk.CENTER)
        self.tree.column("best_lap", width=100, anchor=tk.CENTER)
        self.tree.column("total_laps", width=70, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True)

        self.after(100, self.update_visualization)

    def format_time(self, seconds):
        if not isinstance(seconds, (int, float)):
            return "N/A"
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{h:02}:{m:02}:{s:02}.{ms:03}"

    def sort_by_column(self, col, reverse):
        if col == "total_time":
            data = [(float(self.tree.set(item, "total_time").replace(':', '').replace('.', '')), item) for item in
                    self.tree.get_children('')]
        elif col == "best_lap":
            data = []
            for item in self.tree.get_children(''):
                value = self.tree.set(item, "best_lap")
                if value == 'N/A':
                    data.append((float('inf'), item))
                else:
                    data.append((float(value), item))

        data.sort(reverse=reverse)
        for index, (val, item) in enumerate(data):
            self.tree.move(item, '', index)
        self.tree.heading(col, command=lambda: self.sort_by_column(col, not reverse))

    def _draw_track_with_laps(self):
        self.canvas.create_line(25, 75, 975, 75, width=8, fill="gray")
        for i in range(self.total_laps + 1):
            x = 25 + (950 * i / self.total_laps)
            self.canvas.create_line(x, 70, x, 80, fill="white", width=2)
            if i % 25 == 0:
                self.canvas.create_text(x, 95, text=str(i), fill="white", font=("Arial", 9))

    def _create_car_dots(self, car_names):
        y_step = 12
        y_start = 75 - (len(car_names) * y_step) / 2
        for i, name in enumerate(car_names):
            y_pos = y_start + i * y_step
            dot = self.canvas.create_oval(
                20, y_pos - 3, 30, y_pos + 3, fill=self.car_colors[name], outline="white"
            )
            self.car_dots[name] = dot
            self.canvas.create_text(
                15, y_pos, text=name, fill=self.car_colors[name], font=("Arial", 8, "bold"), anchor="e"
            )

    def _draw_strategy_bars(self):
        self.strategy_bars = {}
        bar_width = 80
        padding = 15
        total_width = bar_width * 10 + padding * 9
        start_x = (950 - total_width) / 2

        for i, (name, strategy) in enumerate(self.strategies.items()):
            x1 = start_x + i * (bar_width + padding)
            x2 = x1 + bar_width
            y1 = 20
            y2 = 230

            self.strategy_canvas.create_rectangle(x1, y1, x2, y2, fill="#333333", outline="")
            self.strategy_canvas.create_text(x1 + bar_width / 2, y1 - 10, text=name, fill="white",
                                             font=("Arial", 9, "bold"))

            progress_bar = self.strategy_canvas.create_rectangle(x1, y2, x2, y2, fill=self.car_colors[name], outline="")
            self.strategy_bars[name] = progress_bar

            stints = [0] + strategy + [self.total_laps]
            for j in range(len(stints) - 1):
                start_lap = stints[j]
                end_lap = stints[j + 1]

                stint_laps = end_lap - start_lap
                if stint_laps > peremennue.TIRE_LIFESPAN.get('Medium', 40):
                    tire_type = 'Hard'
                elif stint_laps > peremennue.TIRE_LIFESPAN.get('Soft', 25):
                    tire_type = 'Medium'
                else:
                    tire_type = 'Soft'

                y_pos = y2 - (end_lap / self.total_laps) * (y2 - y1)
                pit_line = self.strategy_canvas.create_line(x1 - 5, y_pos, x2 + 5, y_pos, fill="red", width=2)

                pit_label = self.strategy_canvas.create_text(x1 + bar_width / 2, y_pos - 5,
                                                             text=f"Pit {end_lap} ({self.tire_names.get(tire_type, tire_type)})",
                                                             fill="white", font=("Arial", 7))

                self.pit_stop_elements[name].append({'lap': end_lap, 'line': pit_line, 'label': pit_label})

            self.strategy_canvas.create_text(x1 + bar_width / 2, y2 + 10, text=f"Кругов: 0",
                                             fill="white", font=("Arial", 8), tag=f"lap_count_{name}")

    def update_visualization(self):
        if self.current_lap_index >= len(self.lap_data):
            self.info_label.config(text="Гонка завершена!")
            self._populate_leaderboard_table()
            return

        lap_info = self.lap_data[self.current_lap_index]
        current_lap_num = self.current_lap_index + 1

        self.info_label.config(text=f"Круг: {current_lap_num} из {self.total_laps}")

        active_cars = [c for c in lap_info if not c['is_dnf']]
        if active_cars:
            min_time = min(c['total_time'] for c in active_cars)
            max_time = max(c['total_time'] for c in active_cars)
        else:
            min_time = 0
            max_time = 0

        for car_info in lap_info:
            car_name = car_info['name']
            dot = self.car_dots[car_name]

            if car_name in self.dnf_agents:
                continue

            if car_info['is_dnf']:
                self.dnf_agents[car_name] = car_info['dnf_lap']
                self.canvas.itemconfigure(dot, fill="red", outline="red")
            else:
                total_time = car_info['total_time']

                if max_time == min_time:
                    progress_norm = 1.0
                else:
                    progress_norm = 1.0 - ((total_time - min_time) / (max_time - min_time + 1e-9))

                total_progress = (current_lap_num / self.total_laps) + (progress_norm / self.total_laps)
                x_pos = 25 + (950 * total_progress)
                x_pos = min(x_pos, 975)

                self.canvas.coords(dot, x_pos - 3, self.canvas.coords(dot)[1], x_pos + 3, self.canvas.coords(dot)[3])

        for name, bar in self.strategy_bars.items():
            if name in self.dnf_agents:
                dnf_lap = self.dnf_agents[name]
                progress_height = (dnf_lap / self.total_laps) * 210
                bar_coords = self.strategy_canvas.coords(bar)
                self.strategy_canvas.coords(bar, bar_coords[0], bar_coords[3] - progress_height, bar_coords[2],
                                            bar_coords[3])
                self.strategy_canvas.itemconfigure(f"lap_count_{name}", text=f"СХОД на {dnf_lap}")

                for pit in self.pit_stop_elements[name]:
                    if pit['lap'] > dnf_lap:
                        self.strategy_canvas.itemconfigure(pit['line'], state='hidden')
                        self.strategy_canvas.itemconfigure(pit['label'], state='hidden')
            else:
                progress_height = (self.current_lap_index + 1) / self.total_laps * 210
                bar_coords = self.strategy_canvas.coords(bar)
                self.strategy_canvas.coords(bar, bar_coords[0], bar_coords[3] - progress_height, bar_coords[2],
                                            bar_coords[3])
                self.strategy_canvas.itemconfigure(f"lap_count_{name}", text=f"Кругов: {self.current_lap_index + 1}")

        self.current_lap_index += 1
        self.after(200, self.update_visualization)

    def _populate_leaderboard_table(self):
        self.leaderboard_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        file_path = "leaderboard.json"
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for entry in data:
                        total_laps_text = str(entry.get('total_laps', 'N/A'))
                        if total_laps_text != 'N/A' and int(total_laps_text) < self.total_laps:
                            total_laps_text = f"Сход ({total_laps_text})"

                        self.tree.insert("", tk.END, values=(
                            entry.get('date', 'N/A'),
                            entry.get('winner', 'N/A'),
                            self.format_time(entry.get('total_time')),
                            entry.get('best_lap_time', 'N/A'),
                            total_laps_text
                        ))
            except (json.JSONDecodeError, IOError) as e:
                self.tree.insert("", tk.END, values=(f"Ошибка: {e}", "", "", "", ""))
        else:
            self.tree.insert("", tk.END, values=("Файл leaderboard.json не найден.", "", "", "", ""))