import time
from telebot import types
import schedule

from constants import MY_NAME, MY_ID
from funcs import TGTestingBot


bot = TGTestingBot()


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.start_message(message)


@bot.message_handler(content_types=['text'])
def testing_request(message):
    bot.user_request_responding(message)


@bot.poll_answer_handler()
def handle_poll_answer(quiz_answer: types.PollAnswer):
    bot.check_quiz_result(quiz_answer)

schedule.every(1).minutes.do(
    lambda: bot.send_quiz(MY_ID, MY_NAME)
)
# schedule.every().day.at("22:05").do(
#     lambda: bot.send_quiz(MY_ID, MY_NAME)
# )
# schedule.every().hour.do(lambda: print())
while True:
    schedule.run_pending()
    time.sleep(1)
print('BOT IS STARTED')
bot.polling(none_stop=True)
