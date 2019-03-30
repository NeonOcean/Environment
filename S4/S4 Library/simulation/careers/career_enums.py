import enum

class CareerCategory(enum.Int):
    Invalid = 0
    Work = 1
    School = 2
    TeenPartTime = 3
    Volunteer = 4

WORK_CAREER_CATEGORIES = (CareerCategory.Work, CareerCategory.TeenPartTime)

class CareerOutfitGenerationType(enum.Int):
    CAREER_TUNING = 0
    ZONE_DIRECTOR = 1
