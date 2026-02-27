"""
ADVANCED ANALYTICS - The Final Escape
Sophisticated game session analysis with deep metrics and premium visualizations.
"""
import json
import pandas as pd
from pathlib import Path
from collections import Counter
import datetime

try:
    import matplotlib.pyplot as plt
    import numpy as np
    import seaborn as sns
    HAS_ADVANCED_PLOT = True
except ImportError:
    HAS_ADVANCED_PLOT = False

# Paths
BASE = Path(__file__).parent.resolve()
DATA_DIR = BASE / "data"
SESSIONS_FILE = DATA_DIR / "sessions.json"
ANALYTICS_DIR = DATA_DIR / "analytics"

def load_all_sessions():
    """Loads consolidated and individual sessions."""
    sessions = []
    if SESSIONS_FILE.exists() and SESSIONS_FILE.stat().st_size > 0:
        try:
            with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                sessions = data if isinstance(data, list) else [data]
        except Exception as e:
            print(f"Warning: Could not load {SESSIONS_FILE}: {e}")

    for f in DATA_DIR.glob("session_*.json"):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                sessions.append(json.load(fp))
        except Exception:
            pass
    
    # Deduplicate by timestamp if exists
    unique_sessions = {}
    for s in sessions:
        ts = s.get('timestamp') or s.get('start_time')
        if ts:
            unique_sessions[ts] = s
        else:
            unique_sessions[id(s)] = s
            
    return list(unique_sessions.values())

def calculate_advanced_metrics(session):
    """Calculates premium metrics for a single session."""
    events = session.get('events', [])
    duration = 0
    if events:
        duration = max(e.get('time', 0) for e in events)
    elif 'threat_history' in session and session['threat_history']:
        duration = max(t[0] for t in session['threat_history'])
    
    score = session.get('final_score', 0)
    
    # 1. Loot Efficiency (Points per minute)
    efficiency = (score / (duration / 60)) if duration > 0 else 0
    
    # 2. AI Pressure Index (Avg threat level)
    threat_history = session.get('threat_history', [])
    avg_threat = np.mean([t[1] for t in threat_history]) if threat_history else 0
    
    # 3. Aggression Ratio (Time in ATTACK state / total time)
    # This requires state change logging
    ai_decisions = session.get('ai_decisions', [])
    
    return {
        "duration": duration,
        "efficiency": round(efficiency, 2),
        "avg_threat": round(avg_threat, 2),
        "outcome": session.get('outcome', 'UNKNOWN'),
        "score": score
    }

def plot_performance_timeline(session, index, out_dir):
    """Generates an event timeline for a session."""
    if not HAS_ADVANCED_PLOT: return
    
    events = session.get('events', [])
    threats = session.get('threat_history', [])
    decisions = session.get('ai_decisions', [])
    
    if not events and not threats: return

    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Plot Threat Level
    if threats:
        times = [t[0] for t in threats]
        vals = [t[1] for t in threats]
        ax1.plot(times, vals, color='#FF5A5A', alpha=0.6, label='Threat Level (%)', linewidth=2)
        ax1.fill_between(times, vals, alpha=0.1, color='#FF5A5A')
    
    ax1.set_xlabel('Time (seconds)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Menace / Pressure (%)', fontsize=12, color='#FF5A5A', fontweight='bold')
    ax1.set_ylim(0, 110)
    
    # Vertical lines for AI State Changes
    colors = {"PATROL": "#5A9BD5", "CHASE": "#FFB432", "ATTACK": "#FF5A5A"}
    for d in decisions:
        ax1.axvline(x=d['time'], color=colors.get(d['state'], '#888'), linestyle='--', alpha=0.5)
        ax1.text(d['time'], 102, d['state'], rotation=45, fontsize=8, color=colors.get(d['state'], '#888'))

    # Scatter for item collection
    if events:
        item_types = list(set(e['item'] for e in events if e['type'] == 'COLLECT'))
        item_colors = plt.cm.get_cmap('viridis', len(item_types))
        for i, itype in enumerate(item_types):
            it_times = [e['time'] for e in events if e['item'] == itype]
            ax1.scatter(it_times, [10]*len(it_times), label=f'Collected: {itype}', s=80, marker='D', edgecolors='white')

    plt.title(f"Gameplay Timeline - Session {index+1}", fontsize=16, fontweight='bold', pad=20)
    ax1.legend(loc='upper left', frameon=True, shadow=True)
    ax1.grid(True, alpha=0.2)
    
    plt.tight_layout()
    plt.savefig(out_dir / f"session_timeline_{index+1}.png", dpi=200)
    plt.close()

def plot_multisession_trends(all_metrics, out_dir):
    """Plots trends across multiple sessions."""
    if not HAS_ADVANCED_PLOT or len(all_metrics) < 2: return
    
    df = pd.DataFrame(all_metrics)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), sharex=True)
    
    # Score Trend
    sns.lineplot(data=df, x=df.index, y='score', marker='o', ax=ax1, color='#50DC78', linewidth=3)
    ax1.set_title('Score Progression', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Final Score')
    ax1.grid(True, alpha=0.3)
    
    # Efficiency Trend
    sns.barplot(data=df, x=df.index, y='efficiency', ax=ax2, palette='Blues_d')
    ax2.set_title('Loot Efficiency (Points / Min)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Efficiency Index')
    ax2.set_xlabel('Session Index')
    
    plt.tight_layout()
    plt.savefig(out_dir / "performance_trends.png", dpi=200)
    plt.close()

def main():
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
    
    sessions = load_all_sessions()
    if not sessions:
        print("No sessions found to analyze.")
        return
        
    print(f"--- ADVANCED ANALYTICS ENGINE ---")
    print(f"Processing {len(sessions)} unique sessions...\n")
    
    all_metrics = []
    for i, s in enumerate(sessions):
        metrics = calculate_advanced_metrics(s)
        all_metrics.append(metrics)
        
        # Plot individual timeline if enough data
        if s.get('threat_history') or s.get('events'):
            plot_performance_timeline(s, i, ANALYTICS_DIR)
            
    # Print Comparison Table
    df = pd.DataFrame(all_metrics)
    print("SESSION PERFORMANCE SUMMARY:")
    print(df[['score', 'duration', 'efficiency', 'avg_threat', 'outcome']].to_string())
    
    if len(sessions) > 1:
        print("\nTREND ANALYSIS:")
        avg_score = df['score'].mean()
        avg_eff = df['efficiency'].mean()
        print(f"Average Score: {avg_score:.1f}")
        print(f"Average Efficiency: {avg_eff:.2f} pts/min")
        
        # Check for improvement
        if len(df) >= 2:
            last = df.iloc[-1]['score']
            prev = df.iloc[-2]['score']
            diff = ((last - prev) / prev * 100) if prev > 0 else 0
            trend = "INCREASING +" if diff > 0 else "DECREASING -"
            print(f"Latest Score Trend: {trend} ({diff:+.1f}%)")
            
        plot_multisession_trends(all_metrics, ANALYTICS_DIR)

    print(f"\nPremium visualizations exported to: {ANALYTICS_DIR}/")

if __name__ == "__main__":
    main()
