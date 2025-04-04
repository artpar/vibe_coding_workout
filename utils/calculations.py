#######################
# Utility Functions
#######################

def calculate_1rm(weight, reps):
    """Calculate 1RM using Epley Formula"""
    return weight * (1 + reps/30)

def standardize_exercise_name(exercise):
    """Standardize exercise names for consistency"""
    exercise = exercise.lower()
    if 'lat pulldown' in exercise:
        return 'Lat Pulldown (All Variations)'
    if 'barbell bench press' in exercise or 'bench press (barbell)' in exercise:
        return 'Barbell Bench Press'
    if 'dumbbell bench press' in exercise or 'bench press (dumbbell)' in exercise:
        return 'Dumbbell Bench Press'
    return exercise


