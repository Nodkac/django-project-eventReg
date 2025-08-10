from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Welcome to the Event Registration App</h1><p>Use the menu to browse events.</p>")
