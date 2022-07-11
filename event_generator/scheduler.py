from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler

scheduler = BackgroundScheduler()
# scheduler = BlockingScheduler()

def job_function():
    print("Hello World")

# Schedule job_function to be called every 3 seconds 
# with an extra-delay picked randomly in a [-2,+2] seconds window
scheduler.add_job(job_function, 
    'interval', seconds=3, jitter=2
)

if __name__ == '__main__':
    scheduler.start()
