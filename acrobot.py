from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import time
from datetime import datetime

today = datetime.now().strftime("%d.%m.%Y")

# ===  Налаштування Telegram ===
BOT_TOKEN = '8061519904:AAGI3cwN4fOVQ2sb59BkO5IwgqmkzKFm_0E'
CHAT_ID = '-1002849580257'         

# ===  Налаштування Selenium ===
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
driver.get("https://agrotender.com.ua/traders/region_dnepr")
time.sleep(5)
html = driver.page_source
driver.quit()

# ===  Парсинг HTML ===
soup = BeautifulSoup(html, "html.parser")
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
        if culture and value and culture in ["Пшениця 1 кл.", "Кукурудза", "Ячмінь", "Ріпак", "Соя"]:
            row = f"{culture:<10} | {value:<8} | {trader_name}"
            rows.append(row)

header = f"<b>🌾 Ціни трейдерів на {today}</b>\n\n<pre>Культура     | Ціна     | Трейдер\n" + "-"*40
body = "\n".join(rows)
footer = "</pre>"

message = header + "\n" + body + footer

# ===  Надсилання у Telegram ===
payload = {
    'chat_id': CHAT_ID,
    'text': message,
    'parse_mode': 'HTML'
}

response = requests.post(f"https://api.telegram.org/bot8061519904:AAGI3cwN4fOVQ2sb59BkO5IwgqmkzKFm_0E/sendMessage", data=payload)
print("📬 Статус:", response.status_code)
