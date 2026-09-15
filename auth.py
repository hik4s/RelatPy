import os
import json
import getpass

from dotenv import load_dotenv

load_dotenv()


class LoginError(Exception):
    """Levantada quando o login não é bem-sucedido (usuário/senha incorretos, etc.)."""


def obter_credenciais():
    """
    Se existir um .env com SITE_USUARIO e SITE_SENHA preenchidos, usa ele.
    Caso contrário (arquivo ausente ou variáveis faltando), pede as
    credenciais no console e já salva num .env novo, para que as
    próximas execuções não precisem pedir de novo.
    """
    usuario = os.environ.get("SITE_USUARIO")
    senha = os.environ.get("SITE_SENHA")

    if not os.path.exists(".env") or not usuario or not senha:
        print("Arquivo .env não encontrado (ou incompleto).")
        print("Informe as credenciais para esta e as próximas execuções:\n")

        usuario = input("Usuário: ").strip()
        senha = pedir_senha_confirmada()

        salvar_env(usuario, senha)

    return usuario, senha


def pedir_senha_confirmada():
    """
    Pede a senha duas vezes e só aceita quando as duas batem,
    evitando salvar uma senha errada no .env por erro de digitação.
    """
    while True:
        senha = getpass.getpass("Senha: ")
        confirmacao = getpass.getpass("Confirme a senha: ")

        if senha == confirmacao:
            return senha

        print("As senhas não coincidem. Tente novamente.\n")


def salvar_env(usuario, senha):
    """
    Cria/sobrescreve o .env na pasta do projeto com as credenciais
    informadas, para que fazer_login não precise pedir de novo
    nas próximas execuções.
    """
    # Aspas em volta do valor evitam problema se usuario/senha tiver
    # espaço; escapamos aspas internas para não quebrar o arquivo.
    usuario_escapado = usuario.replace('"', '\\"')
    senha_escapada = senha.replace('"', '\\"')

    with open(".env", "w", encoding="utf-8") as arquivo:
        arquivo.write(f'SITE_USUARIO="{usuario_escapado}"\n')
        arquivo.write(f'SITE_SENHA="{senha_escapada}"\n')

    print("\n[OK] Credenciais salvas em .env — não vai precisar logar de novo.\n")


async def fazer_login(context, usuario, senha):
    """
    Faz login uma única vez no contexto compartilhado.

    Cookies já são compartilhados automaticamente entre abas do mesmo
    context. Mas esse site guarda o token de autenticação no
    sessionStorage, que é isolado POR ABA mesmo dentro do mesmo
    context/navegador — por isso cada aba nova pedia login de novo.

    A solução: capturamos o sessionStorage logo após o login e
    registramos um init script no context. Esse script roda ANTES
    de qualquer script da própria aplicação em toda aba nova/nova
    navegação, repondo o sessionStorage antes do app checar se
    está autenticado.
    """
    page = await context.new_page()

    await page.goto(
        "https://indicadoresenergisaess.scl.corp/sgind/#/login"
    )

    await page.fill(
        '[name="cre_username"]',
        usuario
    )

    await page.fill(
        '[name="cre_password"]',
        senha
    )

    await page.get_by_role(
        "button",
        name="Logar"
    ).click()

    await page.wait_for_timeout(5000)

    print("URL após login:", page.url)

    # Se ainda estivermos na página de login, o usuário/senha estava errado
    # (ou algum outro problema impediu o login de completar).
    if "login" in page.url.lower():
        await page.close()
        raise LoginError(
            "Login não foi concluído — usuário ou senha incorretos "
            "(ou o site não respondeu como esperado)."
        )

    # Captura tudo que está no sessionStorage dessa aba já autenticada.
    estado_sessao = await page.evaluate("() => JSON.stringify(sessionStorage)")

    # json.dumps aqui serve só para escapar corretamente a string ao
    # embutir dentro do texto do script JS (evita quebrar por causa
    # de aspas/caracteres especiais no token).
    estado_sessao_js = json.dumps(estado_sessao)

    await context.add_init_script(f"""
        (() => {{
            try {{
                const dados = JSON.parse({estado_sessao_js});
                for (const chave in dados) {{
                    window.sessionStorage.setItem(chave, dados[chave]);
                }}
            }} catch (e) {{
                console.error("Falha ao restaurar sessionStorage:", e);
            }}
        }})();
    """)

    # Fecha essa aba de login; as próximas abas abertas no context já
    # nascem com o sessionStorage restaurado pelo init script acima.
    await page.close()


async def tentar_login(context, max_tentativas=3):
    """
    Obtém as credenciais e tenta logar, repetindo o processo se falhar.

    Se o login der errado (ex: .env com senha desatualizada), apaga o
    .env e força o console a pedir as credenciais de novo na próxima
    tentativa — evita ficar preso repetindo a mesma senha errada
    indefinidamente.
    """
    for tentativa in range(1, max_tentativas + 1):
        usuario, senha = obter_credenciais()

        try:
            await fazer_login(context, usuario, senha)
            return

        except LoginError as erro:
            print(f"\n[ERRO] {erro}")

            if os.path.exists(".env"):
                os.remove(".env")
                print(
                    "[INFO] .env removido, pois as credenciais salvas "
                    "não funcionaram.\n"
                )

            if tentativa == max_tentativas:
                raise LoginError(
                    f"Login falhou após {max_tentativas} tentativas."
                ) from erro

            print(f"Tentativa {tentativa} de {max_tentativas} falhou. Tentando de novo...\n")