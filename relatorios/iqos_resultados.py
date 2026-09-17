from datetime import datetime
import time

from relatorios.compensacao import (
    exportar,
    apertar_ok,
    atualizar_pagina
)

print("IQOS RESULTADOS IMPORTADO")


def obter_mes_iqos(periodo_inicio):

    data = datetime.strptime(
        periodo_inicio,
        "%d/%m/%Y %H:%M:%S"
    )

    meses = {
        1: "JAN",
        2: "FEV",
        3: "MAR",
        4: "ABR",
        5: "MAI",
        6: "JUN",
        7: "JUL",
        8: "AGO",
        9: "SET",
        10: "OUT",
        11: "NOV",
        12: "DEZ"
    }

    return meses[data.month]


async def desmarcar_somente_oficial(
    page
):

    try:

        checkbox = page.locator(
            "#somenteOficial"
        )

        marcado = await checkbox.is_checked()

        if marcado:

            await checkbox.click()

            print(
                "[OK] Somente Oficial desmarcado."
            )

        else:

            print(
                "[INFO] Somente Oficial já estava desmarcado."
            )

    except Exception as erro:

        raise Exception(
            f"Erro ao alterar Somente Oficial: {erro}"
        )


async def clicar_listar(
    page
):

    await page.get_by_role(
        "button",
        name="Listar"
    ).click()

    print(
        "[OK] Botão Listar acionado."
    )


async def expandir_item_indice(
    page,
    texto,
    indice=0
):

    linhas = page.locator(
        "tr"
    ).filter(
        has_text=texto
    )

    linha = linhas.nth(indice)

    await linha.wait_for(
        state="visible",
        timeout=120000
    )

    botao = linha.locator(
        "button.p-treetable-toggler"
    )

    await botao.click()

    print(
        f"[OK] Expandido: {texto} (indice={indice})"
    )


async def abrir_insumos_resultado(
    page
):

    linha_resultado = page.locator(
        "tr"
    ).filter(
        has_text="RESULTADO"
    ).first

    await linha_resultado.wait_for(
        state="visible",
        timeout=120000
    )

    texto = await linha_resultado.inner_text()

    print(
        f"[DEBUG] Resultado encontrado:\n{texto}"
    )

    dropdown = linha_resultado.locator(
        "button.p-splitbutton-dropdown"
    )

    await dropdown.wait_for(
        state="visible",
        timeout=120000
    )

    await dropdown.scroll_into_view_if_needed()

    await page.wait_for_timeout(
        1000
    )

    try:

        await dropdown.click(
            force=True
        )

    except Exception:

        await dropdown.evaluate(
            "(e) => e.click()"
        )

    await page.wait_for_timeout(
        2000
    )

    menu_insumos = page.get_by_text(
        "Insumos",
        exact=True
    )

    await menu_insumos.wait_for(
        state="visible",
        timeout=120000
    )

    await menu_insumos.click()

    print(
        "[OK] Insumos selecionado."
    )


async def abrir_aba_insumos(
    page
):

    aba = page.locator(
        '[role="tab"]'
    ).filter(
        has_text="Insumos [ATENDIMENTO_CHEIO]"
    ).first

    await aba.wait_for(
        state="visible",
        timeout=120000
    )

    await aba.click()

    print(
        "[OK] Aba Insumos aberta."
    )


async def abrir_downloads_iqos(
    page
):

    try:

        popover = page.locator(
            "div.p-popover-content"
        )

        if await popover.count() > 0:

            try:

                if await popover.is_visible():

                    print(
                        "[INFO] Central Downloads IQOS já está aberta."
                    )

                    return

            except Exception:

                pass

        envelope = page.locator(
            "div.notification-wrapper"
        )

        await envelope.wait_for(
            state="visible",
            timeout=120000
        )

        await envelope.scroll_into_view_if_needed()

        await page.wait_for_timeout(
            1000
        )

        await envelope.click(
            force=True
        )

        await page.wait_for_timeout(
            2000
        )

        await popover.wait_for(
            state="visible",
            timeout=30000
        )

        print(
            "[OK] Central Downloads IQOS aberta."
        )

    except Exception as erro:

        raise Exception(
            f"Erro ao abrir Central Downloads IQOS: {erro}"
        )


