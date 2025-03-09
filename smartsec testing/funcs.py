from telebot import types
import time

def question_asking(message, bot):
    kb = types.InlineKeyboardMarkup(row_width=1)
    btn_one = types.InlineKeyboardButton(text='Обеспечение доступа к информации только авторизованным лицам',
                                         callback_data='right answer')
    btn_two = types.InlineKeyboardButton(text='Гарантия того, что информация всегда доступна.',
                                        callback_data='wrong answer')
    btn_three = types.InlineKeyboardButton(text='Защита информации от повреждения.',
                                            callback_data='wrong answer')
    btn_four = types.InlineKeyboardButton(text='Хранение данных в облачных сервисах.',
                                            callback_data='wrong answer')
    kb.add(btn_one, btn_two, btn_three, btn_four)

    delete_ReplyKeyboard(message, bot)
    bot.send_message(
        message.chat.id,
        'Что такое конфиденциальность в контексте информационной безопасности?',
        reply_markup=kb
    )


def delete_ReplyKeyboard(msg, bot):
    delete_keyboard_msg = bot.send_message(msg.chat.id, 'Пожалуйста, подождите . . . ',
                                           reply_markup=types.ReplyKeyboardRemove())
    time.sleep(0.5)
    bot.delete_message(msg.chat.id, delete_keyboard_msg.id)