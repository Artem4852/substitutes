from download import download_substitutes
from tables import get_lessons
from datetime import datetime

class_name = None
date = datetime(2025, 3, 18)
download_substitutes(date)
lessons = get_lessons(date, class_name)
print(lessons)