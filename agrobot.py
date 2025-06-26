import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

# === Telegram конфігурація
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

headers = {"User-Agent": "Mozilla/5.0"}
today = datetime.now().strftime("%d.%m.%Y")

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

# === 2. СОНЯШНИКОВА ОЛІЯ
url_oil = "https://agrotender.com.ua/traders/region_ukraine/maslo_podsolnechnoe"
soup_oil = BeautifulSoup(requests.get(url_oil, headers=headers).text, "html.parser")
oil_rows = []
for row in soup_oil.select("tr"):
    price_tag = row.select_one("span.price")
    trader_tag = row.select_one("span.title")
    location_tag = row.select_one("span.location")
    date_tag = row.select_one("span.hidden_date")
    if not all([price_tag, trader_tag, location_tag, date_tag]):
        continue
    price = " ".join(price_tag.get_text().split())
    trader = trader_tag.get_text(strip=True)
    location = location_tag.get_text(strip=True)
    date_raw = date_tag.get("data-date")
    date = f"{date_raw[6:8]}.{date_raw[4:6]}.{date_raw[:4]}"
    oil_rows.append(f"{price:<8} | {date} | {trader:<25} | {location}")

# === 3. ШРОТ
url_meal = "https://agrotender.com.ua/traders/region_ukraine/shrot_podsoln"
soup_meal = BeautifulSoup(requests.get(url_meal, headers=headers).text, "html.parser")
meal_rows = []
for row in soup_meal.select("tr"):
    price_tag = row.select_one("span.price")
    trader_tag = row.select_one("span.title")
    location_tag = row.select_one("span.location")
    date_tag = row.select_one("span.hidden_date")
    if not all([price_tag, trader_tag, location_tag, date_tag]):
        continue
    price = " ".join(price_tag.get_text().split())
    trader = trader_tag.get_text(strip=True)
    location = location_tag.get_text(strip=True)
    date_raw = date_tag.get("data-date")
    date = f"{date_raw[6:8]}.{date_raw[4:6]}.{date_raw[:4]}"
    meal_rows.append(f"{price:<8} | {date} | {trader:<25} | {location}")

# === 4. МАКУХА 
url_cake = "https://agrotender.com.ua/traders/region_ukraine/zhmyh_podsoln_nizkoprot"
soup_cake = BeautifulSoup(requests.get(url_cake, headers=headers).text, "html.parser")
cake_rows = []
for row in soup_cake.select("tr"):
    price_tag = row.select_one("span.price")
    trader_tag = row.select_one("span.title")
    location_tag = row.select_one("span.location")
    date_tag = row.select_one("span.hidden_date")
    if not all([price_tag, trader_tag, location_tag, date_tag]):
        continue
    price = " ".join(price_tag.get_text().split())
    trader = trader_tag.get_text(strip=True)
    location = location_tag.get_text(strip=True)
    date_raw = date_tag.get("data-date")
    date = f"{date_raw[6:8]}.{date_raw[4:6]}.{date_raw[:4]}"
    cake_rows.append(f"{price:<8} | {date} | {trader:<25} | {location}")

# === Формуємо повідомлення
parts = []

if grain_rows:
    parts.append("<b>🌾 ЗЕРНОВІ (Dnipro region)</b>\n<pre>Культура     | Ціна     | Трейдер\n" + "-"*40)
    parts.append("\n".join(grain_rows) + "</pre>")

if oil_rows:
    parts.append("<b>🌻 СОНЯШНИКОВА ОЛІЯ</b>\n<pre>Ціна     | Дата       | Трейдер                 | Локація\n" + "-"*70)
    parts.append("\n".join(oil_rows) + "</pre>")

if meal_rows:
    parts.append("<b>🌰 ШРОТ СОНЯШНИКОВИЙ</b>\n<pre>Ціна     | Дата       | Трейдер                 | Локація\n" + "-"*70)
    parts.append("\n".join(meal_rows) + "</pre>")

if cake_rows:
    parts.append("<b>🥧 МАКУХА СОНЯШНИКОВА</b>\n<pre>Ціна     | Дата       | Трейдер                 | Локація\n" + "-"*70)
    parts.append("\n".join(cake_rows) + "</pre>")

message = f"<b>📅 Ціни трейдерів на {today}</b>\n\n" + "\n\n".join(parts) if parts else f"⚠️ Даних на {today} не знайдено."

# === Вивід у консоль
print("\n" + message.replace("<b>", "").replace("</b>", "").replace("<pre>", "").replace("</pre>", ""))

# === Надсилання в Telegram
if BOT_TOKEN and CHAT_ID:
    payload = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
    response = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=payload)
    print("\n📬 Повідомлення надіслано в Telegram." if response.status_code == 200 else f"\n⚠️ Помилка Telegram: {response.status_code}")
else:
    print("\n⚠️ BOT_TOKEN або CHAT_ID не задано — повідомлення не надіслано.")
