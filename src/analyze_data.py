import pandas as pd
import numpy as np
import json
from pathlib import Path

def analyze_sessions(sessions_file):
    """
    Analyzes game session data to extract player patterns.
    """
    if not Path(sessions_file).exists():
        return {"error": "Sessions file not found"}

    try:
        if Path(sessions_file).stat().st_size == 0:
            return {"error": "No session data available (empty file)"}
            
        with open(sessions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return {"error": f"Failed to load sessions: {e}"}

    if not data:
        return {"error": "No session data available"}

    # Ensure data is a list of records for pandas
    if isinstance(data, dict):
        data = [data]
    elif not isinstance(data, list):
        return {"error": "Invalid session data format"}

    # Create a DataFrame from sessions
    df = pd.DataFrame(data)

    # Basic analysis
    summary = {
        "total_sessions": len(df),
        "average_score": df['final_score'].mean() if 'final_score' in df else 0,
        "max_score": df['final_score'].max() if 'final_score' in df else 0,
        "outcomes": df['outcome'].value_counts().to_dict() if 'outcome' in df else {}
    }

    # Analyze player positions if available
    if 'player_positions' in df.columns:
        all_positions = []
        for pos_list in df['player_positions']:
            if isinstance(pos_list, list):
                all_positions.extend(pos_list)
        
        if all_positions:
            pos_array = np.array(all_positions)
            summary['avg_position'] = pos_array.mean(axis=0).tolist()
            # Find the most visited zone (simplified)
            # Dividing level width 3200 into 10 zones
            zones = (pos_array[:, 0] // 320).astype(int)
            unique, counts = np.unique(zones, return_counts=True)
            zone_popularity = dict(zip(unique.tolist(), counts.tolist()))
            summary['top_zone'] = int(unique[np.argmax(counts)])
            summary['zone_distribution'] = {int(k): int(v) for k, v in zone_popularity.items()}

    return summary

if __name__ == "__main__":
    # Test analysis if run directly
    project_root = Path(__file__).parent.parent
    sessions_path = project_root / "data" / "sessions.json"
    results = analyze_sessions(sessions_path)
    print(json.dumps(results, indent=2))
