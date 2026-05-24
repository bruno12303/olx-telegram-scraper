import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import sqlite3
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

URL = "https://www.olx.pl/elektronika/komputery/podzespoly-i-czesci/slaskie/q-ram-ddr4/?search%5Border%5D=created_at:desc&search%5Bfilter_float_price:to%5D=200&search%5Bfilter_enum_state%5D%5B0%5D=used"
CHECK_INTERVAL = 300

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
    if res is None:
        c.execute('INSERT INTO ads VALUES (?)', (ad_id,))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    requests.post(url, json=payload)

def scrape_olx():
    print("Uruchamiam silnik przeglądarki...")

    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        driver = uc.Chrome(options=options, version_main=144)
        driver.get(URL)

        time.sleep(5) 
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        offers = soup.find_all('div', {'data-cy': 'l-card'})
        
        found_new = 0
        for offer in offers:
            link_tag = offer.find('a')
            if not link_tag: continue
            
            link = link_tag['href']
            if not link.startswith('http'):
                link = "https://www.olx.pl" + link

            try:
                offer_id = link.split('-ID')[-1].split('.html')[0]
            except:
                continue

            if is_new(offer_id):
                title = offer.find('h6').text if offer.find('h6') else "Nowa oferta"
                price = offer.find('p', {'data-testid': 'ad-price'}).text if offer.find('p', {'data-testid': 'ad-price'}) else "Brak ceny"
                
                msg = f"🌟 <b>NOWA OKAZJA OLX!</b>\n\n📝 {title}\n💰 Cena: {price}\n\n🔗 <a href='{link}'>ZOBACZ OGŁOSZENIE</a>"
                send_telegram(msg)
                found_new += 1
        
        print(f"Zakończono skanowanie. Znaleziono nowych: {found_new}")
        driver.quit()

    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        try: driver.quit()
        except: pass

if __name__ == "__main__":
    setup_db()
    print("Bot OLX (Anti-403) wystartował!")
    while True:
        scrape_olx()
        print(f"Czekam {CHECK_INTERVAL} sekund...")
        time.sleep(CHECK_INTERVAL)