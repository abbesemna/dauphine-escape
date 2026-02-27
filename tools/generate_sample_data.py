import json
import random
from datetime import datetime, timedelta
from pathlib import Path

def generate_session(index):
    ts = (datetime.now() - timedelta(hours=index)).isoformat()
    duration = random.randint(30, 120)
    score = random.randint(50, 500)
    
    events = []
    items = ['idea', 'book', 'coffee', 'mind']
    for _ in range(random.randint(3, 8)):
        events.append({
            "time": random.uniform(5, duration),
            "type": "COLLECT",
            "item": random.choice(items)
        })
    
    threat_history = []
    for t in range(0, duration, 2):
        threat_history.append((float(t), random.uniform(10, 90)))
        
    ai_decisions = []
    states = ["PATROL", "CHASE", "ATTACK"]
    for _ in range(random.randint(2, 5)):
        ai_decisions.append({
            "time": random.uniform(0, duration),
            "state": random.choice(states)
        })
        
    return {
        "player_name": "ProPlayer",
        "timestamp": ts,
        "events": events,
        "threat_history": threat_history,
        "ai_decisions": ai_decisions,
        "final_score": score,
        "outcome": random.choice(["ESCAPED", "CAUGHT", "TIMEOUT"])
    }

def main():
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    sessions = [generate_session(i) for i in range(5)]
    
    with open(data_dir / "sessions.json", "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=2)
        
    print("Generated 5 synthetic sessions in data/sessions.json")

if __name__ == "__main__":
    main()
