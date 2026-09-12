import asyncio
import importlib
import os

os.makedirs("downloads", exist_ok=True)

from playwright.async_api import async_playwright
from auth import fazer_login
from config import RELATORIOS

print("DOWNLOADER IMPORTADO")


async def baixar_um_relatorio(context, info, periodo_inicio, periodo_fim):
    """
    Abre UMA aba nova dentro do context compartilhado (sessão já logada)
    e delega todo o fluxo específico para o módulo indicado em info["modulo"].
    """
    page = await context.new_page()

    try:
        await page.goto(info["url"])

        print(f"\n===== {info['nome_arquivo']} =====")
        print("URL depois do goto:", page.url)

        if "login" in page.url.lower():
            raise Exception(
                f"Redirecionado para login. URL atual: {page.url}"
            )

        # Importa dinamicamente relatorios/<modulo>.py e chama processar(...)
        modulo = importlib.import_module(f"relatorios.{info['modulo']}")

        await modulo.processar(page, info, periodo_inicio, periodo_fim)

        print(f"[OK] {info['nome_arquivo']} finalizado.")

    except Exception as erro:
        print(f"[ERRO] {info['nome_arquivo']}: {erro}")

    finally:
        await page.close()


async def baixar_todos_os_relatorios(periodo_inicio, periodo_fim):
    print("Entrou na função baixar_todos_os_relatorios")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel="msedge",
            headless=False
        )

        context = await browser.new_context(
            accept_downloads=True
        )

        # Login uma única vez; todas as abas abaixo reaproveitam a sessão.
        await fazer_login(context)

        # Dispara TODOS os relatórios ao mesmo tempo (uma aba cada).
        tarefas = [
            baixar_um_relatorio(context, info, periodo_inicio, periodo_fim)
            for info in RELATORIOS
        ]

        await asyncio.gather(*tarefas)

        await browser.close()