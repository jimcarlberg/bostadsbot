import asyncio
from playwright.async_api import async_playwright
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

SEARCH_URL = "https://bostad.stockholm.se/bostad?minAntalRum=4&vanlig=1&s=59.29903&n=59.40141&w=17.95647&e=18.16280&sort=annonserad-fran-desc"
SENDER_EMAIL = os.getenv("EMAIL_USER")
APP_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVER_EMAIL = "hello@jimcarlberg.com"

async def scrape_bostader():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(SEARCH_URL)
        await page.wait_for_selector(".search-result-item")
        items = await page.query_selector_all(".search-result-item")

        results = []
        for item in items:
            title_el = await item.query_selector(".search-result-heading")
            link_el = await item.query_selector("a")
            info_el = await item.query_selector(".search-result-summary")

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

async def main():
    results = await scrape_bostader()
    if results:
        send_email(results)
    else:
        print("Inga nya annonser hittades.")

if __name__ == "__main__":
    asyncio.run(main())
