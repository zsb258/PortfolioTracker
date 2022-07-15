from api.models import EventLog, EventExceptionLog, FxEventLog, PriceEventLog

def get_largest_event_id():
    """Get largest event ID."""
    if EventLog.objects.all().order_by('-event_id').exists():
        max_trade_event = EventLog.objects.all().order_by('-event_id').first().event_id
    else:
        max_trade_event = 0
    
    if EventExceptionLog.objects.all().order_by('-event_id').exists():
        max_exception_event = EventExceptionLog.objects.all().order_by('-event_id').first().event_id
    else:
        max_exception_event = 0
    
    if FxEventLog.objects.all().order_by('-event_id').exists():
        max_fx_event = FxEventLog.objects.all().order_by('-event_id').first().event_id
    else:
        max_fx_event = 0

    if PriceEventLog.objects.all().order_by('-event_id').exists():
        max_price_event = PriceEventLog.objects.all().order_by('-event_id').first().event_id
    else:
        max_price_event = 0
    
    return max(
        max_trade_event, max_exception_event, max_fx_event, max_price_event,
    )