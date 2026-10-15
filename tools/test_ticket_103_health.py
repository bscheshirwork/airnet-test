import http.cookiejar
import json
import sys
import urllib.error
import urllib.request

# --- КОНСТАНТЫ СЦЕНАРИЯ ---
TARGET_TICKET_ID = 103
HTTP_EXPECTED_OK_CODE = 200

# Настройка базового URL
base = (sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:5173').rstrip('/')

print(f"Старт проверки стабильности для Заявки #{TARGET_TICKET_ID} (Ожидается статус {HTTP_EXPECTED_OK_CODE})...")

# Создаем изолированную сессию
cookie_jar = http.cookiejar.CookieJar()
client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

try:
    # 1. Шаг: Авторизация для прохождения контроля доступа (middleware)
    login_payload = json.dumps({'role': 'editor'}).encode()
    client.open(urllib.request.Request(base + '/api/demo/login', data=login_payload, headers={'Content-Type': 'application/json'}), timeout=10)

    # 2. Шаг: Выполнение целевого GET-запроса к заявке 102
    response = client.open(urllib.request.Request(base + f'/api/tickets/{TARGET_TICKET_ID}'), timeout=10)
    ticket_status = response.status
    ticket_data = json.load(response)

except urllib.error.HTTPError as e:
    # Перехватываем HTTP-ошибки сервера (включая 500), чтобы узнать статус-код
    ticket_status = e.code
    try:
        ticket_data = json.load(e)
    except Exception:
        ticket_data = e.read().decode('utf-8')
except Exception as e:
    print(f"[СИСТЕМНЫЙ СБОЙ] Не удалось выполнить сетевой запрос: {e}")
    sys.exit(1)

# Валидация статуса ответа на строгое соответствие 200 OK (Без вывода системного трейса)
try:
    assert ticket_status == HTTP_EXPECTED_OK_CODE, \
        f"Стабильность нарушена! Ожидался статус {HTTP_EXPECTED_OK_CODE}, но сервер вернул код {ticket_status}. Ответ бэкенда: {ticket_data}"

    print(f"[УСПЕХ] Тест стабильности пройден. Сервер успешно вернул статус {ticket_status} OK для заявки #{TARGET_TICKET_ID}.")

except AssertionError as e:
    # Выводим чистое сообщение об ошибке (например, если вернулась 500) без Traceback
    print(f"\n[ОШИБКА СТАБИЛЬНОСТИ] {e}\n")
    sys.exit(1)
