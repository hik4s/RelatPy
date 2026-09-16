import asyncio
import importlib
import os

from playwright.async_api import async_playwright

from auth import tentar_login
from config import RELATORIOS

os.makedirs(
    "downloads",
    exist_ok=True
)

RESULTADOS_RELATORIOS = []


def exibir_resumo_final():

    print("\n")
    print("=" * 60)
    print("RESUMO FINAL DOS RELATÓRIOS")
    print("=" * 60)

    concluidos = 0
    removidos = 0
    erros = 0

    for item in RESULTADOS_RELATORIOS:

        if item["status"] == "CONCLUIDO":

            concluidos += 1

            print(
                f"\n✅ {item['relatorio']}"
            )

            print(
                "   Status: CONCLUÍDO"
            )

            print(
                f"   Arquivo: {item['arquivo']}"
            )

        elif item["status"] == "REMOVIDO":

            removidos += 1

            print(
                f"\n❌ {item['relatorio']}"
            )

            print(
                "   Status: REMOVIDO"
            )

            print(
                f"   Arquivo: {item['arquivo']}"
            )

        else:

            erros += 1

            print(
                f"\n⚠️ {item['relatorio']}"
            )

            print(
                "   Status: ERRO"
            )

            print(
                f"   Motivo: {item['erro']}"
            )

    print("\n" + "=" * 60)

    print(
        f"Concluídos: {concluidos}"
    )

    print(
        f"Removidos: {removidos}"
    )

    print(
        f"Erros: {erros}"
    )

    print("=" * 60)


async def baixar_um_relatorio(
    context,
    info,
    periodo_inicio,
    periodo_fim
):

    page = await context.new_page()

    try:

        print("\n" + "=" * 60)
        print(
            f"Iniciando módulo: {info['modulo']}"
        )
        print(
            f"Arquivo esperado: {info['nome_arquivo']}"
        )
        print("=" * 60)

        await page.goto(
            info["url"]
        )

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

        resultado = await modulo.processar(
            page,
            info,
            periodo_inicio,
            periodo_fim
        )

        RESULTADOS_RELATORIOS.append({

            "relatorio": info["modulo"],

            "arquivo": resultado["arquivo"],

            "status": resultado["status"]

        })

        print(
            f"[OK] {info['nome_arquivo']} finalizado."
        )

    except Exception as erro:

        print(
            f"[ERRO] {info['nome_arquivo']}: "
            f"{type(erro).__name__}: {erro}"
        )

        RESULTADOS_RELATORIOS.append({

            "relatorio": info["modulo"],

            "arquivo": info["nome_arquivo"],

            "status": "ERRO",

            "erro": str(erro)

        })

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

        exibir_resumo_final()

        await browser.close()