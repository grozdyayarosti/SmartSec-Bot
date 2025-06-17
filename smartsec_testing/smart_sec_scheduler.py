import schedule

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from constants import REGULAR_QUESTIONS_PERIOD
import time
import datetime

from smartsec_testing.db_connection import Database
from smartsec_testing.funcs import TGTestingBot


class SmartSecScheduler:
    def __init__(self, bot: TGTestingBot):
        self.scheduler = None
        self.bot = bot

    def send_scheduled_message(self):
        with Database() as db:
            users = db.get_all_users_for_reqular_questions()
        for user in users:
            self.bot.send_quiz(user['chat_id'], user['user_name'], False)
        print(f'[{str(datetime.datetime.now().time()).split(".")[0]}]'
              f' - SCHEDULE sending quiz...')

    def start_scheduler(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.send_scheduled_message,
                          trigger='interval',
                          seconds=REGULAR_QUESTIONS_PERIOD)
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
