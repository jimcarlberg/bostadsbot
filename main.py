import asyncio
from playwright.async_api import async_playwright
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

print("🚀 main.py är igång!")

SEARCH_URL = "https://bostad.stockholm.se/bostad?minAntalRum=4&vanlig=1&s=59.29903&n=59.40141&w=17.95647&e=18.16280&sort=annonserad-fran-desc"
SENDER_EMAIL = os.getenv("EMAIL_USER") or "MISSING_EMAIL"
APP_PASSWORD = os.getenv("EMAIL_PASSWORD") or "MISSING_PASS"
RECEIVER_EMAIL = "hello@jimcarlberg.com"

if "MISSING" in SENDER_EMAIL or "MISSING" in APP_PASSWORD:
    print("❗️Saknar e-postuppgifter! Kontrollera GitHub Secrets.")
    exit(1)

async def scrape_bostader():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("🔍 Navigerar till bostad.stockholm.se...")
        await page.goto(SEARCH_URL, wait_until="load")
        print("✅ Sidan laddad, hanterar cookies...")

        try:
            await page.locator("button:has-text('Avvisa alla')").click(timeout=5000)
            print("🍪 Cookie-popup avvisad.")
        except:
            print("ℹ️ Ingen cookie-popup att avvisa.")

        # Extra lång väntan
        print("⏳ Väntar extra 10 sekunder för att allt ska laddas...")
        await page.wait_for_timeout(10000)

        # Scrolla ner
        await page.mouse.wheel(0, 2000)
        await page.wait_for_timeout(1000)

        # Hämta alla annonser direkt utan wait_for_selector
        items = await page.query_selector_all("ul.search-list > li")
        print(f"🔎 Direkt DOM-sökning hittade {len(items)} annonser.")

        if not items:
            await page.screenshot(path="screenshot.png", full_page=True)
            html = await page.content()
            with open("page.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("📸 Skärmdump + HTML sparad.")
            await browser.close()
            return []

        results = []
        for item in items:
            title_el = await item.query_selector("a.search-list-heading")
            link_el = await item.query_selector("a")
            info_el = await item.query_selector(".search-list-summary")

            title = await title_el.inner_text() if title_el else "(no title)"
            link = await link_el.get_attribute("href") if link_el else "#"
            info = await info_el.inner_text() if info_el else ""

            results.append({
                "title": title.strip(),
                "link": f"https://bostad.stockholm.se{link.strip()}",
                "info": info.strip()
            })

        await browser.close()
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

async def main():
    results = await scrape_bostader()
    if results:
        send_email(results)
    else:
        print("ℹ️ Inga nya annonser hittades.")

if __name__ == "__main__":
    asyncio.run(main())
