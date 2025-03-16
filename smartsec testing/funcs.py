from telebot import types
import time


def delete_ReplyKeyboard(msg, bot):
    delete_keyboard_msg = bot.send_message(msg.chat.id, 'Пожалуйста, подождите . . . ',
                                           reply_markup=types.ReplyKeyboardRemove())
    time.sleep(0.5)
    bot.delete_message(msg.chat.id, delete_keyboard_msg.id)