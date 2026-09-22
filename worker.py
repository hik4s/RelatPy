import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

from main import executar_relatorios


FORMATO_PERIODO = "%d/%m/%Y %H:%M:%S"

RAIZ = Path(__file__).resolve().parent

CAMINHO_PID = (
    RAIZ
    / "status"
    / "worker.pid"
)


def validar_periodo(
    periodo_inicio,
    periodo_fim
):

    inicio = datetime.strptime(
        periodo_inicio,
        FORMATO_PERIODO
    )

    fim = datetime.strptime(
        periodo_fim,
        FORMATO_PERIODO
    )

    if inicio > fim:

        raise ValueError(
            "A data inicial não pode ser maior "
            "que a data final."
        )


def remover_pid():

    if not CAMINHO_PID.exists():

        return

    try:

        pid_registrado = int(
            CAMINHO_PID.read_text(
                encoding="utf-8"
            ).strip()
        )

        if pid_registrado == os.getpid():

            CAMINHO_PID.unlink(
                missing_ok=True
            )

    except (
        OSError,
        ValueError
    ):

        pass


def main():

    print(
        "[WORKER] Processo iniciado.",
        flush=True
    )

    if len(sys.argv) != 3:

        raise ValueError(
            "Uso esperado: worker.py "
            "\"dd/mm/aaaa hh:mm:ss\" "
            "\"dd/mm/aaaa hh:mm:ss\""
        )

    periodo_inicio = sys.argv[1]

    periodo_fim = sys.argv[2]

    print(
        "[WORKER] Período selecionado: "
        f"{periodo_inicio} até {periodo_fim}",
        flush=True
    )

    validar_periodo(
        periodo_inicio,
        periodo_fim
    )

    print(
        "[WORKER] Período validado.",
        flush=True
    )

    executar_relatorios(
        periodo_inicio,
        periodo_fim
    )

    print(
        "[WORKER] Execução concluída.",
        flush=True
    )


if __name__ == "__main__":

    try:

        main()

    except Exception:

        traceback.print_exc()

        sys.exit(1)

    finally:

        remover_pid()