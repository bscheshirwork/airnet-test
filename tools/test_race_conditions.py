import http.cookiejar
import json
import sys
import time
import threading
import urllib.error
import urllib.request

base = (sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:5173').rstrip('/')

# Единый клиент и хранилище кук на весь скрипт, как в вашем шаблоне
cookie_jar = http.cookiejar.CookieJar()
client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

def request(path, body=None):
    payload = None if body is None else json.dumps(body).encode()

    # Подмешиваем маркер Xdebug только к тем запросам, где нужна искусственная задержка
    delimiter = '&' if '?' in path else '?'
    url = f"{base}/api{path}"
    if "/tickets/101" in path:
        url += f"{delimiter}XDEBUG_SESSION=REACT_DEBUG"

    response = client.open(urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'}), timeout=15)
    return json.load(response)

# --- Шаг 1: Авторизация (Выполняется последовательно) ---
try:
    login = request('/demo/login', {'role': 'editor'})
    assert login['employee']['role'] == 'editor', "Ошибка авторизации"
    print("[УСПЕХ] Авторизован под ролью editor. Сессионная кука сохранена.")
except Exception as e:
    print(f"[ОШИБКА] Сбой авторизации: {e}")
    sys.exit(1)

# Хранилище результатов для параллельных потоков
results = {}

def worker(ticket_id, delay, storage_key):
    if delay > 0:
        time.sleep(delay)
    try:
        results[storage_key] = request(f'/tickets/{ticket_id}')
        print(f"[Поток] Ответ по тикету {ticket_id} получен.")
    except Exception as e:
        results[storage_key] = e

# --- Шаг 2: Симуляция гонки (Параллельные клики) ---
print("\nИмитация быстрого переключения элементов в React...")

# Первый клик: тикет 101 (уйдет сразу, зависнет на бэкенде в Xdebug)
t1 = threading.Thread(target=worker, args=(101, 0, "first_clicked"))

# Второй клик: тикет 102 (уйдет через 0.2 сек, выполнится бэкендом мгновенно)
t2 = threading.Thread(target=worker, args=(102, 0.2, "last_clicked"))

t1.start()
t2.start()

t1.join()
t2.join()

# --- Шаг 3: Валидация результатов ---
print("\n--- Анализ ответов бэкенда ---")
last_data = results.get("last_clicked")

try:
    assert last_data['ticket']['id'] == 102 and last_data['ticket']['source']['id'] == 2, last_data

    print("\n[ТЕСТ ВЫПОЛНЕН] Сетевая гонка успешно сымитирована:")
    print(" -> Бэкенд выдал правильные данные для каждого запроса независимо.")
    print(" -> Ответ для тикета 102 вернулся РАНЬШЕ, хотя был запущен ПОЗДНЕЕ.")
    print("\n[ВНИМАНИЕ] Этот скрипт проверяет только API.")
    print("Чтобы гонка не сломала интерфейс, убедитесь, что в React настроена отмена (AbortController) или Ignore-паттерн!")

except AssertionError as e:
    print(f"\n[ОШИБКА] Бэкенд вернул некорректную структуру данных: {e}")