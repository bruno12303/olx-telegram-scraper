# OLX Scraper & Telegram Notifier

An automated bot that monitors new listings on OLX and sends instant notifications via Telegram. The project bypasses anti-bot protections (e.g., Cloudflare/403) by utilizing the `undetected_chromedriver`.

## Key Features
* **Anti-Bot Bypass:** Uses an automated yet "undetectable" headless Chrome browser to effectively bypass OLX security measures.
* **Real-Time Notifications:** Integrates with the Telegram API to send formatted messages (title, price, link) directly to your device.
* **Local Database:** Utilizes a lightweight `SQLite3` database to store unique ad IDs, preventing duplicate notifications.
* **Flexibility:** Configurable check intervals and an easily modifiable target URL (currently configured to search for DDR4 RAM in Silesia under 200 PLN).

## Technologies
* **Python 3**
* **BeautifulSoup4:** Parsing and extracting data from HTML.
* **Undetected Chromedriver:** Managing browser sessions without triggering anti-scraping mechanisms.
* **SQLite3:** Database for tracking ad history.
* **Requests:** Communication with the Telegram API.
* **python-dotenv:** Secure management of environment variables.

## Installation and Setup

1. Clone the repository:
```bash
git clone [https://github.com/bruno12303/olx-telegram-scraper.git](https://github.com/bruno12303/olx-telegram-scraper.git)
cd olx-telegram-scraper
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Telegram Configuration:
Create a `.env` file in the root directory of the project and add your API keys (you can get the token from BotFather on Telegram):
```env
TELEGRAM_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

5. Run the bot:
```bash
python bot_olx.py
```

## Project Structure
* `bot_olx.py` - The main script responsible for scraping and sending messages.
* `requirements.txt` - A list of project dependencies.
* `.env.example` - A template for environment variables (you should create your own `.env` file based on this).
* `olx_ads.db` - (Auto-generated after first run) SQLite database storing processed ads.