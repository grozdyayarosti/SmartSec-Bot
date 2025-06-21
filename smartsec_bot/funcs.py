import random
import string
import requests
import telebot
from telebot import types
import time
from googletrans import Translator
from domainreputation import Client

from constants import MISTRAL_API_KEY, TELEGRAM_BOT_TOKEN, DOMAINREPUTATION_API_KEY


class TGHelpBot(telebot.TeleBot):
    def __init__(self):
        super().__init__(TELEGRAM_BOT_TOKEN)

    def start_message(self, message: types.Message):
        self.send_message(
            message.chat.id,
            f"Доброго времени суток, {message.from_user.first_name}!\n"
            f"Я - <b>{self.get_me().first_name}</b>.\nЧто вас интересует?",
            parse_mode='html',
            # Вывод альтернативной клавиатуры для выбора предложенных ответов
            # (в зависимости от параметра будут предложены разные варианты в клавиатуре)
            reply_markup=self.create_markup('start')
        )

    def send_infosec_answer(self, message: types.Message):
        delete_keyboard_msg = self.send_message(message.chat.id, 'Пожалуйста, подождите . . . ',
                                               reply_markup=types.ReplyKeyboardRemove())
        response = self.ask_mistral(message.text)
        response_text = self.processing_response(response)
        self.delete_message(message.chat.id, delete_keyboard_msg.id)
        self.send_message(
            chat_id=message.chat.id,
            text=response_text,
            reply_markup=self.create_markup('start'),
            parse_mode='MarkdownV2'
        )

    def passwords_handling(self, message):
        kb = types.InlineKeyboardMarkup(row_width=1)
        btn_easy = types.InlineKeyboardButton(text='Слабый пароль',
                                              callback_data='easy password')
        btn_medium = types.InlineKeyboardButton(text='Хороший пароль',
                                                callback_data='medium password')
        btn_hard = types.InlineKeyboardButton(text='Сильный пароль',
                                              callback_data='hard password')
        kb.add(btn_easy, btn_medium, btn_hard)

        # self.delete_ReplyKeyboard(message)
        self.send_message(message.chat.id,
                         f'Какой пароль сгенерировать?',
                         reply_markup=kb)

    def url_checking(self, message):
        url = message.text
        url = url.split('/')[2] if url[:4] == 'http' else url.split('/')[0]
        wait_message = self.send_message(
            message.chat.id,
            "Я изучаю ссылку.\nПожалуйста, подождите . . . ",
            parse_mode='HTML')
        output = self.get_url_info(url)
        print(f'{output = }')
        self.delete_message(message.chat.id, wait_message.id)
        self.send_message(message.chat.id,
                          output,
                          parse_mode='HTML',
                          reply_markup=self.create_markup('to_home'))

    @staticmethod
    def get_url_info(url):
        def translate(word):
            result = Translator().translate(word, dest='ru')
            return result.text
        print(url)
        try:
            client = Client(DOMAINREPUTATION_API_KEY)
            response = client.get(url)
            response_dict = eval(str(response))
            print(response_dict)
            # 12cnd.1slo.pl excoder.club plantakiademexico.com mein-db-vorgang34.online

            info_dict = dict()
            info_dict['<b>Скорость работы</b>'] = '- ' + translate(response_dict['mode'])
            info_dict['<b>Репутация сайта</b>'] = f"- {response_dict['reputation_score']}/100"
            l = eval(response_dict['test_results'])
            for elem in l:
                warns = ['\n- ' + warn for warn in eval(elem["warnings"])]
                key = '<b>' + translate(elem["test"]) + '</b>'
                value = translate("".join(warns))
                info_dict[key] = value

            if not info_dict.get('Уязвимости SSL') is None:
                info_dict['Уязвимости SSL'] = (
                    info_dict['Уязвимости SSL'].replace(
                        'Запись TLSA не настроена и не настроена неправильно',
                        'Запись TLSA не настроена или настроена неправильно'))

            url_info = ''
            for k, v in info_dict.items():
                url_info += f"{k}: \n{v}\n"
        except Exception as _ex:
            print(_ex)
            url_info = 'Неверная ссылка!\nПерепроверьте её корректность, пожалуйста'
        finally:
            print(url_info)
            return url_info


    @staticmethod
    def get_password(password_type):
        if password_type == 'easy password':
            with open('txt_files/passwords.txt', 'r') as f:
                lines = f.readlines()
            password = "Слабый пароль:  " + random.choice(lines).strip()
        elif password_type == 'medium password':
            length = random.randint(6, 8)
            characters = string.ascii_letters + string.digits
            password = "Хороший пароль:  " + ''.join(random.choice(characters) for _ in range(length))
        elif password_type == 'hard password':
            length = random.randint(9, 12)
            characters = string.ascii_letters + string.digits + string.punctuation
            password = "Сильный пароль:  " + ''.join(random.choice(characters) for _ in range(length))
        return password

    @staticmethod
    def ask_mistral(prompt: str) -> str:
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "mistral-large-latest",  # Или "mistral-small" для более дешёвых запросов
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post(url, json=data, headers=headers)
        # return response['choices'][0]['message']['content']
        if response.status_code == 200:
            response_text = eval(response.text.replace('null', "None"))['choices'][0]['message']['content']
        else:
            response_text = "Ошибка на стороне сервера.\nУже исправляем!"
        return response_text

    @staticmethod
    def processing_response(response: str) -> str:
        # TODO реализовать через регулярки
        response = response.replace('.', '\\.')
        response = response.replace("_", "\\_")
        response = response.replace("-", "\\-")
        # response = response.replace("*", "\\*")
        # response = response.replace("#", "\\#")
        response = response.replace("[", "\\[")
        response = response.replace("(", "\\(")
        response = response.replace(")", "\\)")
        response = response.replace("<", "\\<")
        response = response.replace(">", "\\>")
        response = response.replace("`", "\\`")
        response = response.replace("!", "\\!")
        response = response.replace("**", "*")

        lines = response.split('\n')
        # Проходим по каждой строке
        for i in range(len(lines)):
            # Заменяем все символы # на *
            if '#' in lines[i]:
                lines[i] = lines[i].replace('###', '*') + '*'
                lines[i] = lines[i].replace("#", "\\#")
        # Собираем строки обратно в текст с символами новой строки
        response = '\n'.join(lines)

        return response

    @staticmethod
    def create_markup(mode: str):
        if mode == 'start':
            main_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = telebot.types.KeyboardButton("Вопрос по ИБ")
            item2 = telebot.types.KeyboardButton('Проверка ссылок')
            item3 = telebot.types.KeyboardButton('Генерация пароля')
            main_menu_markup.add(item1, item2, item3)
            return main_menu_markup
        elif mode == 'to_home':
            to_home_markup = types.InlineKeyboardMarkup(row_width=1)
            to_home_btn = types.InlineKeyboardButton(text='Вернуться к меню',
                                                     callback_data='to_home')
            to_home_markup.add(to_home_btn)
            return to_home_markup
        elif mode == 'empty':
            empty_markup = telebot.types.ReplyKeyboardRemove()
            return empty_markup

    def delete_ReplyKeyboard(self, msg):
        delete_keyboard_msg = self.send_message(msg.chat.id, 'Пожалуйста, подождите . . . ',
                                               reply_markup=types.ReplyKeyboardRemove())
        time.sleep(0.5)
        self.delete_message(msg.chat.id, delete_keyboard_msg.id)
