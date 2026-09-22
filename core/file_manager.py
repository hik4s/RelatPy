import os
import shutil
from datetime import datetime


# =====================================================
# PASTAS DA REDE
# =====================================================

PASTAS_SERVIDOR = {

    "compensacao":
    r"\\fs-ess.scl.corp\dados$\DEOP\DEOP-CPQE\00_PÓS OPERAÇÃO\01_BOLETIM_DIÁRIO\BI_IQOS_SGIND\COMPENSACAO DETALHAMENTO",

    "reclamacao":
    r"\\fs-ess.scl.corp\dados$\DEOP\DEOP-CPQE\00_PÓS OPERAÇÃO\01_BOLETIM_DIÁRIO\BI_IQOS_SGIND\RECLAMACOES",

    "interrupcoes_cliente":
    r"\\fs-ess.scl.corp\dados$\DEOP\DEOP-CPQE\00_PÓS OPERAÇÃO\01_BOLETIM_DIÁRIO\BI_IQOS_SGIND\INTERRUPÇÕES POR CLIENTE",

    "interrupcoes_evento":
    r"\\fs-ess.scl.corp\dados$\DEOP\DEOP-CPQE\00_PÓS OPERAÇÃO\01_BOLETIM_DIÁRIO\BI_IQOS_SGIND\EVENTOS",

    "todas_ocorrencias":
    r"\\fs-ess.scl.corp\dados$\DEOP\DEOP-CPQE\00_PÓS OPERAÇÃO\01_BOLETIM_DIÁRIO\BI_IQOS_SGIND\OCORRENCIAS",

    "dia_critico":
    r"\\fs-ess.scl.corp\dados$\DEOP\DEOP-CPQE\00_PÓS OPERAÇÃO\01_BOLETIM_DIÁRIO\BI_IQOS_SGIND\DIA CRITICO",

    "iqos_resultados":
    r"\\fs-ess.scl.corp\dados$\DEOP\DEOP-CPQE\00_PÓS OPERAÇÃO\01_BOLETIM_DIÁRIO\BI_IQOS_SGIND\Atendimentos Emergencial - TMA\IQOS - TMA"
}


# =====================================================
# NOMES DOS MESES
# =====================================================

MESES = {

    1: "Janeiro",
    2: "Fevereiro",
    3: "Marco",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro"
}


# =====================================================
# NOMES DOS ARQUIVOS
# =====================================================

def gerar_nome_final(
    modulo,
    periodo_inicio
):

    data = datetime.strptime(
        periodo_inicio,
        "%d/%m/%Y %H:%M:%S"
    )

    prefixo = data.strftime(
        "%m_%Y"
    )

    nomes = {

        "compensacao":
        f"{prefixo}_eventos_compensacao_detalhamento.csv",

        "dia_critico":
        f"{prefixo}_dia_critico.csv",

        "interrupcoes_evento":
        f"{prefixo}_eventos.csv",

        "reclamacao":
        f"{prefixo}_reclamacoes.csv",

        "todas_ocorrencias":
        f"{prefixo}_ocorrencias.csv",

        "interrupcoes_cliente":
        f"{prefixo}_interrupcoes_por_cliente.csv"
    }

    if modulo == "iqos_resultados":

        nome_mes = MESES[
            data.month
        ]

        return (
            f"{prefixo}_eventos_"
            f"{nome_mes}_cheio.csv"
        )

    return nomes.get(
        modulo
    )


# =====================================================
# DESTINO FINAL DA REDE
# =====================================================

def obter_destino_rede(
    modulo
):

    return PASTAS_SERVIDOR.get(
        modulo
    )


def gerar_caminho_final_rede(
    modulo,
    periodo_inicio
):

    pasta = obter_destino_rede(
        modulo
    )

    if not pasta:

        return None

    nome = gerar_nome_final(
        modulo,
        periodo_inicio
    )

    return os.path.join(
        pasta,
        nome
    )


# =====================================================
# LOCALIZAR ARQUIVO
# =====================================================

def localizar_arquivo(
    nome_arquivo,
    pasta_base="downloads"
):

    for raiz, _, arquivos in os.walk(
        pasta_base
    ):

        if nome_arquivo in arquivos:

            return os.path.join(
                raiz,
                nome_arquivo
            )

    return None


# =====================================================
# RENOMEAR
# =====================================================

def renomear_arquivo(
    origem,
    novo_nome
):

    pasta = os.path.dirname(
        origem
    )

    destino = os.path.join(
        pasta,
        novo_nome
    )

    os.rename(
        origem,
        destino
    )

    return destino


# =====================================================
# COPIAR PARA SERVIDOR
# =====================================================

def copiar_relatorio_para_servidor(
    modulo,
    caminho_arquivo,
    periodo_inicio
):

    pasta_destino = obter_destino_rede(
        modulo
    )

    if not pasta_destino:

        raise ValueError(
            f"Destino não configurado para: {modulo}"
        )

    if not os.path.exists(
        pasta_destino
    ):

        raise FileNotFoundError(
            f"Pasta não encontrada: {pasta_destino}"
        )

    nome_final = gerar_nome_final(
        modulo,
        periodo_inicio
    )

    destino = os.path.join(
        pasta_destino,
        nome_final
    )

    shutil.copy2(
        caminho_arquivo,
        destino
    )

    print(
        f"[OK] Arquivo enviado para rede: {destino}"
    )

    return destino


# =====================================================
# VALIDAÇÃO DE ARQUIVO NA REDE
# =====================================================

def arquivo_existe_no_servidor(
    modulo,
    periodo_inicio
):

    pasta_destino = obter_destino_rede(
        modulo
    )

    if not pasta_destino:

        return False

    if not os.path.exists(
        pasta_destino
    ):

        return False

    nome_arquivo = gerar_nome_final(
        modulo,
        periodo_inicio
    )

    caminho = os.path.join(
        pasta_destino,
        nome_arquivo
    )

    return os.path.exists(
        caminho
    )


# =====================================================
# TESTE
# =====================================================

if __name__ == "__main__":

    periodo = "01/09/2026 00:00:00"

    for modulo in [

        "compensacao",
        "reclamacao",
        "interrupcoes_cliente",
        "interrupcoes_evento",
        "todas_ocorrencias",
        "dia_critico",
        "iqos_resultados"
    ]:

        print(
            modulo,
            "->",
            gerar_nome_final(
                modulo,
                periodo
            )
        )