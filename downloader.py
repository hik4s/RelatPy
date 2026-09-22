import asyncio
import importlib
import os

from playwright.async_api import async_playwright

from auth import tentar_login
from config import RELATORIOS

from core.executor import (
    executar_relatorio,
    executar_lote,
    inicializar_status,
    atualizar_arquivo
)

from core.file_manager import (
    copiar_relatorio_para_servidor
)

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
        print("\n==============================")
        print("MODULO:", info["modulo"])
        print("RESULTADO COMPLETO:")
        print(resultado)
        print("==============================\n")

        arquivo_local = resultado.get(
            "arquivo"
        )
        print(f"[DEBUG] arquivo_local recebido: {arquivo_local}")

        arquivo_rede = None

        try:

            if (
                arquivo_local
                and
                os.path.exists(
                    arquivo_local
                )
            ):

                arquivo_rede = copiar_relatorio_para_servidor(

                    modulo=info["modulo"],

                    caminho_arquivo=arquivo_local,

                    periodo_inicio=periodo_inicio
                )
                
                print(f"[OK] Arquivo local: {arquivo_local}")

                print(f"[OK] Arquivo rede: {arquivo_rede}")

        except Exception as erro:

            print(
                f"[AVISO] Falha ao enviar para rede: {erro}"
            )

        atualizar_arquivo(

            info["modulo"],

            arquivo_local,

            arquivo_rede
        )

        RESULTADOS_RELATORIOS.append({

            "relatorio": info["modulo"],

            "arquivo": arquivo_local,

            "status": resultado["status"]

        })

        print(
            f"[OK] {info['nome_arquivo']} finalizado."
        )

        return resultado

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

        raise

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

    inicializar_status(
        RELATORIOS
    )

    print(
        "PARALELO:",
        [
            r["modulo"]
            for r in RELATORIOS
            if r.get(
                "paralelo",
                False
            )
        ]
    )

    print(
        "SEQUENCIAL:",
        [
            r["modulo"]
            for r in RELATORIOS
            if not r.get(
                "paralelo",
                False
            )
        ]
    )

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            channel="msedge",
            headless=True
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

        paralelos = []
        sequenciais = []

        for info in RELATORIOS:

            if info.get(
                "paralelo",
                False
            ):

                paralelos.append(
                    info
                )

            else:

                sequenciais.append(
                    info
                )

        print(
            f"\nRelatórios paralelos: {len(paralelos)}"
        )

        print(
            f"Relatórios sequenciais: {len(sequenciais)}"
        )

        tarefas = []

        for info in paralelos:

            print(
                f"\nAgendando paralelo: {info['modulo']}"
            )

            tarefas.append(

                executar_relatorio(

                    baixar_um_relatorio(
                        context,
                        info,
                        periodo_inicio,
                        periodo_fim
                    ),

                    info["modulo"]
                )
            )

        if tarefas:

            await executar_lote(
                tarefas
            )

        for info in sequenciais:

            print(
                f"\nExecutando sequencial: {info['modulo']}"
            )

            try:

                await executar_relatorio(

                    baixar_um_relatorio(
                        context,
                        info,
                        periodo_inicio,
                        periodo_fim
                    ),

                    info["modulo"]
                )

            except Exception:

                pass

        exibir_resumo_final()

        await browser.close()