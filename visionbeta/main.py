
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from playwright.async_api import async_playwright
from utils.scraper import iniciar_login, verificar_login, raspar_categoria

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

login_status = {"cookies_ok": False}

@app.post("/iniciar-login")
async def iniciar():
    login_status["cookies_ok"] = False
    asyncio.create_task(iniciar_login(login_status))
    return {"ok": True}

@app.get("/status-cookies")
async def status():
    return {"ok": login_status["cookies_ok"]}

@app.post("/executar-raspagem")
async def executar(request: Request):
    dados = await request.json()
    url = dados.get("url")
    if not url:
        return JSONResponse(status_code=400, content={"error": "URL inválida"})
    resultado = await raspar_categoria(url)
    return {"ok": True, "result": resultado}


from fastapi.responses import FileResponse
import os

@app.get("/baixar-csv")
async def baixar_csv():
    caminho = "/mnt/data/links_extraidos.csv"
    if os.path.exists(caminho):
        return FileResponse(path=caminho, filename="links_extraidos.csv", media_type="text/csv")
    return JSONResponse(status_code=404, content={"error": "Arquivo CSV não encontrado."})


@app.post("/confirmar-login")
async def confirmar_login():
    from utils.scraper import verificar_login
    ok = await verificar_login()
    if ok:
        login_status["cookies_ok"] = True
        return {"ok": True}
    return {"ok": False, "error": "Login ainda não foi concluído com sucesso."}
