RELATORIOS = [
    {
        "modulo": "compensacao",              # nome do arquivo em relatorios/ (sem .py)
        "url": "https://indicadoresenergisaess.scl.corp/sgind/#/relatcompensacao",
        "empresa_desejada": "ESS",
        "periodo_apuracao": "MENSAL",
        "nome_arquivo": "relatorio_compensacao.csv",
        "formato_data": "datahora",
    },

    # --- Exemplo de como adicionar o 2º relatório ---
    # Copie relatorios/_template.py para relatorios/nome_do_relatorio.py,
    # ajuste os seletores dentro dele, e adicione a entrada aqui:
    #
    # {
    #     "modulo": "nome_do_relatorio",
    #     "url": "https://indicadoresenergisaess.scl.corp/sgind/#/outrapagina",
    #     "empresa_desejada": "ESS",          # remova/ajuste se não se aplicar
    #     "periodo_apuracao": "MENSAL",       # remova/ajuste se não se aplicar
    #     "nome_arquivo": "relatorio_2.csv",
    #     "formato_data": "data",             # "data" (dd/mm/yyyy) ou "datahora" (dd/mm/yyyy hh:mm:ss)
    # },

    # ... repita para os relatórios 3 a 7 ...
]