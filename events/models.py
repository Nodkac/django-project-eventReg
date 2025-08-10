from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    venue = models.CharField(max_length=120, blank=True)
    capacity = models.PositiveIntegerField(default=50)
    waitlist_enabled = models.BooleanField(default=True)
    is_team_event = models.BooleanField(default=False)
    team_size_min = models.PositiveIntegerField(default=1)
    team_size_max = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title


class Registration(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = "CONFIRMED", "Confirmed"
        WAITLIST = "WAITLIST", "Waitlist"

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    email = models.EmailField()
    team_name = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.CONFIRMED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("event", "email")
        indexes = [models.Index(fields=["email", "status"])]

    def __str__(self):
        return f"{self.name} @ {self.event}"
