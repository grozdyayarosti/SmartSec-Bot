from telebot import types

from funcs import TGTestingBot


bot = TGTestingBot()


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.start_message(message)


@bot.message_handler(content_types=['text'])
def dialog(message):
    bot.send_quiz(message)


@bot.poll_answer_handler()
def handle_poll_answer(quiz_answer: types.PollAnswer):
    bot.check_quiz_result(quiz_answer)


print('BOT IS STARTED')
bot.polling(none_stop=True)
