import os

from apscheduler.schedulers.blocking import BlockingScheduler

from main import send_webhook

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=9)
def scheduled_job():
    send_webhook(os.environ['WEBHOOK_URL'])

sched.start()
