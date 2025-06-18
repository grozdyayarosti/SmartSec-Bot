from funcs import TGHelpBot

bot = TGHelpBot()


# Обработчик события при получении команды start
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.start_message(message)


#Обработчик события при получении текстового сообщения
@bot.message_handler(content_types=['text'])
def dialog(message):
    match message.text:
        case 'Вопрос по ИБ':
            reply_message = bot.send_message(
                message.chat.id,
                "Задайте вопрос по ИБ",
                reply_markup=bot.markUpSave('empty')
            )
            bot.register_next_step_handler(reply_message, bot.send_infosec_answer)
        case 'Генерация пароля':
            bot.passwords_handling(message)
        case _:
            bot.send_message(message.chat.id,"Выберите опцию меню")


@bot.callback_query_handler(func=lambda callback: callback.data)
def check_callback_data(callback):
    # if callback.data == 'wrong question':
    #     delete_ReplyKeyboard(callback.message)
    #     bot.send_message(callback.message.chat.id, 'Переформулируйте вопрос, пожалуйста', reply_markup=to_home_markup)
    #     bot.register_next_step_handler(callback.message, topyc_synchronization)
    # elif callback.data == 'correct question':
    #     question = callback.message.text[18:-5]
    #     inl_keyb_reply = get_articles(question, connection)
    #     bot.send_message(callback.message.chat.id, inl_keyb_reply, reply_markup=main_menu_markup)

    if 'password' in callback.data:
        inl_keyb_reply = bot.get_password(callback.data)
        bot.send_message(callback.message.chat.id, inl_keyb_reply, reply_markup=bot.markUpSave('start'))

    elif callback.data == 'to home':
        bot.clear_step_handler_by_chat_id(chat_id=callback.message.chat.id)
        welcome(callback.message)

    else:
        bot.send_message(callback.message.chat.id, 'пустота')


print('BOT IS STARTED')
# Заставляет бота работать бесперебойно(пока на машине запущен код)
bot.polling(none_stop=True)
