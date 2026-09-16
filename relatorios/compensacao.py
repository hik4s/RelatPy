import os

print("COMPENSACAO IMPORTADO")


async def processar(
    page,
    info,
    periodo_inicio,
    periodo_fim
):
    """
    Ponto de entrada padrão chamado pelo downloader.py.
    Executa toda a sequência específica do relatório de Compensação.
    """

    print("1- Selecionando Empresa")

    await selecionar_empresa(
        page,
        info["empresa_desejada"]
    )

    print("2- Preenchendo datas")

    await preencher_datas_compensacao(
        page,
        periodo_inicio,
        periodo_fim
    )

    print("3- Preenchendo período")

    await selecionar_periodo_apuracao(
        page,
        info["periodo_apuracao"]
    )

    print(
        "[OK] Empresa, datas e período preenchidos."
    )

    print("4- Pesquisando")

    await pesquisar(page)

    await aguardar_fim_carregamento(
        page
    )

    await abrir_relatorio(page)

    await selecionar_relatorio(page)

    await abrir_detalhamento(page)

    await abrir_aba_detalhamento_compensacao(
        page
    )

    await exportar(page)

    await apertar_ok(page)

    await atualizar_pagina(page)

    await abrir_downloads(page)

    print(
        "8- Aguardando processamento"
    )

    status_exportacao = await aguardar_processamento(
        page
    )

    if status_exportacao == "REMOVIDO":

        print(
            "[ERRO] Exportação removida pelo sistema."
        )

        return {
            "status": "REMOVIDO",
            "arquivo": info["nome_arquivo"]
        }

    print(
        "9- Reabrindo downloads"
    )

    await abrir_downloads(page)

    print(
        "10- Baixando arquivo"
    )

    await baixar_arquivo(
        page,
        info["nome_arquivo"]
    )

    print(
        "[OK] Relatório finalizado."
    )

    return {
        "status": "CONCLUIDO",
        "arquivo": info["nome_arquivo"]
    }


async def selecionar_empresa(page, empresa="ESS"):
    await page.locator("p-select").first.click()

    await page.get_by_text(empresa, exact=True).click()

    valor = await page.locator(
        "p-select span[role='combobox']"
    ).first.inner_text()

    print(f"Empresa selecionada: {valor}")


async def preencher_datas_compensacao(page, data_inicio, data_fim):
    campos = page.locator("p-datepicker input.p-datepicker-input")

    campo_inicio = campos.nth(0)
    campo_fim = campos.nth(1)

    await campo_inicio.click()
    await campo_inicio.press("Control+A")
    await campo_inicio.fill(data_inicio)
    await campo_inicio.press("Tab")

    print("Campo início:", await campo_inicio.input_value())

    await campo_fim.click()
    await campo_fim.press("Control+A")
    await campo_fim.fill(data_fim)
    await campo_fim.press("Tab")

    print("Campo fim:", await campo_fim.input_value())


async def selecionar_periodo_apuracao(page, periodo="MENSAL"):
    """
    Seleciona o período de apuração:
    MENSAL / TRIMESTRAL / ANUAL_ACUMULADO
    """
    await page.locator("p-multiselect").click()

    await page.wait_for_selector('li[role="option"]', timeout=0)

    await page.locator(
        f'li[role="option"][aria-label="{periodo}"]'
    ).click()

    await page.keyboard.press("Escape")


async def pesquisar(page):
    await page.get_by_role("button", name="Pesquisar").click()
    await page.wait_for_timeout(1000)
    print("[OK] Pesquisa executada.")

async def aguardar_fim_carregamento(page):

    loading = page.get_by_text(
        "Carregando...",
        exact=True
    )

    try:

        await loading.wait_for(
            state="visible",
            timeout=5000
        )

        print(
            "[INFO] Carregando encontrado. Aguardando finalizar..."
        )

        await loading.wait_for(
            state="hidden",
            timeout=120000
        )

        print(
            "[OK] Carregamento finalizado."
        )

    except Exception:

        # O carregamento nunca apareceu
        print(
            "[INFO] Nenhum carregamento detectado."
        )


async def abrir_relatorio(page):
    await page.get_by_role(
        "tab", name="Relatório de Compensação #0"
    ).click()
    print("[OK] Relatório de Compensação aberto.")


async def selecionar_relatorio(page):
    linha = page.locator('tr[data-p-selectable-row="true"]').first
    await linha.click(button="right")
    print("[OK] Menu de contexto aberto.")


async def abrir_detalhamento(page):
    await page.get_by_text("Detalhar Compensação", exact=True).click()
    await page.wait_for_timeout(2000)
    print("[OK] Detalhamento aberto.")


async def abrir_aba_detalhamento_compensacao(page):
    await page.get_by_role(
        "tab", name="Detalhamento Compensação #1"
    ).click()
    print("[OK] Aba de detalhamento aberta.")


