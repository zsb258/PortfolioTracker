"""Module that implements a scheduler to publish events to server endpoint using POST request ."""

from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.events import JobEvent, EVENT_JOB_ERROR
import requests

from event_generator.event_generator import EventGenerator

SERVER_URL = 'http://localhost:8000'

_scheduler = BlockingScheduler({
    'daemon': True,
    'apscheduler.job_defaults.max_instances': 2
})


def publish_market_data():
    """Uses dummy client to publish market data."""
    payload = EventGenerator().send_next_market_data()
    if payload:
        print(f'Publishing new market data (event {payload["EventID"]})...')
        requests.post(f'{SERVER_URL}/api/events/', data=payload)
    else:
        raise Exception('No market data to publish')

def publish_trade_event():
    """Uses dummy client to publish trade event."""
    payload = EventGenerator().send_next_trade_event()
    if payload:
        print(f'Publishing new trade event (event {payload["EventID"]})...')
        requests.post(f'{SERVER_URL}/api/events/', data=payload)
    else:
        raise Exception('No trade event to publish')

# Schedule to post a new market data every 2 seconds
# with an extra-delay picked randomly in a [-1, +1] seconds window.
_scheduler.add_job(
    publish_market_data,
    'interval', seconds=2, jitter=1,
    id='market_data_producer',
)

# Schedule to post a new trade event every 5 seconds
# Trade events are sent less frequently than market data events,
# due to the observation that there are more market data events than trade events.
_scheduler.add_job(
    publish_trade_event,
    'interval', seconds=5,
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
