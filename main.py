import asyncio
from datetime import datetime

from auth import obter_credenciais
from downloader import baixar_todos_os_relatorios


def pedir_data_hora(mensagem):
    while True:
        texto = input(mensagem).strip()
        try:
            datetime.strptime(texto, "%d/%m/%Y %H:%M:%S")
            return texto
        except ValueError:
            print("Formato inválido! Use dd/mm/yyyy hh:mm:ss")


def capturar_periodo():
    print("=== Período para extração dos relatórios ===")

    while True:
        inicio = pedir_data_hora("Data/hora INÍCIO (dd/mm/yyyy hh:mm:ss): ")
        fim = pedir_data_hora("Data/hora FIM    (dd/mm/yyyy hh:mm:ss): ")

        dt_inicio = datetime.strptime(inicio, "%d/%m/%Y %H:%M:%S")
        dt_fim = datetime.strptime(fim, "%d/%m/%Y %H:%M:%S")

        if dt_inicio > dt_fim:
            print("A data inicial não pode ser maior que a final.\n")
            continue

        return inicio, fim


def main():
    usuario, senha = obter_credenciais()

    periodo_inicio, periodo_fim = capturar_periodo()

    print("\nIniciando download dos relatórios (em paralelo)...\n")

    asyncio.run(
        baixar_todos_os_relatorios(usuario, senha, periodo_inicio, periodo_fim)
    )

    print("\nProcesso concluído.")


if __name__ == "__main__":
    main()