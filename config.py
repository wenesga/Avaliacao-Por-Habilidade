"""Constantes e caminhos do sistema."""

import os


"""
As artes ficam no topo porque st.set_page_config() precisa do caminho da logo e deve ser a primeira
chamada st.* do script.

imagens/ guarda as artes do projeto e fonts/ as fontes. static/ é diferente: o Streamlit serve essa
pasta em app/static/ (enableStaticServing em .streamlit/config.toml) e o manifest e os ícones do PWA
dependem desse caminho, então ela não deve ser movida.
"""
ARQUIVO_LOGO = "static/logo.svg"                 # opcional: marca quadrada do projeto em vetor, um arquivo só para barra lateral, ícone da aba e ícone do app instalado (por isso fica em static/, que o manifest alcança por URL)


ARQUIVO_BANNER = "static/banner.jpg"            # opcional: arte pronta para o topo da Página Inicial (ideal 1200x400px ou 1500x500px, formato "capa" tipo Facebook/Twitter — pode já vir com a logo embutida, feita no Photoshop)


ARQUIVO_CABECALHO = "imagens/cabecalho.png"      # opcional: timbre institucional no topo de toda página do relatório em PDF. Tem que ser PNG (o fpdf2 não embute PDF); exportar com ~2008px de largura = 300 DPI nos 170mm da página. A altura é livre, o código lê a proporção do arquivo


"""
Pasta dos dados que mudam durante o uso (banco de alunos, conteúdos, configuração). Localmente é a
pasta do projeto; no Fly.io aponta para o volume persistente via TRILHA_DIR_DADOS=/data, pois só o
volume sobrevive a reinícios e publicações.
"""
DIR_DADOS = os.environ.get("TRILHA_DIR_DADOS", ".")
os.makedirs(DIR_DADOS, exist_ok=True)


ARQUIVO_ALUNOS = os.path.join(DIR_DADOS, "banco_alunos.json")             # formato antigo (só lido uma vez, pra migrar pro SQLite abaixo)


ARQUIVO_ALUNOS_DB = os.path.join(DIR_DADOS, "banco_alunos.db")            # progresso dos alunos (SQLite — suporta vários alunos salvando ao mesmo tempo sem corromper dados)


ARQUIVO_CONTEUDOS = os.path.join(DIR_DADOS, "conteudos.json")             # conteúdos cadastrados (nativos + criados pelo professor)


ARQUIVO_CONFIG = os.path.join(DIR_DADOS, "config_sistema.json")           # configurações gerais (senha do professor)


                                                 # ARQUIVO_LOGO, ARQUIVO_BANNER e ARQUIVO_CABECALHO ficam no topo, antes de st.set_page_config().

"""
Senha inicial do Painel do Professor. Pode ser trocada no próprio painel, em Configurações.
"""
SENHA_PADRAO_PROFESSOR = "computa258"


"""
Paleta de cores suaves para destacar os cartões de conteúdo do fundo, em tema claro e escuro (ver
CSS .cartao-cor-*). É usada em ciclo conforme novos conteúdos são cadastrados.
"""
PALETA_CORES_CARTAO = ["azul", "roxo", "rosa", "amarelo", "verde", "ciano"]


"""
A navegação tem um único eixo: 'pagina' indica onde o aluno está. 'conteudo_ativo' só tem
significado quando pagina == PAGINA_MATERIA, e 'aba_materia' só existe dentro de uma matéria. Isso
evita estados sem sentido (por exemplo, Início + uma matéria).
"""
PAGINA_INICIO = "inicio"


PAGINA_MATERIA = "materia"


PAGINA_PROFESSOR = "professor"


ABA_TEORIA = "📖 Orientações"


ABA_MISSOES = "🎮 Questões"


ABA_PROFESSOR_VISAO = "📊 Visão Geral"


ABA_PROFESSOR_CONTEUDOS = "➕ Gerenciar Conteúdos"


ABA_PROFESSOR_CONFIG = "⚙️ Configurações"


"""
A sessão do professor expira após esse tempo sem uso do painel (cada renderização do painel
autenticado renova o prazo). Professor e aluno compartilham a mesma sessão do navegador (computador
da sala), então um painel destravado esquecido expõe notas, exclusão de alunos e troca de senha.
"""
MINUTOS_SESSAO_PROFESSOR = 30


TAMANHO_MIN_APELIDO = 2


TAMANHO_MAX_APELIDO = 20


# Bimestres de 2026 da escola (nome, início, fim), em AAAA-MM-DD.
BIMESTRES = [
    ("1º bimestre", "2026-02-02", "2026-04-11"),
    ("2º bimestre", "2026-04-13", "2026-06-30"),
    ("3º bimestre", "2026-08-03", "2026-10-08"),
    ("4º bimestre", "2026-10-19", "2026-12-18"),
]
DISCIPLINAS = {"Matemática": "_M", "Português": "_P"}  # o fim do código do descritor diz a disciplina (D044_M = Matemática)
ARQUIVO_DESCRITORES_SAETO = "descritores_saeto.json"  # descritores SAETO/SAEB usados pela escola (ex.: D044_M)


"""
O XP de cada questão diminui a cada erro nela, mas nunca fica negativo nem chega a zero: o aluno
sempre ganha algo por terminar. Não há perda de XP ao errar, o que contradiria a proposta pedagógica
do sistema, que trata o erro como parte do processo.
"""
DESCONTO_XP_POR_ERRO = 0.20   # cada erro NESTA questão reduz 20% do XP dela


PISO_XP_FRACAO = 0.20         # nunca menos que 20% do valor configurado pelo professor


ESTILO_LINHA_TURMA = "background-color: #f1f3f5; color: #1f3a6e; font-weight: bold"
