import subprocess
import time

# Ожидаем пока контейнер cloudpub опубликует URL
time.sleep(5)
result = subprocess.run(
    ["docker", "logs", 'cloudpub'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

if not result.stderr:
    new_webhook = result.stdout.split(" -> ")[1].strip()
    print(f"Запущен вебхук {new_webhook}")
    with open('/shared/webhook_url.txt', "w") as f:
        f.write(new_webhook)
    print("Бот запущен с новым WEBHOOK_URL")
