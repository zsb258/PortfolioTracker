"""Module that implements a scheduler to publish events to server endpoint using POST request ."""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import JobEvent, EVENT_JOB_ERROR
from django.test import Client

from event_generator.event_generator import EventGenerator

_scheduler = BackgroundScheduler({
    'daemon': True,
    'apscheduler.job_defaults.max_instances': 2
})

_client = Client()

def publish_market_data():
    """Uses dummy client to publish market data."""
    print('Publishing new market data...')
    payload = EventGenerator().send_next_market_data()
    if payload:
        _client.post('/api/events/', data=payload)
    else:
        raise Exception('No market data to publish')

def publish_trade_event():
    """Uses dummy client to publish trade event."""
    print('Publishing new trade event...')
    payload = EventGenerator().send_next_trade_event()
    if payload:
        _client.post('/api/events/', data=payload)
    else:
        raise Exception('No trade event to publish')

# Schedule job functions to be called every 3 seconds
# with an extra-delay picked randomly in a [-2,+2] seconds window.
# Mimics delay of 1 to 5 seconds between publishing events.
_scheduler.add_job(
    publish_market_data,
    'interval', seconds=3, jitter=2,
    id='market_data_producer',
)
_scheduler.add_job(
    publish_trade_event,
    'interval', seconds=3, jitter=2,
    id='trade_event_producer',
)

def _callback(event: JobEvent):
    """Callback function that fires when a scheduled job throws exception.
    First remove the job from scheduler,
    then if there are no more jobs left, stop the scheduler.
    """
    if event.code == EVENT_JOB_ERROR:
        _scheduler.pause()
        _scheduler.remove_job(event.job_id)  # Remove job that raised exception
        _scheduler.resume()
    if len(_scheduler.get_jobs()) == 0:
        _scheduler.shutdown(wait=False)  # No jobs left, stop scheduler

# remove job when there is an exception to indicate no more data
_scheduler.add_listener(callback=_callback, mask=EVENT_JOB_ERROR)

def start_publishing():
    """Start scheduler if it is not already running."""
    if not _scheduler.running:
        _scheduler.start()
