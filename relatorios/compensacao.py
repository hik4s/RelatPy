import os

print("COMPENSACAO IMPORTADO")


async def processar(page, info, periodo_inicio, periodo_fim):
    """
    Ponto de entrada padrão chamado pelo downloader.py.
    Executa toda a sequência específica do relatório de Compensação.
    """
    print("1- Selecionando Empresa")
    await selecionar_empresa(page, info["empresa_desejada"])

    print("2- Preenchendo datas")
    await preencher_datas_compensacao(page, periodo_inicio, periodo_fim)

    print("3- Preenchendo período")
    await selecionar_periodo_apuracao(page, info["periodo_apuracao"])

    print("[OK] Empresa, datas e período preenchidos.")

    print("4- Pesquisando")
    await pesquisar(page)

    await abrir_relatorio(page)
    await selecionar_relatorio(page)
    await abrir_detalhamento(page)
    await abrir_aba_detalhamento_compensacao(page)
    await exportar(page)
    await apertar_ok(page)
    await atualizar_pagina(page)
    await abrir_downloads(page)
    await aguardar_processamento(page)
    await abrir_downloads(page)
    await baixar_arquivo(page, info["nome_arquivo"])


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
    await page.wait_for_timeout(5000)
    print("[OK] Página atualizada.")


async def abrir_downloads(page):
    await page.locator("div.notification-btn").click()
    await page.wait_for_timeout(3000)
    print("[OK] Central de downloads aberta.")


async def aguardar_processamento(page):
    """
    Atualiza a página enquanto existir um download com status PROCESSANDO.
    """
    while True:
        badge_processando = page.get_by_text("PROCESSANDO", exact=True)

        if await badge_processando.count() == 0:
            print("[OK] Nenhum processamento pendente.")
            break

        print("[INFO] Download ainda processando. Atualizando...")
        await page.reload()
        await page.wait_for_timeout(3000)


async def baixar_arquivo(page, nome_arquivo_esperado=None):
    """
    Baixa o arquivo da central de downloads.

    IMPORTANTE (rodando em paralelo): quando várias abas processam
    relatórios ao mesmo tempo, a central de downloads pode listar
    itens de OUTROS relatórios também. Por isso, em vez de pegar
    sempre "o primeiro botão", procuramos a LINHA cujo texto bate
    com o nome do relatório atual antes de clicar em baixar.
    """
    os.makedirs("downloads", exist_ok=True)

    if nome_arquivo_esperado:
        # Tenta achar a linha da central de downloads que menciona
        # esse relatório especificamente (ajuste o texto de busca
        # conforme o nome/rótulo real que aparece na central).
        linha = page.locator(
            f'tr:has-text("{nome_arquivo_esperado.split(".")[0]}")'
        ).first
        botao_download = linha.locator(
            "button.ui-button-secondary.p-button-icon-only"
        )
    else:
        botao_download = page.locator(
            "button.ui-button-secondary.p-button-icon-only"
        ).first

    print("Botão de download localizado:", await botao_download.count())

    async with page.expect_download() as download_info:
        await botao_download.click()

    download = await download_info.value

    nome_arquivo = nome_arquivo_esperado or download.suggested_filename

    caminho = os.path.join("downloads", nome_arquivo)

    await download.save_as(caminho)

    print(f"[OK] Arquivo baixado: {caminho}")