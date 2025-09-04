# f1_ai_simulation

A Python-based simulation of a car race where AI agents, trained using a Genetic Algorithm, compete to find the optimal pit-stop strategy.

## 🏁 Overview

This project simulates a car race where 10 AI agents compete against each other. Each agent is a neural network that uses a **Genetic Algorithm (GA)** to evolve its racing strategy, primarily focusing on pit-stop timing. The simulation includes dynamic elements like tire wear, weather changes (dry, rain), and pit-stop penalties, making the race outcome highly dependent on a smart strategy.

The project consists of several key components:
* **`RaceEngine`**: The core simulation that handles lap timings, tire degradation, and weather effects.
* **`AgentGA`**: The neural network and genetic algorithm that finds the best strategy for each agent.
* **`RaceVisualizer`**: A GUI built with `tkinter` that provides a real-time visualization of the race and displays the final results.
* **`LeaderboardManager`**: Manages the `leaderboard.json` file, which stores the top-performing agents.

## ⚙️ How It Works

1.  **Strategy Evolution**: Before the race starts, each of the 10 neural networks runs its own genetic algorithm to determine the optimal laps for pit stops.
2.  **Race Simulation**: The `RaceEngine` runs the race lap by lap, applying penalties for tire wear and inappropriate tire choices based on the current weather.
3.  **Real-Time Visualization**: The `RaceVisualizer` displays the race in real-time, showing car positions and tire strategy for each agent.
4.  **Leaderboard**: After the race, the winner's data (total time, best lap, strategy) is added to a global leaderboard, which is sorted by the best lap time.

## 🚀 Getting Started

### Prerequisites

* Python 3.x
* `tkinter` (usually included with Python)

### Installation

1.  Clone the repository:
    ```bash
    git clone [https://github.com/YOUR_USERNAME/neural-race-simulation.git](https://github.com/YOUR_USERNAME/neural-race-simulation.git)
    cd neural-race-simulation
    ```

2.  Run the simulation:
    ```bash
    python main.py
    ```

The GUI will pop up and the simulation will begin. Once the race is over, the leaderboard will be displayed.

## 📁 File Structure

* `main.py`: The entry point of the application.
* `race_engine.py`: Core logic for the race simulation.
* `agent_ga.py`: Contains the logic for the genetic algorithm.
* `race_visualizer.py`: Handles the graphical user interface.
* `leaderboard_manager.py`: Manages the leaderboard data file.
* `config.py`: Configuration settings (e.g., total laps, pit stop time).
* `peremennue.py`: Variables for tire wear and weather penalties.
* `leaderboard.json`: The data file for the Hall of Fame.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY/issues).

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---
