import requests
from bs4 import BeautifulSoup
import time
import os

# Railway Environment Variables se token aur ID fetch karna
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Yahan apni Shein items ki multiple links daalein (comma lagakar)
LINKS = [
    "https://www.shein.com/link-1",
    "https://www.shein.com/link-2",
    "https://www.shein.com/link-3"
]

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram par message bhejne mein error aaya: {e}")

def check_shein_item(url):
    # User-Agent dalna zaruri hai taaki Shein hume bot samajh kar block na kare
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        # Agar block ho gaye toh error return karega
        if response.status_code == 403:
            return "Shein ne bot block kar diya (403 Forbidden)."

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # NOTE: Shein ki website change hoti rehti hai. 
        # Yeh ek general example hai. Aapko apna link open karke 'Inspect' karna hoga 
        # aur price wale element ki sahi 'class' yahan dalni hogi.
        price_element = soup.find('div', class_='price-discount__price') # Yeh class change ho sakti hai
        
        if price_element:
            return f"Current Price: {price_element.text.strip()}"
        else:
            return "Item ka price nahi mila. (Shayad Out of Stock hai ya HTML class badal gayi hai)"
            
    except Exception as e:
        return f"Scraping error: {e}"

def main():
    print("Script start ho gayi hai...")
    send_telegram_message("✅ Aapka Shein Tracker Bot Start ho gaya hai!")
    
    while True:
        for link in LINKS:
            print(f"Checking: {link}")
            status = check_shein_item(link)
            
            # Telegram par message bhejna
            message = f"👗 **Shein Item Update**\nLink: {link}\nStatus: {status}"
            send_telegram_message(message)
            
            # Ek link check karne ke baad 15 seconds rukna taaki IP block na ho
            time.sleep(15) 
        
        print("Saare links check ho gaye. Ab 12 ghante baad firse check karunga...")
        # 12 ghante (43200 seconds) ke liye script pause ho jayegi, fir repeat karegi. 
        # Aap isko apne hisaab se kam zyada kar sakte hain.
        time.sleep(43200) 

if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("ERROR: Telegram Token ya Chat ID missing hai!")
    else:
        main()
      
