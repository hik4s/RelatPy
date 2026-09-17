import asyncio
import json
import os
from datetime import datetime

STATUS = {}

MAX_PARALELO = 3

SEMAFORO = asyncio.Semaphore(
    MAX_PARALELO
)


def salvar_status():
    """
    Persiste o status da execução.
    Usado futuramente pelo Streamlit.
    """

    os.makedirs(
        "status",
        exist_ok=True
    )

    with open(
        "status/status.json",
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            STATUS,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


def atualizar_status(
    modulo,
    status,
    detalhe=None
):
    """
    Atualiza o status global.
    """

    STATUS[modulo] = {
        "status": status,
        "detalhe": detalhe,
        "ultima_atualizacao":
            datetime.now().strftime(
                "%d/%m/%Y %H:%M:%S"
            )
    }

    salvar_status()


async def executar_relatorio(
    corrotina,
    modulo
):
    """
    Executa um relatório com controle
    de paralelismo e rastreabilidade.
    """

    async with SEMAFORO:

        atualizar_status(
            modulo,
            "EXECUTANDO"
        )

        try:

            resultado = await corrotina

            atualizar_status(
                modulo,
                "CONCLUIDO"
            )

            return resultado

        except Exception as erro:

            atualizar_status(
                modulo,
                "ERRO",
                str(erro)
            )

            raise


async def executar_lote(
    tarefas
):
    """
    Executa múltiplos relatórios
    respeitando o semáforo.
    """

    return await asyncio.gather(
        *tarefas,
        return_exceptions=True
    )


def inicializar_status(
    relatorios
):
    """
    Cria o status inicial.
    """

    STATUS.clear()

    for item in relatorios:

        STATUS[
            item["modulo"]
        ] = {
            "status": "PENDENTE",
            "detalhe": None,
            "ultima_atualizacao": None
        }

    salvar_status()