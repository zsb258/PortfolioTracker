from django.http import HttpRequest, HttpResponse, JsonResponse

from event_generator.event_generator import EventGenerator
from event_handler.event_handlers import EventHandler
from util.common_types import MarketEvent, TradeEvent

def index(request: 'HttpRequest') -> 'HttpResponse':
    return JsonResponse({'message': 'Hello, World!'})

def get_next_market_data(req: HttpRequest) -> HttpResponse:
    return JsonResponse(EventGenerator().publish_next_market_data())

def get_next_trade_event(req: HttpRequest) -> HttpResponse:
    return JsonResponse(EventGenerator().publish_next_trade_event())

def process_event(req: HttpRequest) -> HttpResponse:
    if req.POST:
        event: MarketEvent = req.POST
        EventHandler().handle_event(event)
        return HttpResponse(status=204)
    else:
        return HttpResponse(status=400)