async def exportar(page):
    await page.get_by_role("button", name="Exportar (.csv)").click()
    print("[OK] Exportação solicitada.")


async def apertar_ok(page):
    await page.get_by_role("button", name="OK").click()
    await page.wait_for_timeout(1000)
    print("[OK] Confirmação realizada.")


async def atualizar_pagina(page):

    await page.reload()

    await page.wait_for_load_state(
        "networkidle"
    )

    print(
        "[OK] Página atualizada."
    )


async def abrir_downloads(page):

    for tentativa in range(5):

        popover = page.locator(
            "div.p-popover"
        )

        if await popover.count() > 0:

            try:

                visivel = await popover.first.is_visible()

                if visivel:

                    print(
                        "[OK] Central de downloads já está aberta."
                    )

                    return

            except Exception:
                pass

        print(
            f"[INFO] Abrindo central de downloads (tentativa {tentativa + 1})..."
        )

        await page.locator(
            "div.notification-btn"
        ).click()

        await page.wait_for_timeout(1500)

        popover = page.locator(
            "div.p-popover"
        )

        if await popover.count() > 0:

            try:

                visivel = await popover.first.is_visible()

                if visivel:

                    print(
                        "[OK] Central de downloads aberta."
                    )

                    return

            except Exception:
                pass

    raise Exception(
        "Não foi possível manter a central de downloads aberta."
    )


async def aguardar_processamento(page):

    while True:

        cards = page.locator(
            "div.p-card-content"
        )

        total_cards = await cards.count()

        if total_cards == 0:

            print(
                "[INFO] Nenhum card encontrado."
            )

            await atualizar_pagina(page)

            await abrir_downloads(page)

            continue

        texto = await cards.nth(0).inner_text()

        texto_upper = texto.upper()

        if "PROCESSANDO" in texto_upper:

            print(
                "[INFO] Ainda processando..."
            )

            await atualizar_pagina(page)

            await abrir_downloads(page)

            continue

        if "CONCLUÍDO" in texto_upper:

            print(
                "[OK] Processamento concluído."
            )

            return "CONCLUIDO"

        if "REMOVIDO" in texto_upper:

            print(
                "[ERRO] Exportação removida."
            )

            return "REMOVIDO"

        print(
            "[INFO] Status não identificado."
        )

        await atualizar_pagina(page)

        await abrir_downloads(page)


async def baixar_arquivo(
    page,
    nome_arquivo_esperado
):

    os.makedirs(
        "downloads",
        exist_ok=True
    )

    texto_busca = nome_arquivo_esperado.replace(
        ".csv",
        ""
    )

    print(
        f"Procurando download contendo: {texto_busca}"
    )

    # Aguarda aparecer qualquer card
    for tentativa in range(10):

        cards = page.locator(
            "div.p-card-content"
        )

        total = await cards.count()

        print(
            f"Tentativa {tentativa + 1} - Cards encontrados: {total}"
        )

        if total > 0:
            break

        await page.wait_for_timeout(2000)

    cards = page.locator(
        "div.p-card-content"
    )

    total_cards = await cards.count()

    print(
        f"Cards encontrados: {total_cards}"
    )

    for i in range(total_cards):

        texto = await cards.nth(i).inner_text()

        print(
            f"CARD {i}: {texto}"
        )

        if texto_busca.lower() in texto.lower():

            print(
                f"[OK] Download localizado no CARD {i}"
            )

            botao = cards.nth(i).locator(
                "button.ui-button-secondary.p-button-icon-only"
            ).first

            async with page.expect_download() as download_info:

                await botao.click()

            download = await download_info.value

            caminho = os.path.join(
                "downloads",
                download.suggested_filename
            )

            await download.save_as(caminho)

            print(
                f"[OK] Arquivo baixado: {caminho}"
            )

            return

    raise Exception(
        f"Nenhum download contendo '{texto_busca}' foi encontrado."
    )

    # Diagnóstico dos cards visíveis
    cards = page.locator("div.p-card-content")

    total_cards = await cards.count()

    print(
        f"Cards encontrados: {total_cards}"
    )

    for i in range(total_cards):

        texto = await cards.nth(i).inner_text()

        print(
            f"CARD {i}: {texto}"
        )

        if texto_busca.lower() in texto.lower():

            print(
                f"[OK] Download localizado no CARD {i}"
            )

            botao = cards.nth(i).locator(
                "button.ui-button-secondary.p-button-icon-only"
            ).first

            async with page.expect_download() as download_info:

                await botao.click()

            download = await download_info.value

            caminho = os.path.join(
                "downloads",
                download.suggested_filename
            )

            await download.save_as(caminho)

            print(
                f"[OK] Arquivo baixado: {caminho}"
            )

            return

    raise Exception(
        f"Nenhum card contendo '{texto_busca}' foi encontrado."
    )