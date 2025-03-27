import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

print("🚀 main.py är igång!")

SEARCH_URL = "https://bostad.stockholm.se/bostad?minAntalRum=4&vanlig=1&s=59.29903&n=59.40141&w=17.95647&e=18.16280&sort=annonserad-fran-desc"
SENDER_EMAIL = os.getenv("EMAIL_USER") or "MISSING_EMAIL"
APP_PASSWORD = os.getenv("EMAIL_PASSWORD") or "MISSING_PASS"
RECEIVER_EMAIL = "hello@jimcarlberg.com"

def fetch_bostader():
    print("🌐 Hämtar HTML från sidan...")
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(SEARCH_URL, headers=headers)
    if response.status_code != 200:
        print(f"❌ Misslyckades att hämta sidan (status {response.status_code})")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    print("🔎 Söker efter annonser i HTML...")
    for li in soup.select("ul.search-list > li"):
        title_el = li.select_one("a.search-list-heading")
        info_el = li.select_one(".search-list-summary")

        title = title_el.text.strip() if title_el else "(no title)"
        link = title_el["href"] if title_el and "href" in title_el.attrs else "#"
        info = info_el.text.strip() if info_el else ""

        results.append({
            "title": title,
            "link": f"https://bostad.stockholm.se{link}",
            "info": info
        })

    print(f"✅ Hittade {len(results)} annonser.")
    return results

def send_email(results):
    print(f"📤 Skickar mejl med {len(results)} annonser...")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Nya bostadsannonser (Stockholm)"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    html = "<html><body><h2>Nya bostadsannonser</h2><ul>"
    for r in results:
        html += f'<li><a href="{r["link"]}">{r["title"]}</a><br>{r["info"]}</li>'
    html += "</ul></body></html>"

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
    print("✅ Mejlet skickades!")

def main():
    results = fetch_bostader()
    if results:
        send_email(results)
    else:
        print("ℹ️ Inga annonser hittades eller sidan var tom.")

if __name__ == "__main__":
    main()
