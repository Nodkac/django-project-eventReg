from .models import Registration

MAX_CONFIRMED_PER_PERSON = 2

def confirmed_count_for_email(email: str) -> int:
    return Registration.objects.filter(email=email, status="CONFIRMED").count()

def event_confirmed_count(event) -> int:
    return Registration.objects.filter(event=event, status="CONFIRMED").count()
