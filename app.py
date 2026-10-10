import os
import sys
import subprocess

# Ancora o diretório de trabalho na pasta deste arquivo. Sem isso, os caminhos relativos (logo, banner, bancos) só funcionam se quem rodar o script já estiver "dentro" desta pasta no terminal.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

from config import ARQUIVO_LOGO, PAGINA_INICIO, PAGINA_MATERIA, PAGINA_PROFESSOR

# st.set_page_config() precisa ser a PRIMEIRA chamada st.* do script.
st.set_page_config(
    page_title="Avaliação por Habilidade",
    page_icon=ARQUIVO_LOGO if os.path.exists(ARQUIVO_LOGO) else "🎓",
    layout="wide"
)

from banco import inicializar_banco_db, migrar_json_para_sqlite_se_necessario, registrar_acesso_se_novo
from estilo import aplicar_estilo
from injecoes import aplicar_injecoes
from paginas.inicio import render_pagina_inicial
from paginas.materia import render_pagina_materia
from paginas.menu import render_menu_lateral
from paginas.professor import render_pagina_professor
from sessao import inicializar_estado, renderizar_flash_pendente

aplicar_injecoes()
inicializar_banco_db()
migrar_json_para_sqlite_se_necessario()
registrar_acesso_se_novo()
inicializar_estado()
aplicar_estilo()

with st.sidebar:
    render_menu_lateral()

renderizar_flash_pendente()

pagina = st.session_state.pagina
if pagina == PAGINA_INICIO:
    render_pagina_inicial()
elif pagina == PAGINA_MATERIA:
    render_pagina_materia()
elif pagina == PAGINA_PROFESSOR:
    render_pagina_professor()

# Rodar com "python app.py" abre o Streamlit sozinho.
if __name__ == '__main__':
    if not os.environ.get("RODANDO_STREAMLIT"):
        os.environ["RODANDO_STREAMLIT"] = "1"
        subprocess.run([sys.executable, "-m", "streamlit", "run", __file__])
