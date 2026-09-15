import asyncio
import importlib
import os

os.makedirs("downloads", exist_ok=True)

from playwright.async_api import async_playwright
from auth import tentar_login
from config import RELATORIOS


async def baixar_um_relatorio(
    context,
    info,
    periodo_inicio,
    periodo_fim
):
    page = await context.new_page()

    try:

        print("\n" + "=" * 60)
        print(f"Iniciando módulo: {info['modulo']}")
        print(f"Arquivo esperado: {info['nome_arquivo']}")
        print("=" * 60)

        await page.goto(info["url"])

        print(
            f"URL após navegação: {page.url}"
        )

        if "login" in page.url.lower():
            raise Exception(
                f"Redirecionado para login. URL atual: {page.url}"
            )

        modulo = importlib.import_module(
            f"relatorios.{info['modulo']}"
        )

        await modulo.processar(
            page,
            info,
            periodo_inicio,
            periodo_fim
        )

        print(
            f"[OK] {info['nome_arquivo']} finalizado."
        )

    except Exception as erro:

        print(
            f"[ERRO] {info['nome_arquivo']}: "
            f"{type(erro).__name__}: {erro}"
        )

    finally:

        await page.close()


async def baixar_todos_os_relatorios(
    usuario,
    senha,
    periodo_inicio,
    periodo_fim
):
    print(
        "Entrou na função baixar_todos_os_relatorios"
    )

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            channel="msedge",
            headless=False
        )

        context = await browser.new_context(
            accept_downloads=True
        )

        await tentar_login(
            context,
            usuario,
            senha
        )

        print(
            f"Total de relatórios: {len(RELATORIOS)}"
        )

        for info in RELATORIOS:

            print(
                f"\nIniciando: {info['modulo']}"
            )

            await baixar_um_relatorio(
                context,
                info,
                periodo_inicio,
                periodo_fim
            )

        await browser.close()