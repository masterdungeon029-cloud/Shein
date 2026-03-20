import cloudscraper
from bs4 import BeautifulSoup
import time
import os
import requests
import re
import random

# Railway Environment Variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# --- APKI SAARI LINKS (PURANI + NAYI) ---
RAW_LINKS = """
https://www.sheinindia.in/shein-shein-relaxed-fit-short-sleeve-cuban-collar-overlay-panel-pocket-shirt/p/443327677_coffee?user=old,
https://www.sheinindia.in/shein-shein-medium-length-spread-collar-full-sleeve-checked-shirt/p/443391936_red?user=old,
https://www.sheinindia.in/shein-shein-short-sleeve-striped-textured-polo-tshirt/p/443390489_navyblue?user=old,
https://www.sheinindia.in/shein-shein-drop-shoulder-stranger-things-back-print-crew-tshirt/p/443387042_navy?user=old,
https://www.sheinindia.in/shein-shein-oversized-fit-drop-shoulder-typographic-back-print-crew-tshirt/p/443331617_black?user=old,
https://www.sheinindia.in/shein-shein-fly-with-button-closure-mid-wash-distressed-jeans/p/443384920_darkblue?user=old,
https://www.sheinindia.in/shein-shein-medium-length-spread-collar-full-sleeve-checked-shirt/p/443391936_khaki?user=old,
https://www.sheinindia.in/shein-shein-medium-length-spread-collar-striped-shirt/p/443391935_blue?user=old,
https://www.sheinindia.in/shein-shein-medium-length-short-sleeve-buttoned-polo-tshirt/p/443385948_grey?user=old,
https://www.sheinindia.in/shein-shein-medium-length-short-sleeve-self-design-polo-tshirt/p/443394851_navyblue?user=old,
https://www.sheinindia.in/shein-shein-drop-shoulder-graphic-back-print-crew-tshirt/p/443382800_black?user=old,
https://www.sheinindia.in/shein-shein-drop-shoulder-front--back-graphic-print-crew-tshirt/p/443382820_black?user=old,
https://www.sheinindia.in/shein-shein-house-of-dragon-chest-print-crew-neck-sweatshirt/p/443388931_offwhite?user=old,
https://www.sheinindia.in/shein-shein-medium-length-zipped-collar-ribbed-tshirt/p/443390443_black?user=old,
https://www.sheinindia.in/shein-shein-short-sleeve-contrast-trim-colour-blocked-polo-tshirt/p/443386543_navy?user=old,
https://www.sheinindia.in/shein-shein-short-sleeve-contrast-collar-ribbed-polo-tshirt/p/443385515_seagreen?user=old,
https://www.sheinindia.in/shein-shein-short-sleeve-colour-block-striped-polo-tshirt/p/443382768_black?user=old,
https://www.sheinindia.in/shein-shein-short-sleeve-contrast-striped-polo-tshirt/p/443383304_black?user=old,
https://www.sheinindia.in/shein-shein-short-sleeve-colour-block-striped-polo-tshirt/p/443386542_pistagreen?user=old,
https://www.sheinindia.in/shein-shein-drop-shoulder-numeric-chest-print-crew-tshirt/p/443387444_black?user=old,
https://www.sheinindia.in/shein-shein-relaxed-fit-drop-shoulder-typographic-chest-print-sweatshirt/p/443383710_brown?user=old,
https://www.sheinindia.in/shein-shein-drop-shoulder-short-sleeve-textured-crew-tshirt/p/443387638_blue?user=old,
https://www.sheinindia.in/shein-shein-relaxed-fit-drop-shoulder-typographic-chest-print-crew-sweatshirt/p/443381346_maroon?user=old,
https://www.sheinindia.in/shein-shein-raglan-sleeve-typographic-chest-print-crew-tshirt/p/443382529_navy?user=old,
https://www.sheinindia.in/shein-shein-full-length-fly-with-button-closure-cargo-jeans/p/443384264_darkolive?user=old,
https://www.sheinindia.in/shein-shein-full-length-fly-with-button-closure-cargo-jeans/p/443384264_ltgrey?user=old,
https://www.sheinindia.in/shein-shein-ankle-length-semi-elasticated-waist-pant/p/443381959_cream?user=old,
https://www.sheinindia.in/shein-shein-full-length-fly-with-button-closure-mid-wash-jeans/p/443390726_charcoal?user=old,
https://www.sheinindia.in/shein-shein-full-length-fly-with-button-closure-clean-wash-jeans/p/443383975_olivegreen?user=old,
https://www.sheinindia.in/shein-shein-fly-with-button-closure-drawstring-detail-panelled-jeans/p/443383003_midblue?user=old,
https://www.sheinindia.in/shein-shein-full-length-typographic-placement-print-straight-track-pants/p/443384227_black?user=old,
https://www.sheinindia.in/shein-shein-short-sleeves-graphic-back-print-crew-tshirt/p/443387455_black?user=old,
https://www.sheinindia.in/shein-shein-relaxed-fit-drop-shoulder-typographic-back-print-crew-tshirt/p/443330475_white?user=old,
https://www.sheinindia.in/shein-shein-short-sleeves-graphic-back-print-crew-tshirt/p/443389791_black?user=old,
https://www.sheinindia.in/shein-shein-medium-length-full-sleeve-sweatshirt/p/443318638_beige?user=old,
https://www.sheinindia.in/shein-shein-panelled-light-wash-carpenter-style-cargo-jeans/p/443383999_midblue?user=old
"""

