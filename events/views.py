from django.db import transaction
from django.db.models import Count, Q, F, IntegerField, ExpressionWrapper
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from .models import Event, Registration
from .utils import MAX_CONFIRMED_PER_PERSON, confirmed_count_for_email, event_confirmed_count

def event_list(request):
    confirmed_count = Count("registration", filter=Q(registration__status="CONFIRMED"))
    events = (
        Event.objects
        .annotate(
            confirmed=confirmed_count,
            spots=ExpressionWrapper(F("capacity") - confirmed_count, output_field=IntegerField())
        )
        .order_by("start_at")
    )
    return render(request, "events/event_list.html", {"events": events})

@transaction.atomic
def register(request, event_id):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")
    name = request.POST.get("name", "").strip()
    email = request.POST.get("email", "").strip()
    if not (name and email):
        return HttpResponseBadRequest("Name & email required")

    ev = Event.objects.select_for_update().get(pk=event_id)
    if ev.is_team_event:
        return HttpResponseBadRequest("Use team registration endpoint.")

    if Registration.objects.filter(event=ev, email=email).exists():
        spots_left = ev.capacity - event_confirmed_count(ev)
        return render(request, "events/partials/status.html",
                      {"status": "already", "event": ev, "spots_left": spots_left})

    personal_confirmed = confirmed_count_for_email(email)
    confirmed_now = event_confirmed_count(ev)
    capacity_left = ev.capacity - confirmed_now

    reason = None
    if personal_confirmed >= MAX_CONFIRMED_PER_PERSON:
        status = Registration.Status.WAITLIST
        reason = "caplimit"
    else:
        if capacity_left > 0:
            status = Registration.Status.CONFIRMED
        elif ev.waitlist_enabled:
            status = Registration.Status.WAITLIST
            reason = "soldout"
        else:
            return render(request, "events/partials/status.html",
                          {"status": "soldout", "event": ev, "spots_left": capacity_left})

    reg = Registration.objects.create(event=ev, name=name, email=email, status=status)
    spots_left = ev.capacity - event_confirmed_count(ev)
    return render(request, "events/partials/status.html",
                  {"status": status.lower(), "reg_id": reg.id, "reason": reason,
                   "event": ev, "spots_left": spots_left})

@transaction.atomic
def register_team(request, event_id):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    ev = Event.objects.select_for_update().get(pk=event_id)
    if not ev.is_team_event:
        return HttpResponseBadRequest("Not a team event.")

    team_name = request.POST.get("team_name", "").strip()
    raw = request.POST.get("members", "").strip().splitlines()

    members = []
    for line in raw:
        line = line.strip()
        if not line:
            continue
        if "<" in line and ">" in line:
            name = line.split("<")[0].strip()
            email = line[line.find("<")+1:line.find(">")].strip()
        else:
            parts = [p.strip() for p in line.replace(";", ",").split(",")]
            if len(parts) < 2:
                return HttpResponseBadRequest("Each member needs name,email")
            name, email = parts[0], parts[1]
        members.append((name, email))

    if not (ev.team_size_min <= len(members) <= ev.team_size_max):
        return HttpResponseBadRequest(f"Team must be {ev.team_size_min}-{ev.team_size_max} members.")

    # dedupe by email
    seen = set(); deduped = []
    for name, email in members:
        e = email.lower()
        if e not in seen:
            seen.add(e); deduped.append((name, e))
    members = deduped

    confirmed_now = event_confirmed_count(ev)
    capacity_left = ev.capacity - confirmed_now

    require_waitlist = False
    reason = None
    if capacity_left < len(members):
        if ev.waitlist_enabled:
            require_waitlist = True; reason = "soldout"
        else:
            spots_left = ev.capacity - event_confirmed_count(ev)
            return render(request, "events/partials/team_status.html", {
                "rows": [(email, "soldout") for _, email in members],
                "team": team_name, "all_waitlist": False,
                "event": ev, "spots_left": spots_left
            })

    if not require_waitlist:
        for _, email in members:
            if Registration.objects.filter(event=ev, email=email).exists():
                require_waitlist = True; reason = "already_in_event"; break
            if confirmed_count_for_email(email) >= MAX_CONFIRMED_PER_PERSON:
                require_waitlist = True; reason = "caplimit"; break

    rows = []
    if require_waitlist:
        for name, email in members:
            if not Registration.objects.filter(event=ev, email=email).exists():
                Registration.objects.create(event=ev, name=name, email=email,
                                            team_name=team_name, status="WAITLIST")
            rows.append((email, "waitlist"))
        spots_left = ev.capacity - event_confirmed_count(ev)
        return render(request, "events/partials/team_status.html", {
            "rows": rows, "team": team_name, "all_waitlist": True, "reason": reason,
            "event": ev, "spots_left": spots_left
        })

    for name, email in members:
        Registration.objects.create(event=ev, name=name, email=email,
                                    team_name=team_name, status="CONFIRMED")
        rows.append((email, "confirmed"))

    spots_left = ev.capacity - event_confirmed_count(ev)
    return render(request, "events/partials/team_status.html", {
        "rows": rows, "team": team_name, "all_waitlist": False,
        "event": ev, "spots_left": spots_left
    })

@transaction.atomic
def cancel_registration(request, reg_id):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    reg = get_object_or_404(Registration.objects.select_for_update(), pk=reg_id)
    email = reg.email
    was_confirmed = (reg.status == "CONFIRMED")
    original_event = reg.event  # keep before delete
    reg.delete()

    updates = []
    # update original event spots
    updates.append((original_event.id, original_event.capacity - event_confirmed_count(original_event)))

    promoted = None
    if was_confirmed:
        waitlisted = (
            Registration.objects.select_for_update()
            .filter(email=email, status="WAITLIST")
            .order_by("created_at")
        )
        for w in waitlisted:
            evt = Event.objects.select_for_update().get(pk=w.event_id)
            if event_confirmed_count(evt) < evt.capacity and confirmed_count_for_email(email) < MAX_CONFIRMED_PER_PERSON:
                w.status = "CONFIRMED"; w.save(update_fields=["status"])
                promoted = w
                updates.append((evt.id, evt.capacity - event_confirmed_count(evt)))
                break

    return render(request, "events/partials/cancel_status.html",
                  {"promoted": promoted, "updates": updates})
