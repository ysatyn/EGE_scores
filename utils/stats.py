# Этот кусок кода написан DeepSeek, за качество не отвечаю

from typing import List, Dict, Tuple
from db.models import Scores
from collections import defaultdict

def prepare_simple_chart_data(scores: List[Scores]) -> Dict[str, List[Tuple]]:
    data = defaultdict(list)
    
    for score in scores:
        data[score.subject_id].append((score.created_at, score.score))
    
    return dict(data)

def get_simple_stats(scores: List[Scores]) -> str:
    if not scores:
        return "📭 Нет данных"
    
    total = len(scores)
    avg = sum(s.score for s in scores) / total
    max_score = max(s.score for s in scores)
    
    subjects = {}
    for score in scores:
        if score.subject_name not in subjects:
            subjects[score.subject_name] = []
        subjects[score.subject_name].append(score.score)
    
    text = f"📊 *Статистика*\n\n"
    text += f"• Всего попыток: {total}\n"
    text += f"• Средний балл: {avg:.1f}\n"
    text += f"• Лучший результат: {max_score}\n\n"
    
    text += f"📚 *По предметам:*\n"
    for subject_name, subject_scores in subjects.items():
        subject_avg = sum(subject_scores) / len(subject_scores)
        text += f"• {subject_name}: {subject_avg:.1f} ({len(subject_scores)} попыток)\n"
    
    return text