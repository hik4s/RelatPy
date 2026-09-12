import os
import json

from dotenv import load_dotenv

load_dotenv()


async def fazer_login(context):
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
        os.environ["SITE_USUARIO"]
    )

    await page.fill(
        '[name="cre_password"]',
        os.environ["SITE_SENHA"]
    )

    await page.get_by_role(
        "button",
        name="Logar"
    ).click()

    await page.wait_for_timeout(5000)

    print("URL após login:", page.url)

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