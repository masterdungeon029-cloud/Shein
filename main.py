import requests
from bs4 import BeautifulSoup
import time
import os

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Aapki Shein Wishlist ki links
LINKS = [
    "https://sheinindia.onelink.me/ZrSt/abs92v2n",
    "https://sheinindia.onelink.me/ZrSt/lpt4kz9y",
    "https://sheinindia.onelink.me/ZrSt/9rhlr3ir",
    "https://sheinindia.onelink.me/ZrSt/s23mh0uq",
    "https://sheinindia.onelink.me/ZrSt/h2oca6lp",
    "https://sheinindia.onelink.me/ZrSt/xrp94ai6",
    "https://sheinindia.onelink.me/ZrSt/shbvppgo",
    "https://sheinindia.onelink.me/ZrSt/meimljbg",
    "https://sheinindia.onelink.me/ZrSt/5xruolx7",
    "https://sheinindia.onelink.me/ZrSt/olk0nh14",
    "https://sheinindia.onelink.me/ZrSt/m92tr8o0"
]

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    # Lamba message ho toh Telegram automatically handle kar lega
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "disable_web_page_preview": True}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram error: {e}")

def check_shein_item(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    try:
        # allow_redirects=True isliye kyunki onelink.me app links hain jo redirect hote hain
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        
        if response.status_code == 403:
            return "Block ho gaya (403)"

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check if price exists (class names might need adjustment later)
        price_element = soup.find('div', class_='price-discount__price')
        
        if price_element:
            return f"✅ IN STOCK! Price: {price_element.text.strip()}"
        else:
            return "❌ Out of Stock ya HTML element nahi mila"
            
    except Exception as e:
        return "⚠️ Error in checking"

def main():
    print("Fast Script start ho gayi hai...")
    send_telegram_message("🚀 Aapka Fast Shein Tracker start ho gaya hai! Ab har 5 minute mein items check honge.")
    
    while True:
        # Ek message banayenge jisme saare links ka status hoga
        summary_message = "🔄 **Shein Wishlist Update**\n\n"
        
        for index, link in enumerate(LINKS):
            print(f"Checking item {index + 1}/{len(LINKS)}...")
            status = check_shein_item(link)
            
            # Message mein line add karna
            summary_message += f"Item {index + 1}: {status}\nLink: {link}\n\n"
            
            # Har link ke baad 5 second ka wait taaki Shein block na kare
            time.sleep(5) 
            
        # Saare 11 items check hone ke baad ek sath Telegram par message bhejna
        send_telegram_message(summary_message)
        
        print("Saare links check ho gaye. Ab 5 minute baad firse check karunga...")
        # 5 minute (300 seconds) ka wait
        time.sleep(300) 

if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("ERROR: Tokens missing hain!")
    else:
        main()
        
