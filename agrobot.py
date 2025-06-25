import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

# Отримуємо токен і чат ID з середовища
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# Завантажуємо HTML сторінку
url = "https://agrotender.com.ua/traders/region_dnepr"
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

trader_blocks = soup.select("div.traders__item__content")

rows = []
for block in trader_blocks:
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
            rows.append(f"{culture:<10} | {value:<8} | {trader_name}")

today = datetime.now().strftime("%d.%m.%Y")
header = f"<b>🌾 Ціни трейдерів на {today}</b>\n\n<pre>Культура     | Ціна     | Трейдер\n" + "-"*40
body = "\n".join(rows)
footer = "</pre>"
message = header + "\n" + body + footer

# Надсилаємо повідомлення в Telegram
payload = {
    'chat_id': CHAT_ID,
    'text': message,
    'parse_mode': 'HTML'
}
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
requests.post(url, data=payload)
