
import asyncio
from playwright.async_api import async_playwright
import csv

browser_global = None
context_global = None

async def iniciar_login(login_status):
    global browser_global, context_global
    async with async_playwright() as p:
        browser_global = await p.chromium.launch(headless=False)
        context_global = await browser_global.new_context()
        page = await context_global.new_page()
        await page.goto("https://shopee.com.br/buyer/login")
        print("Aguardando login manual...")

        # Espera até detectar cookies válidos
        for _ in range(600):
            cookies = await context_global.cookies()
            if any("SPC_EC" in c["name"] for c in cookies):
                login_status["cookies_ok"] = True
                print("Login detectado.")
                break
            await asyncio.sleep(1)

async def verificar_login():
    cookies = await context_global.cookies()
    return any("SPC_EC" in c["name"] for c in cookies)

async def raspar_categoria(url):
    global context_global
    page = await context_global.new_page()
    await page.goto(url)
    await page.wait_for_timeout(5000)

    produtos = await page.query_selector_all("a[data-sqe='link']")
    links = []
    for p in produtos:
        href = await p.get_attribute("href")
        if href:
            links.append("https://shopee.com.br" + href)

    # Salva em CSV
    with open("/mnt/data/links_extraidos.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Link do Produto"])
        for l in links:
            writer.writerow([l])

    return f"{len(links)} links extraídos e salvos!"
