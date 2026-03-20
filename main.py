import cloudscraper
from bs4 import BeautifulSoup
import time
import os
import requests
import re

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Aapki saari links yahan hain. Comma aur duplicates script khud handle kar legi!
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
https://www.sheinindia.in/shein-shein-relaxed-fit-drop-shoulder-typographic-chest-print-sweatshirt/p/443383710_brown?user=old,
https://www.sheinindia.in/shein-shein-relaxed-fit-drop-shoulder-typographic-chest-print-crew-sweatshirt/p/443381346_maroon?user=old,
https://www.sheinindia.in/shein-shein-raglan-sleeve-typographic-chest-print-crew-tshirt/p/443382529_navy?user=old
"""

# Yeh formula apne aap text mein se saare links dhoondh lega aur duplicates hata dega
LINKS = list(set(re.findall(r'(https://www\.sheinindia\.in/[^\s,]+)', RAW_LINKS)))

# Items ka status yaad rakhne ke liye dictionary
item_states = {}

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "disable_web_page_preview": True}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram error: {e}")

def check_shein_item(url):
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
    try:
        response = scraper.get(url, timeout=20)
        
        if response.status_code == 403:
            return "ERROR", "Block ho gaya"

        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text().lower()
        
        # Check if out of stock text is on the page (Jaisa aapke screenshot mein tha)
        if "out of stock" in page_text:
            return "OUT_OF_STOCK", None
            
        # Agar out of stock nahi hai, toh price dhoondho
        price_element = soup.find(class_=re.compile(r'price', re.I)) 
        
        if price_element:
            price = price_element.text.strip()
            price = re.sub(r'\s+', ' ', price)
            return "IN_STOCK", price
        else:
            # Agar direct class se price nahi mila, toh ₹ symbol dhoondhne ka try karo
            rupee_element = soup.find(string=re.compile(r'₹'))
            if rupee_element:
                return "IN_STOCK", rupee_element.strip()
            return "IN_STOCK", "Price website par check karein"
            
    except Exception as e:
        return "ERROR", str(e)

def main():
    print(f"Total {len(LINKS)} unique links mili hain. Smart Tracker start ho raha hai...")
    send_telegram_message(f"🥷 Smart Tracker Start!\nTotal Items: {len(LINKS)}\n\nAb main chupchap nazar rakhunga. Jaise hi koi item IN STOCK aayega, main turant price ke sath aapko message bhejunga. No spam! 😎")
    
    # Shuru mein sabko "OUT_OF_STOCK" maan lete hain
    for link in LINKS:
        item_states[link] = "OUT_OF_STOCK"
        
    while True:
        for index, link in enumerate(LINKS):
            status, price_or_error = check_shein_item(link)
            
            # Agar item In Stock hai aur pehle Out of Stock tha
            if status == "IN_STOCK":
                if item_states[link] != "IN_STOCK":
                    msg = f"🎉 **ITEM IN STOCK AAGAYA!** 🎉\n\n**Price:** {price_or_error}\n**Jaldi order karo:** {link}"
                    send_telegram_message(msg)
                    # Status update kar do taaki dobara same item ka message na aaye
                    item_states[link] = "IN_STOCK"
                    
            elif status == "OUT_OF_STOCK":
                # Agar item wapas out of stock ho gaya
                item_states[link] = "OUT_OF_STOCK"
            
            # Har link check karne ke baad 8 seconds ruko taaki website block na kare
            time.sleep(8)
            
        print("Ek round complete. Waiting for 5 mins...")
        time.sleep(300)

if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("ERROR: Tokens missing hain!")
    elif len(LINKS) == 0:
        print("ERROR: Koi links nahi mili.")
    else:
        main()
        