async def aguardar_processamento_iqos(
    page,
    timeout=600
):

    inicio = time.time()

    while True:

        try:

            await abrir_downloads_iqos(
                page
            )

        except Exception:

            pass

        cards = page.locator(
            "div.p-card-content"
        )

        total = await cards.count()

        print(
            f"[DEBUG] Cards encontrados: {total}"
        )

        if total > 0:

            for i in range(total):

                try:

                    card = cards.nth(i)

                    texto = await card.inner_text()

                    texto_upper = texto.upper()

                    print(
                        f"\n[DEBUG] CARD {i}\n{texto}\n"
                    )

                    if (
                        "ATENDIMENTO_CHEIO"
                        not in texto_upper
                    ):
                        continue

                    if "CONCLUÍDO" in texto_upper:

                        print(
                            "[OK] Exportação concluída."
                        )

                        return "CONCLUIDO"

                    if "REMOVIDO" in texto_upper:

                        print(
                            "[ERRO] Exportação removida."
                        )

                        return "REMOVIDO"

                except Exception:

                    pass

        if (
            time.time() - inicio
        ) > timeout:

            raise TimeoutError(
                "Tempo excedido aguardando exportação IQOS."
            )

        await page.wait_for_timeout(
            5000
        )                        

async def baixar_arquivo_iqos(
    page
):

    card = page.locator(
        "div.p-card-content"
    ).filter(
        has_text="ATENDIMENTO_CHEIO"
    ).first

    await card.wait_for(
        state="visible",
        timeout=120000
    )

    botao_download = card.locator(
        "button.p-button-secondary.p-button-icon-only"
    )

    await botao_download.wait_for(
        state="visible",
        timeout=120000
    )

    async with page.expect_download() as download_info:

        await botao_download.click()

    download = await download_info.value

    caminho = (
        f"downloads/{download.suggested_filename}"
    )

    await download.save_as(
        caminho
    )

    print(
        f"[OK] Arquivo salvo: {caminho}"
    )

    return caminho


async def processar(
    page,
    info,
    periodo_inicio,
    periodo_fim
):

    print(
        "=== IQOS RESULTADOS ==="
    )

    mes = obter_mes_iqos(
        periodo_inicio
    )

    print(
        f"[INFO] Mês identificado: {mes}"
    )

    print(
        "1- Desmarcando Somente Oficial"
    )

    await desmarcar_somente_oficial(
        page
    )

    print(
        "2- Clicando em Listar"
    )

    await clicar_listar(
        page
    )

    await page.wait_for_timeout(
        5000
    )

    print(
        "3- Expandindo primeiro ATENDIMENTO_CHEIO"
    )

    await expandir_item_indice(
        page,
        "ATENDIMENTO_CHEIO",
        0
    )

    await page.wait_for_timeout(
        1500
    )

    print(
        "4- Expandindo segundo ATENDIMENTO_CHEIO"
    )

    await expandir_item_indice(
        page,
        "ATENDIMENTO_CHEIO",
        1
    )

    await page.wait_for_timeout(
        1500
    )

    print(
        f"5- Expandindo mês {mes}"
    )

    await expandir_item_indice(
        page,
        mes,
        0
    )

    await page.wait_for_timeout(
        1500
    )

    print(
        "6- Expandindo DIARIO"
    )

    await expandir_item_indice(
        page,
        "DIARIO",
        0
    )

    await page.wait_for_timeout(
        1500
    )

    print(
        "7- Expandindo CONJ_ELETRICO"
    )

    await expandir_item_indice(
        page,
        "CONJ_ELETRICO",
        0
    )

    await page.wait_for_timeout(
        3000
    )

    print(
        "8- Abrindo menu Insumos"
    )

    await abrir_insumos_resultado(
        page
    )

    await page.wait_for_timeout(
        3000
    )

    print(
        "9- Abrindo aba Insumos"
    )

    await abrir_aba_insumos(
        page
    )

    await page.wait_for_timeout(
        2000
    )

    print(
        "10- Exportando CSV"
    )

    await exportar(
        page
    )

    print(
        "11- Confirmando"
    )

    await apertar_ok(
        page
    )

    print(
        "12- Atualizando página"
    )

    await atualizar_pagina(
        page
    )

    await page.wait_for_load_state(
    "networkidle"
    )

    await page.wait_for_timeout(
    3000
    )

    print(
        "13- Abrindo central de downloads IQOS"
    )

    await abrir_downloads_iqos(
        page
    )

    print(
        "14- Aguardando processamento"
    )

    status_exportacao = await aguardar_processamento_iqos(
        page
    )

    if status_exportacao == "REMOVIDO":

        return {
            "status": "REMOVIDO",
            "arquivo": info["nome_arquivo"]
        }

    print(
        "15- Reabrindo central de downloads"
    )

    await abrir_downloads_iqos(
        page
    )

    print(
        "16- Baixando arquivo"
    )

    await baixar_arquivo_iqos(
        page
    )

    print(
        "[OK] IQOS finalizado."
    )

    return {
        "status": "CONCLUIDO",
        "arquivo": info["nome_arquivo"]
    }