import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os

# === Telegram конфігурація
BOT_TOKEN = '8061519904:AAGI3cwN4fOVQ2sb59BkO5IwgqmkzKFm_0E'
CHAT_ID = '-1002849580257'

headers = {"User-Agent": "Mozilla/5.0"}
now = datetime.now()
seven_days_ago = now - timedelta(days=7)
today_str = now.strftime("%d.%m.%Y")

# === 1. ЗЕРНОВІ
url_grain = "https://agrotender.com.ua/traders/region_dnepr"
soup_grain = BeautifulSoup(requests.get(url_grain, headers=headers).text, "html.parser")
grain_rows = []
for block in soup_grain.select("div.traders__item__content"):
    name_tag = block.select_one(".traders__item__content-title")
    if not name_tag:
        continue
    trader_name = name_tag.get_text(strip=True)
    titles = block.select(".traders__item__content-p-title")
    prices = block.select(".traders__item__content-p-price")
    for title, price in zip(titles, prices):
        culture = title.get_text(strip=True)
        value = price.get_text(strip=True)
        if culture in ["Кукурудза", "Соя", "Ріпак", "Ячмінь", "Пшениця 1 кл."]:
            grain_rows.append(f"{culture:<10} | {value:<8} | {trader_name}")

# === Функція для обробки секцій з датою
def parse_table_rows(soup):
    rows = []
    for row in soup.select("tr"):
        price_tag = row.select_one("span.price")
        trader_tag = row.select_one("span.title")
        location_tag = row.select_one("span.location")
        date_tag = row.select_one("span.hidden_date")
        if not all([price_tag, trader_tag, location_tag, date_tag]):
            continue
        date_raw = date_tag.get("data-date")  # e.g. '20250630'
        parsed_date = datetime.strptime(date_raw, "%Y%m%d")
        if parsed_date < seven_days_ago:
            continue
        price = " ".join(price_tag.get_text().split())
        trader = trader_tag.get_text(strip=True)
        location = location_tag.get_text(strip=True)
        date = parsed_date.strftime("%d.%m.%Y")
        rows.append(f"{price:<8} | {date} | {trader:<25} | {location}")
    return rows

# === 2. Олія
url_oil = "https://agrotender.com.ua/traders/region_ukraine/maslo_podsolnechnoe"
soup_oil = BeautifulSoup(requests.get(url_oil, headers=headers).text, "html.parser")
oil_rows = parse_table_rows(soup_oil)

# === 3. Шрот
url_meal = "https://agrotender.com.ua/traders/region_ukraine/shrot_podsoln"
soup_meal = BeautifulSoup(requests.get(url_meal, headers=headers).text, "html.parser")
meal_rows = parse_table_rows(soup_meal)

# === 4. Макуха
url_cake = "https://agrotender.com.ua/traders/region_ukraine/zhmyh_podsoln_nizkoprot"
soup_cake = BeautifulSoup(requests.get(url_cake, headers=headers).text, "html.parser")
cake_rows = parse_table_rows(soup_cake)
# Перше повідомлення: зернові + олія
message1_parts = []

if grain_rows:
    message1_parts.append("<b>🌾 ЗЕРНОВІ (Dnipro region)</b>\n<pre>Культура     | Ціна     | Трейдер\n" + "-"*40)
    message1_parts.append("\n".join(grain_rows) + "</pre>")

if oil_rows:
    message1_parts.append("<b>🌻 СОНЯШНИКОВА ОЛІЯ</b>\n<pre>Ціна     | Дата       | Трейдер                 | Локація\n" + "-"*70)
    message1_parts.append("\n".join(oil_rows) + "</pre>")

message1 = f"<b>📅 Ціни трейдерів на {today_str}</b>\n\n" + "\n\n".join(message1_parts)


# Друге повідомлення: шрот + макуха
message2_parts = []

if meal_rows:
    message2_parts.append("<b>🌰 ШРОТ СОНЯШНИКОВИЙ</b>\n<pre>Ціна     | Дата       | Трейдер                 | Локація\n" + "-"*70)
    message2_parts.append("\n".join(meal_rows) + "</pre>")

if cake_rows:
    message2_parts.append("<b>🥧 МАКУХА СОНЯШНИКОВА</b>\n<pre>Ціна     | Дата       | Трейдер                 | Локація\n" + "-"*70)
    message2_parts.append("\n".join(cake_rows) + "</pre>")

message2 = "\n\n".join(message2_parts)
def send_telegram_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': msg,
        'parse_mode': 'HTML'
    }
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print(f"⚠️ Помилка Telegram: {response.status_code}")
        print("📨 Відповідь:", response.text)

# Надсилання
if BOT_TOKEN and CHAT_ID:
    if message1.strip():
        send_telegram_message(message1)
    if message2.strip():
        send_telegram_message(message2)
else:
  print("⚠️ BOT_TOKEN або CHAT_ID не задано.")
