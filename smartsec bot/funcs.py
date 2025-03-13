import requests

from constants import MISTRAL_API_KEY


# Функция для отправки запроса в Mistral AI API
def ask_mistral(prompt):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "mistral-small-latest",  # Или "mistral-small" для более дешёвых запросов
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(url, json=data, headers=headers)
    # return response['choices'][0]['message']['content']
    response_text = eval(response.text.replace('null', "None"))['choices'][0]['message']['content']
    return response_text

def processing_response(response):
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

# user_message = 'Как обеспечить защиту домашнего роутера?'
# user_message2 = 'Какие существубт протоколы шифрования?'
# response = ask_mistral(user_message2)
# print(response)
