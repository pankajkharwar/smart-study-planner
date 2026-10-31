"""
AI Study Plan Engine
Calculates optimized daily study time allocation based on subject difficulties.
"""

def generate_study_plan(subjects, daily_hours):
    """
    Allocates daily study hours across subjects based on difficulty weights:
    - weak: weight 3
    - medium: weight 2
    - strong: weight 1
    
    Returns a list of dicts with subject details, hours, minutes, and percentage.
    """
    difficulty_weight = {
        "weak": 3,
        "medium": 2,
        "strong": 1
    }

    total_weight = 0
    for subject in subjects:
        diff_key = subject["difficulty"].lower().strip()
        total_weight += difficulty_weight.get(diff_key, 2)

    if total_weight == 0:
        total_weight = 1

    study_plan = []
    for subject in subjects:
        diff_key = subject["difficulty"].lower().strip()
        weight = difficulty_weight.get(diff_key, 2)
        allocated_time = (weight / total_weight) * daily_hours
        percentage = (weight / total_weight) * 100
        minutes = int(round(allocated_time * 60))

        study_plan.append({
            "subject": subject["name"],
            "difficulty": diff_key.capitalize(),
            "weight": weight,
            "hours_per_day": round(allocated_time, 2),
            "minutes_per_day": minutes,
            "percentage": round(percentage, 1)
        })

    return study_plan
