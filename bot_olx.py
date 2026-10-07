import os
import re
import sqlite3
import subprocess
import time
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = 300


def get_thread_id(var_name):
    val = os.getenv(var_name)
    return int(val) if val and val.isdigit() else None


CATEGORIES = [
    {
        "name": "Dyski",
        "thread_id": get_thread_id("THREAD_DYSKI"),
        "urls": [
            "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-512-gb-ssd/?courier=1&search%5Bfilter_enum_diskcapacity_components_and_parts%5D%5B0%5D=257gb-512gb&search%5Bfilter_enum_diskcapacity_components_and_parts%5D%5B1%5D=513gb-1000gb&search%5Bfilter_enum_disktype_components_and_parts%5D%5B0%5D=ssd&search%5Bfilter_enum_state%5D%5B0%5D=new&search%5Bfilter_enum_state%5D%5B1%5D=used&search%5Bfilter_float_price%3Ato%5D=180",
            "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/dyski/q-dysk-ssd-2tb/?courier=1&search%5Bfilter_enum_diskcapacity_components_and_parts%5D%5B0%5D=1tb-and-more&search%5Bfilter_enum_disktype_components_and_parts%5D%5B0%5D=ssd&search%5Bfilter_float_price%3Ato%5D=700"
        ]
    },
    {
        "name": "Karty graficzne",
        "thread_id": get_thread_id("THREAD_GPU"),
        "urls": [
            "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-rtx-4060ti/?courier=1&search%5Bfilter_enum_state%5D%5B0%5D=used&search%5Bfilter_enum_state%5D%5B1%5D=new&search%5Bfilter_float_price%3Ato%5D=1100",
            "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-rtx-4060/?courier=1&search%5Bfilter_enum_state%5D%5B0%5D=used&search%5Bfilter_enum_state%5D%5B1%5D=new&search%5Bfilter_float_price%3Ato%5D=1050",
            "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-rtx3070/?courier=1&search%5Bfilter_float_price%3Afrom%5D=700&search%5Bfilter_float_price%3Ato%5D=1100&search%5Border%5D=created_at%3Adesc",
            "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-rx6700-xt/?courier=1&search%5Bfilter_enum_graphicscardmemory%5D%5B0%5D=10gb-12gb&search%5Bfilter_enum_state%5D%5B0%5D=used&search%5Bfilter_enum_state%5D%5B1%5D=new&search%5Bfilter_float_price%3Afrom%5D=800&search%5Bfilter_float_price%3Ato%5D=1100",
            "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-rtx3060ti/?courier=1&search%5Bfilter_enum_state%5D%5B0%5D=used&search%5Bfilter_enum_state%5D%5B1%5D=new&search%5Bfilter_float_price%3Afrom%5D=700&search%5Bfilter_float_price%3Ato%5D=1000"
        ]
    },
    {
        "name": "Procesory",
        "thread_id": get_thread_id("THREAD_CPU"),
        "urls": [
            "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-ryzen-5-3600/?courier=1&search%5Bfilter_float_price%3Ato%5D=200"
        ]
    },
    {
        "name": "RAM",
        "thread_id": get_thread_id("THREAD_RAM"),
        "urls": [
            "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-16gb-ddr4/?courier=1&search%5Bfilter_enum_state%5D%5B0%5D=new&search%5Bfilter_enum_state%5D%5B1%5D=used&search%5Bfilter_enum_totalcapacity%5D%5B0%5D=12gb-16gb&search%5Bfilter_enum_typeofmemory%5D%5B0%5D=ddr4&search%5Bfilter_float_price%3Ato%5D=220"
        ]
    },
    {
        "name": "Płyty główne",
        "thread_id": get_thread_id("THREAD_MOBO"),
        "urls": [
            "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-a520/?courier=1&search%5Bfilter_enum_state%5D%5B0%5D=new&search%5Bfilter_enum_state%5D%5B1%5D=used&search%5Bfilter_float_price%3Ato%5D=200",
            "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-b450/?courier=1&search%5Bfilter_enum_state%5D%5B0%5D=new&search%5Bfilter_enum_state%5D%5B1%5D=used&search%5Bfilter_float_price%3Ato%5D=200",
            "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-b550/?courier=1&search%5Bfilter_enum_state%5D%5B0%5D=used&search%5Bfilter_enum_state%5D%5B1%5D=new&search%5Bfilter_float_price%3Ato%5D=200"
        ]
    },
    {
        "name": "Zasilacze",
        "thread_id": get_thread_id("THREAD_PSU"),
        "urls": [
            "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-zasilacz-700w/?courier=1&search%5Bfilter_enum_state%5D%5B0%5D=new&search%5Bfilter_enum_state%5D%5B1%5D=used&search%5Bfilter_float_price%3Ato%5D=120",
            "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-zasilacz-650w/?courier=1&search%5Bfilter_enum_state%5D%5B0%5D=new&search%5Bfilter_enum_state%5D%5B1%5D=used",
            "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-zasilacz-600w/?courier=1&search%5Bfilter_enum_state%5D%5B0%5D=used&search%5Bfilter_enum_state%5D%5B1%5D=new&search%5Bfilter_float_price%3Ato%5D=120"
        ]
    },
    {
        "name": "Chłodzenia",
        "thread_id": get_thread_id("THREAD_COOLING"),
        "urls": [
            "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-spartan-5/?courier=1&search%5Bfilter_float_price%3Ato%5D=50",
            "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-fera-3/?courier=1&search%5Bfilter_float_price%3Ato%5D=45",
            "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/q-fera-5/?courier=1&search%5Bfilter_float_price%3Ato%5D=50"
        ]
    }
]


