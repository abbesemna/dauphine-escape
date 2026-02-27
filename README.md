# Dauphine Escape

Professional 2D arcade-style evasion game featuring predictive AI and real-time performance analytics.

## Overview

**Dauphine Escape** challenges players to navigate a virtual campus while being pursued by an adaptive AI "Exam". The project demonstrates the integration of pathfinding algorithms, predictive modeling, and data-driven gameplay.

---

## Core Features

- **Adaptive AI System**: Utilizes the A* algorithm for global pathfinding and real-time decision trees for tactical behavior.
- **Predictive Modeling**: Leverages NumPy for linear extrapolation, allowing the AI to anticipate player trajectories.
- **Advanced Analytics**: Automated session logging and data visualization using Pandas and Matplotlib.
- **Modular Architecture**: Clean, object-oriented codebase optimized for performance and maintainability.

---

## Technical Mechanics

### AI Behavior
The "Exam" entity operates through a sophisticated logic layer:
1. **Strategic Pathfinding**: Optimal route calculation via A* algorithm.
2. **Dynamic State Machine**: Context-aware transitions between `PATROL`, `CHASE`, and `ATTACK` modes.
3. **Trajectory Prediction**: Performance-optimized NumPy calculations to predict player positioning.

### Performance Tracking
Gameplay sessions are recorded with high-precision metrics:
- **Loot Efficiency**: Points collected per minute ratio.
- **AI Pressure Index**: Average threat level throughout the session.
- **Aggression Analysis**: AI state distribution and response times.

---

## Getting Started

### Prerequisites
Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Execution
Launch the primary game engine:
```bash
python -m src.main
```

### Analytical Tools
The `tools/` directory contains utility scripts for data analysis:
- **Session Analysis**: `python tools/analyze_data.py`
- **Installation Check**: `python tools/test_installation.py`

---

## Project Structure

- `src/`: Core game engine and entity modules.
- `assets/`: Optimized visual and auditory resources.
- `data/`: Automated session logs and analytical exports.
- `tools/`: Performance analysis and developmental utilities.
- `docs/`: Technical documentation and project specifications.

---

## Academic Context

Developed as an implementation study for **Paris Dauphine University**, focusing on AI implementations and data-driven game design.

---

## License

MIT License.