# Extracting unique links and cleaning commas
LINKS = list(set(re.findall(r'(https://www\.sheinindia\.in/[^\s,]+)', RAW_LINKS)))

item_states = {}

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown", "disable_web_page_preview": True}
    try:
        requests.post(url, json=payload)
    except:
        pass

def check_shein_item(url):
    # Mimicking real browsers to avoid bot detection
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
    try:
        response = scraper.get(url, timeout=15)
        if response.status_code != 200:
            return "ERROR", None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        page_content = str(soup).lower()
        
        # --- STRICT CHECKING LOGIC ---
        # Label check
        is_oos = any(x in page_content for x in ["out of stock", "sold out", "coming soon", "is currently out of stock"])
        
        # Real button check
        add_to_bag_btn = soup.find(string=re.compile('Add to Bag', re.I)) or soup.find('button', {'class': re.compile('add-to-cart|add-bag-btn', re.I)})
        
        # If no OOS text AND button is found, it's likely real stock
        if not is_oos and add_to_bag_btn:
            price = "Price on Site"
            price_element = soup.find(class_=re.compile(r'price', re.I))
            if price_element:
                price = price_element.text.strip()
            return "REAL_STOCK", price
        
        return "OUT", None
            
    except Exception:
        return "ERROR", None

def main():
    print(f"Total Unique Items: {len(LINKS)}")
    send_telegram_message(f"🚨 **ULTRA NITRO + ANTI-GHOST ON**\nTotal unique links: {len(LINKS)}\n\nAb real stock aate hi shor machega! 🔥")
    
    # Initialize state
    for link in LINKS:
        item_states[link] = "OUT"
        
    while True:
        for link in LINKS:
            status, price = check_shein_item(link)
            
            if status == "REAL_STOCK":
                if item_states.get(link) != "IN_STOCK":
                    msg = f"✅ **PRODUCT IN STOCK!**\n💰 **Price:** {price}\n🛒 **Loot Lo:** {link}"
                    send_telegram_message(msg)
                    item_states[link] = "IN_STOCK"
            elif status == "OUT":
                item_states[link] = "OUT"
            
            # 2 seconds gap between items (Nitro speed)
            time.sleep(2)
            
        print("Round complete. Restarting in 20 seconds...")
        time.sleep(20) # Fast cycle restart

if __name__ == "__main__":
    main()
    
