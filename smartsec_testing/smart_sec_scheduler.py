import schedule

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from constants import MY_NAME, MY_ID
import time
import datetime

from smartsec_testing.constants import MY_ID, MY_NAME
from smartsec_testing.funcs import TGTestingBot


class SmartSecScheduler:
    def __init__(self, bot: TGTestingBot):
        self.scheduler = None
        self.bot = bot

    def send_scheduled_message(self):
        self.bot.send_quiz(MY_ID, MY_NAME)
        print(f'[{str(datetime.datetime.now().time()).split(".")[0]}]'
              f' - SCHEDULE sending quiz...')

    def start_scheduler(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.send_scheduled_message,
                          trigger='interval',
                          seconds=2*24*60*60)
        self.scheduler.start()
        print("Планировщик запущен!")
        try:
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            self.scheduler.shutdown()

    def pause_scheduler(self):
        self.scheduler.pause()
        print("Планировщик приостановлен!")

    def resume_scheduler(self):
        self.scheduler.resume()
        print("Планировщик возобновлен")
