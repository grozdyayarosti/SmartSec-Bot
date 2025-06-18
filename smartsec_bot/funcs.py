import random
import string

import requests
import telebot
from telebot import types
import time

from constants import MISTRAL_API_KEY, TELEGRAM_BOT_TOKEN


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
            reply_markup=self.markUpSave('start')
        )

    def send_infosec_answer(self, message: types.Message):
        delete_keyboard_msg = self.send_message(message.chat.id, 'Пожалуйста, подождите . . . ',
                                               reply_markup=types.ReplyKeyboardRemove())
        response = self.ask_mistral(message.text)
        # response = "Информационная безопасность (ИБ) — это совокупность мер и технологий, направленных на защиту информации от несанкционированного доступа, использования, раскрытия, изменения, уничтожения или других видов ущерба. Основная цель информационной безопасности — обеспечить конфиденциальность, целостность и доступность информации.\n\n### Основные компоненты информационной безопасности:\n\n1. **Конфиденциальность**: Защита информации от несанкционированного доступа и раскрытия. Это включает в себя шифрование данных, контроль доступа и аутентификацию пользователей.\n\n2. **Целостность**: Обеспечение того, что информация не была изменена или уничтожена без разрешения. Это включает в себя контроль версий, резервное копирование и проверку целостности данных.\n\n3. **Доступность**: Обеспечение того, что информация доступна для авторизованных пользователей в нужное время. Это включает в себя резервное копирование, восстановление после сбоев и управление доступностью систем.\n\n### Зачем нужна информационная безопасность?\n\n1. **Защита данных**: В современном мире данные являются одним из самых ценных ресурсов. Утечка или кража данных может привести к значительным финансовым потерям, ущербу репутации и юридическим последствиям.\n\n2. **Соблюдение нормативных требований**: Многие отрасли и страны имеют строгие законы и стандарты, касающиеся защиты данных. Несоблюдение этих требований может привести к штрафам и другим санкциям.\n\n3. **Защита от кибератак**: Кибератаки становятся все более изощренными и частыми. Информационная безопасность помогает защитить организации от таких угроз, как вирусы, трояны, фишинг и DDoS-атаки.\n\n4. **Обеспечение доверия**: Клиенты и партнеры должны быть уверены в том, что их данные находятся в безопасности. Это способствует укреплению доверия и укреплению деловых отношений.\n\n5. **Обеспечение непрерывности бизнеса**: Информационная безопасность помогает минимизировать риски, связанные с перерывами в работе, и обеспечивает возможность быстрого восстановления после инцидентов.\n\n### Основные меры информационной безопасности:\n\n1. **Шифрование данных**: Защита данных при передаче и хранении с помощью криптографических методов.\n\n2. **Контроль доступа**: Ограничение доступа к информации только для авторизованных пользователей.\n\n3. **Антивирусное ПО и системы обнаружения вторжений**: Защита от вредоносного ПО и мониторинг сетевого трафика для выявления подозрительной активности.\n\n4. **Резервное копирование и восстановление**: Регулярное создание резервных копий данных и разработка планов восстановления после сбоев.\n\n5. **Обучение и осведомленность сотрудников**: Обучение сотрудников основам информационной безопасности и повышение их осведомленности о потенциальных угрозах.\n\n6. **Политики и процедуры безопасности**: Разработка и внедрение политик и процедур, направленных на обеспечение информационной безопасности.\n\nИнформационная безопасность является критически важной для любой организации, независимо от ее размера и отрасли, и требует постоянного внимания и обновления в условиях быстро меняющейся угрозной среды."
        response_text = self.processing_response(response)
        self.delete_message(message.chat.id, delete_keyboard_msg.id)
        self.send_message(
            chat_id=message.chat.id,
            text=response_text,
            reply_markup=self.markUpSave('start'),
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

    @staticmethod
    def get_password(password_type):
        if password_type == 'easy password':
            with open('./smartsec_bot/txt_files/passwords.txt', 'r') as f:
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
        # Собираем строки обратно в текст с символами новой строки
        response = '\n'.join(lines)

        return response

    # Функция, которая в зависимости от полученного параметра создаёт markup - альетарнативную клавиатуру с разными вариантами ответа
    @staticmethod
    def markUpSave(mode: str) -> types.ReplyKeyboardMarkup:
        main_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if mode == 'start':
            item1 = telebot.types.KeyboardButton("Вопрос по ИБ")
            item2 = telebot.types.KeyboardButton('Проверка ссылок')
            item3 = telebot.types.KeyboardButton('Генерация пароля')
            main_menu_markup.add(item1, item2, item3)
        elif mode == 'empty':
            main_menu_markup = telebot.types.ReplyKeyboardRemove()

        return main_menu_markup

    def delete_ReplyKeyboard(self, msg):
        delete_keyboard_msg = self.send_message(msg.chat.id, 'Пожалуйста, подождите . . . ',
                                               reply_markup=types.ReplyKeyboardRemove())
        time.sleep(0.5)
        self.delete_message(msg.chat.id, delete_keyboard_msg.id)
