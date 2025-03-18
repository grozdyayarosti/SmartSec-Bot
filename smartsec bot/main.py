from funcs import TGHelpBot

bot = TGHelpBot()


# Обработчик события при получении команды start
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.start_message(message)


#Обработчик события при получении текстового сообщения
@bot.message_handler(content_types=['text'])
def dialog(message):
    bot.send_start_menu(message)


print('BOT IS STARTED')
# Заставляет бота работать бесперебойно(пока на машине запущен код)
bot.polling(none_stop=True)
