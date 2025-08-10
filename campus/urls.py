# campus/urls.py
from django.contrib import admin
from django.urls import path
from events import views as ev

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", ev.event_list, name="event_list"),
    path("events/<int:event_id>/register/", ev.register, name="register"),
    path("events/<int:event_id>/register-team/", ev.register_team, name="register_team"),
    path("registrations/<int:reg_id>/cancel/", ev.cancel_registration, name="cancel_registration"),
]
