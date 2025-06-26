import datetime
import threading
import time
import requests
import telebot
from flask import Flask, request
from telebot import types

from funcs import TGTestingBot
from constants import TG_WEBHOOK_INFO_URL, WEBHOOK_URL, WEBHOOK_PORT
from smart_sec_scheduler import SmartSecScheduler


bot = TGTestingBot()
app = Flask(__name__)
scheduler = SmartSecScheduler(bot)


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.start_bot(message)


@bot.poll_answer_handler()
def handle_poll_answer(quiz_answer: types.PollAnswer):
    bot.check_quiz_result(quiz_answer)


@bot.callback_query_handler(func=lambda callback: callback.data)
def check_callback_data(callback: telebot.types.CallbackQuery):
    if callback.data == 'go_testing':
        bot.start_testing(callback, scheduler)


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return 'Это Webhook бота!', 200  # Теперь браузер получит ответ
    if request.method == 'POST':
        if request.headers.get('content-type') == 'application/json':
            json_data = request.get_json()
            update = telebot.types.Update.de_json(json_data)
            bot.process_new_updates([update])
            print(f'[{str(datetime.datetime.now().time()).split(".")[0]}] - REPLY sending quiz...')
            return 'OK', 200
    return 'Invalid content-type', 400


# bot.polling()
if __name__ == '__main__':
    scheduler_thread = threading.Thread(target=scheduler.start_scheduler,
                                        daemon=True)
    scheduler_thread.start()

    if WEBHOOK_URL:
        print(requests.get(TG_WEBHOOK_INFO_URL).json())
        # Удаляем старый Webhook и устанавливаем новый
        bot.remove_webhook()
        time.sleep(1)
        bot.set_webhook(url=WEBHOOK_URL)

        # Запуск Flask-сервера
        print(f"Бот запущен на Webhook: {WEBHOOK_URL}")
        app.run(host='0.0.0.0', port=WEBHOOK_PORT)
    else:
        bot.testing_is_not_available()

# https://cloudpub.ru/dashboard
# clo.exe publish http port