def get_chrome_major_version():
    try:
        cmd = r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version'
        output = subprocess.check_output(cmd, shell=True).decode()
        match = re.search(r'version\s+REG_SZ\s+(\d+)\.', output)
        if match:
            return int(match.group(1))
    except Exception:
        pass
    return None


def setup_db():
    conn = sqlite3.connect('olx_ads.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS ads (id TEXT PRIMARY KEY)')
    conn.commit()
    conn.close()


def is_new(ad_id):
    conn = sqlite3.connect('olx_ads.db')
    c = conn.cursor()
    c.execute('SELECT id FROM ads WHERE id=?', (ad_id,))
    res = c.fetchone()
    conn.close()
    return res is None


def mark_as_read(ad_id):
    conn = sqlite3.connect('olx_ads.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO ads VALUES (?)', (ad_id,))
    conn.commit()
    conn.close()


def send_telegram(text, image_url=None, thread_id=None, max_retries=3):
    if not TOKEN or not CHAT_ID:
        print("Brak tokenu lub ID czatu w .env!")
        return False

    if image_url:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        payload = {
            "chat_id": CHAT_ID,
            "photo": image_url,
            "caption": text,
            "parse_mode": "HTML"
        }
    else:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        }

    if thread_id:
        payload["message_thread_id"] = thread_id

    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(url, json=payload, timeout=20)
            if resp.status_code == 200:
                return True

            if image_url and resp.status_code != 200:
                fallback_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                fallback_payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
                if thread_id:
                    fallback_payload["message_thread_id"] = thread_id
                fb_resp = requests.post(fallback_url, json=fallback_payload, timeout=20)
                if fb_resp.status_code == 200:
                    return True

            print(f"Telegram API błąd {resp.status_code}: {resp.text}")
        except requests.exceptions.RequestException as e:
            print(f"Próba wysyłki {attempt}/{max_retries} nieudana: {e}")
            time.sleep(2)

    return False


def extract_title(offer):
    """Wyciąga właściwy tytuł niezależnie od użytego tagu HTML w danej wersji OLX."""
    for tag in ['h4', 'h6', 'h5']:
        el = offer.find(tag)
        if el and el.text.strip():
            return el.text.strip()

    img = offer.find('img')
    if img and img.get('alt') and len(img['alt'].strip()) > 3:
        return img['alt'].strip()

    link = offer.find('a')
    if link and link.text.strip():
        return link.text.strip()

    return "Nowa oferta"


def extract_image(offer):
    """Wyciąga bezpośredni adres URL zdjęcia z miniaturki ogłoszenia."""
    img = offer.find('img')
    if not img:
        return None

    candidates = [
        img.get('src'),
        img.get('data-src'),
        img.get('data-srcset'),
        img.get('srcset')
    ]

    for val in candidates:
        if not val:
            continue
        urls = [part.strip().split(' ')[0] for part in val.split(',') if part.strip()]
        for u in urls:
            if u.startswith('http') and not u.endswith('.svg') and 'placeholder' not in u:
                return u

    return None


def scrape_category(driver, category):
    name = category["name"]
    urls = category.get("urls", [])
    thread_id = category.get("thread_id")
    category_new = 0

    print(f"\n[+] Rozpoczynam kategorię: {name} (liczba linków: {len(urls)})")

    for idx, url in enumerate(urls, start=1):
        print(f"[{name}] Sprawdzam link {idx}/{len(urls)}...")
        driver.get(url)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-cy='l-card']"))
            )
        except Exception:
            print(f"[{name}] Brak ofert lub limit czasu dla linku {idx}.")
            continue

        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)
        except Exception:
            pass

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        offers = soup.find_all('div', {'data-cy': 'l-card'})

        for offer in offers:
            link_tag = offer.find('a')
            if not link_tag or 'href' not in link_tag.attrs:
                continue

            link = link_tag['href']
            if not link.startswith('http'):
                link = "https://www.olx.pl" + link

            try:
                offer_id = link.split('-ID')[-1].split('.html')[0]
            except Exception:
                continue

            if is_new(offer_id):
                title = extract_title(offer)
                image_url = extract_image(offer)

                price_tag = offer.find('p', {'data-testid': 'ad-price'})
                price = price_tag.text.strip() if price_tag else "Brak ceny"

                msg = (
                    f"🌟 <b>NOWA OKAZJA [{name.upper()}]!</b>\n\n"
                    f"📝 <b>{title}</b>\n"
                    f"💰 Cena: {price}\n\n"
                    f"🔗 <a href='{link}'>ZOBACZ OGŁOSZENIE</a>"
                )

                if send_telegram(msg, image_url=image_url, thread_id=thread_id):
                    mark_as_read(offer_id)
                    category_new += 1
                else:
                    print(f"Pominięto zapis ID {offer_id} - ponowimy w kolejnym cyklu.")

        time.sleep(2)

    print(f"[{name}] Zakończono kategorię. Nowych ofert: {category_new}")
    return category_new


def run_cycle():
    print("Uruchamiam silnik przeglądarki...")
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    major_version = get_chrome_major_version()
    driver = None

    try:
        if major_version:
            driver = uc.Chrome(options=options, version_main=major_version)
        else:
            driver = uc.Chrome(options=options)

        total_new = 0
        for category in CATEGORIES:
            total_new += scrape_category(driver, category)
            time.sleep(3)

        print(f"\n=== Podsumowanie cyklu: {total_new} nowych ogłoszeń. ===")

    except Exception as e:
        print(f"Wystąpił błąd ogólny silnika: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


if __name__ == "__main__":
    setup_db()
    print("Bot OLX (Multi-Category Forum + Zdjęcia) wystartował!")
    while True:
        run_cycle()
        print(f"\nCzekam {CHECK_INTERVAL} sekund...")
        time.sleep(CHECK_INTERVAL)