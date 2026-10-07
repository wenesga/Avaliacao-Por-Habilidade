"""Constantes e caminhos do sistema."""

import os


# As artes ficam aqui em cima, e não junto dos outros ARQUIVO_* mais abaixo,
# porque st.set_page_config() precisa do caminho da logo e tem que ser a
# PRIMEIRA chamada st.* do script — não dá pra declarar depois. Antes o caminho
# estava repetido literalmente dentro do set_page_config; quando as imagens
# foram pra pasta imagens/, essa cópia esquecida faria o ícone da aba cair no
# fallback 🎓 silenciosamente, sem erro nenhum. Uma constante só evita isso.
#
# imagens/ é para as artes do projeto (como fonts/ é para as fontes). Não
# confundir com static/, que é funcional: o Streamlit serve aquela pasta em
# app/static/ (enableStaticServing no .streamlit/config.toml) e o manifest e os
# ícones do PWA dependem daquele caminho literal — não mover.
ARQUIVO_LOGO = "static/logo.svg"                 # opcional: marca quadrada do projeto em vetor, um arquivo só para barra lateral, ícone da aba e ícone do app instalado (por isso fica em static/, que o manifest alcança por URL)


ARQUIVO_BANNER = "static/banner.jpg"            # opcional: arte pronta para o topo da Página Inicial (ideal 1200x400px ou 1500x500px, formato "capa" tipo Facebook/Twitter — pode já vir com a logo embutida, feita no Photoshop)


ARQUIVO_CABECALHO = "imagens/cabecalho.png"      # opcional: timbre institucional no topo de toda página do relatório em PDF. Tem que ser PNG (o fpdf2 não embute PDF); exportar com ~2008px de largura = 300 DPI nos 170mm da página. A altura é livre, o código lê a proporção do arquivo


# Pasta dos dados que mudam durante o uso (banco de alunos, conteúdos, configuração).
# Localmente é a própria pasta do projeto. Na hospedagem (Fly.io) aponta para o
# volume de disco persistente, via variável TRILHA_DIR_DADOS=/data — só o volume
# sobrevive a reinícios; o resto do disco do servidor é refeito a cada publicação.
DIR_DADOS = os.environ.get("TRILHA_DIR_DADOS", ".")
os.makedirs(DIR_DADOS, exist_ok=True)


ARQUIVO_ALUNOS = os.path.join(DIR_DADOS, "banco_alunos.json")             # formato antigo (só lido uma vez, pra migrar pro SQLite abaixo)


ARQUIVO_ALUNOS_DB = os.path.join(DIR_DADOS, "banco_alunos.db")            # progresso dos alunos (SQLite — suporta vários alunos salvando ao mesmo tempo sem corromper dados)


ARQUIVO_CONTEUDOS = os.path.join(DIR_DADOS, "conteudos.json")             # conteúdos cadastrados (nativos + criados pelo professor)


ARQUIVO_CONFIG = os.path.join(DIR_DADOS, "config_sistema.json")           # configurações gerais (senha do professor)


                                                 # ARQUIVO_LOGO / ARQUIVO_BANNER / ARQUIVO_CABECALHO ficam lá no topo do
                                                 # arquivo, antes do st.set_page_config() — ver o comentário de lá.

# Senha inicial do Painel do Professor.
# O professor pode (e deve) trocá-la dentro do próprio painel, em "⚙️ Configurações".
SENHA_PADRAO_PROFESSOR = "computa258"


# Paleta de cores suaves pra destacar os cartões de "Conteúdos disponíveis" do
# fundo (funciona em tema claro e escuro — ver CSS ".cartao-cor-*" mais abaixo).
# Cicla nessa ordem conforme novos conteúdos são cadastrados.
PALETA_CORES_CARTAO = ["azul", "roxo", "rosa", "amarelo", "verde", "ciano"]


# A navegação tem UM eixo só: 'pagina' diz onde o aluno está.
# 'conteudo_ativo' só significa alguma coisa quando pagina == PAGINA_MATERIA, e
# 'aba_materia' só existe dentro de uma matéria. Antes eram dois eixos
# independentes ("qual página" x "qual matéria"), o que permitia estados sem
# sentido (Início + Frações) e fazia a Avaliação depender de uma escolha
# feita em outro canto da tela — o aluno clicava sem saber onde ia parar.
PAGINA_INICIO = "inicio"


PAGINA_MATERIA = "materia"


PAGINA_PROFESSOR = "professor"


ABA_TEORIA = "📖 Teoria"


ABA_MISSOES = "🎮 Questões"


ABA_PROFESSOR_VISAO = "📊 Visão Geral"


ABA_PROFESSOR_CONTEUDOS = "➕ Gerenciar Conteúdos"


ABA_PROFESSOR_CONFIG = "⚙️ Configurações"


# A sessão do professor expira sozinha depois desse tempo SEM uso do painel
# (cada renderização do painel autenticado renova o prazo). Motivo: professor e
# aluno dividem a mesma sessão do navegador — é o computador da sala de aula
# passando de mão em mão —, então um painel destravado esquecido aberto entrega
# notas da turma, exclusão de alunos e troca de senha pra quem sentar depois.
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


# Sem isso, um aluno que acerta de primeira e um que erra 20 vezes na mesma
# questão ganhavam o mesmo XP — o professor orientador apontou esse problema
# (2026-09-05). A correção NÃO pode ser "perder XP ao errar": além de zerar o
# aluno que erra metade das vezes (o próprio Wenes notou isso), contradiria a
# Justificativa do TCC, que trata o erro como parte do processo, não motivo de
# perda. A solução é o XP da questão diminuir com as tentativas, mas nunca ficar
# negativo nem chegar a zero — o aluno sempre ganha algo por terminar.
DESCONTO_XP_POR_ERRO = 0.20   # cada erro NESTA questão reduz 20% do XP dela


PISO_XP_FRACAO = 0.20         # nunca menos que 20% do valor configurado pelo professor


ESTILO_LINHA_TURMA = "background-color: #f1f3f5; color: #1f3a6e; font-weight: bold"
