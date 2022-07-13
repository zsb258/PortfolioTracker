from django.http import HttpRequest, HttpResponse, JsonResponse

from event_generator.event_generator import EventGenerator
from event_handler.event_handlers import EventHandler
from util.common_types import Event

def index(request: 'HttpRequest') -> 'HttpResponse':
    return JsonResponse({'message': 'Hello, World!'})

def process_event(req: HttpRequest) -> HttpResponse:
    if req.POST:
        event: Event = req.POST
        EventHandler().handle_event(event)
        return HttpResponse(status=204)
    else:
        return HttpResponse(status=400)