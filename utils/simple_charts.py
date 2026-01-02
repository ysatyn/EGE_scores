# Этот кусок кода был написан DeepSeek, за качество не отвечаю

import matplotlib.pyplot as plt
import io
from typing import List, Dict
from datetime import datetime

SUBJECT_COLORS = {
    "math_profile": "#FF6B6B",  # Красный
    "math_basic": "#4ECDC4",     # Бирюзовый
    "russian": "#45B7D1",        # Голубой
    "physics": "#96CEB4",        # Светло-зеленый
    "chemistry": "#FFEAA7",      # Желтый
    "biology": "#DDA0DD",        # Фиолетовый
    "informatics": "#98D8C8",    # Мятный
    "history": "#F7DC6F",        # Золотой
    "social": "#BB8FCE",         # Лавандовый
    "geography": "#82E0AA",      # Зеленый
    "literature": "#F1948A",     # Коралловый
    "english": "#85C1E9",        # Небесный
    "german": "#F8C471",         # Оранжевый
    "french": "#D7BDE2",         # Сиреневый
    "spanish": "#76D7C4",        # Бирюза
    "chinese": "#F9E79F",        # Бежевый
}

def generate_simple_progress_chart(scores_data: Dict[str, List[tuple]]) -> io.BytesIO:
    fig, ax = plt.subplots(figsize=(14, 8))
    
    legend_handles = []
    legend_labels = []
    
    for subject_id, data in scores_data.items():
        if not data:
            continue
            
        data.sort(key=lambda x: x[0])
        dates = [d[0] for d in data]
        scores = [d[1] for d in data]
        
        color = SUBJECT_COLORS.get(subject_id, "#000000")
        
        line, = ax.plot(dates, scores, 
                       marker='o', 
                       linewidth=2,
                       markersize=6,
                       color=color)
        
        from utils.subjects import EGE_SUBJECTS_DICT
        subject_name = EGE_SUBJECTS_DICT.get(subject_id, subject_id)
        legend_handles.append(line)
        legend_labels.append(subject_name)
    
    ax.set_xlabel('Дата попытки', fontsize=12)
    ax.set_ylabel('Баллы', fontsize=12)
    ax.set_title('Прогресс по всем предметам', fontsize=14)
    
    ax.grid(True, alpha=0.3)
    
    plt.xticks(rotation=45)
    
    ax.legend(legend_handles, legend_labels, 
             loc='center left', 
             bbox_to_anchor=(1, 0.5),
             fontsize=10)
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    
    return buf