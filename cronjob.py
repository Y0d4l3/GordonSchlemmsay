from apscheduler.schedulers.blocking import BlockingScheduler
import os
from main import send_webhook

scheduler = BlockingScheduler()
schedule.every().day.at("09:00").do(send_webhook, os.environ['WEBHOOK-URL'])

scheduler.start()