"""
ANALYSE DES DONNÉES - The Final Escape
Génère graphiques et statistiques des sessions de jeu
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

class GameDataAnalyzer:
    """Analyse les données de sessions"""
    
    def __init__(self, data_folder='/mnt/user-data/outputs/data'):
        self.data_folder = Path(data_folder)
        self.sessions = []
        self.load_sessions()
    
    def load_sessions(self):
        """Charge toutes les sessions"""
        if not self.data_folder.exists():
            print(f"❌ Dossier {self.data_folder} introuvable")
            return
        
        json_files = list(self.data_folder.glob('session_*.json'))
        print(f"📁 {len(json_files)} sessions trouvées\n")
        
        for file in json_files:
            with open(file, 'r', encoding='utf-8') as f:
                self.sessions.append(json.load(f))
        
        print(f"✅ {len(self.sessions)} sessions chargées\n")
    
    def analyze_outcomes(self):
        """Analyse les résultats"""
        if not self.sessions:
            print("❌ Aucune session à analyser")
            return
        
        outcomes = Counter([s['outcome'] for s in self.sessions])
        
        print("=" * 60)
        print("🏆 RÉSULTATS DES PARTIES")
        print("=" * 60)
        total = len(self.sessions)
        for outcome, count in outcomes.items():
            percentage = (count / total) * 100
            emoji = {
                'ESCAPED': '🎉',
                'CAUGHT': '💀',
                'TIMEOUT': '⏱️'
            }.get(outcome, '❓')
            print(f"{emoji} {outcome:12s} : {count:3d} ({percentage:5.1f}%)")
        print()
    
    def analyze_scores(self):
        """Statistiques des scores"""
        if not self.sessions:
            return
        
        scores = [s['final_score'] for s in self.sessions]
        
        print("=" * 60)
        print("💯 STATISTIQUES DE SCORE")
        print("=" * 60)
        print(f"Score moyen        : {np.mean(scores):.1f}")
        print(f"Score médian       : {np.median(scores):.1f}")
        print(f"Score minimum      : {min(scores)}")
        print(f"Score maximum      : {max(scores)}")
        print(f"Écart-type         : {np.std(scores):.1f}")
        print()
    
    def plot_outcome_distribution(self):
        """Graphique des résultats"""
        if not self.sessions:
            return
        
        outcomes = Counter([s['outcome'] for s in self.sessions])
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors = {
            'ESCAPED': '#50DC78',
            'CAUGHT': '#FF5A5A',
            'TIMEOUT': '#FFB432'
        }
        
        labels = list(outcomes.keys())
        values = list(outcomes.values())
        bar_colors = [colors.get(label, '#888888') for label in labels]
        
        bars = ax.bar(labels, values, color=bar_colors, edgecolor='white', linewidth=2)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=14, fontweight='bold')
        
        ax.set_xlabel('Résultat', fontsize=14, fontweight='bold')
        ax.set_ylabel('Nombre de parties', fontsize=14, fontweight='bold')
        ax.set_title('🏆 Distribution des Résultats - The Final Escape', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_facecolor('#f8f9fa')
        
        plt.tight_layout()
        output = '/mnt/user-data/outputs/outcome_distribution.png'
        plt.savefig(output, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✅ Graphique sauvegardé: {output}")
        plt.close()
    
    def generate_full_report(self):
        """Génère rapport complet"""
        print("\n" + "=" * 60)
        print("📊 RAPPORT D'ANALYSE - THE FINAL ESCAPE")
        print("=" * 60 + "\n")
        
        self.analyze_outcomes()
        self.analyze_scores()
        
        print("=" * 60)
        print("📈 GÉNÉRATION DES GRAPHIQUES")
        print("=" * 60 + "\n")
        
        self.plot_outcome_distribution()
        
        print("\n✅ Analyse terminée !")

def main():
    analyzer = GameDataAnalyzer()
    if len(analyzer.sessions) == 0:
        print("⚠️  Aucune session trouvée.\n")
        return
    analyzer.generate_full_report()

if __name__ == "__main__":
    main()
