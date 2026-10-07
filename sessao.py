"""Estado da sessão, login do aluno e do professor, mensagens rápidas."""

import streamlit as st
import time
from banco import carregar_perfil_aluno
from config import ABA_PROFESSOR_VISAO, ABA_TEORIA, MINUTOS_SESSAO_PROFESSOR, PAGINA_INICIO, PAGINA_MATERIA, PAGINA_PROFESSOR, TAMANHO_MAX_APELIDO, TAMANHO_MIN_APELIDO
from configuracao import carregar_config
from conteudos import carregar_conteudos


def inicializar_estado():
    if 'conteudos' not in st.session_state: st.session_state.conteudos = carregar_conteudos()
    if 'config' not in st.session_state: st.session_state.config = carregar_config()
    if 'aluno_ativo' not in st.session_state: st.session_state.aluno_ativo = ""
    if 'conteudo_ativo' not in st.session_state: st.session_state.conteudo_ativo = ""
    # Guardamos o INSTANTE EM QUE A SESSÃO EXPIRA, não um booleano "está logado":
    # com o booleano, ficar autenticado era um estado sem prazo nenhum, que só
    # terminava se alguém lembrasse de clicar em "Sair do Painel". 0.0 = sem sessão.
    if 'professor_auth_expira_em' not in st.session_state: st.session_state.professor_auth_expira_em = 0.0
    if 'pagina' not in st.session_state: st.session_state.pagina = PAGINA_INICIO
    if 'aba_materia' not in st.session_state: st.session_state.aba_materia = ABA_TEORIA
    if 'aba_professor' not in st.session_state: st.session_state.aba_professor = ABA_PROFESSOR_VISAO
    if 'novas_secoes_teoria' not in st.session_state: st.session_state.novas_secoes_teoria = []
    if 'novas_missoes' not in st.session_state: st.session_state.novas_missoes = []


def sessao_professor_ativa():
    return time.time() < st.session_state.professor_auth_expira_em


def abrir_sessao_professor():
    """Também usada pra RENOVAR o prazo enquanto o professor está usando o
    painel — assim o tempo conta a partir do último uso, e a sessão não morre
    no meio de um cadastro longo de conteúdo."""
    st.session_state.professor_auth_expira_em = time.time() + MINUTOS_SESSAO_PROFESSOR * 60


def encerrar_sessao_professor():
    st.session_state.professor_auth_expira_em = 0.0


def apelido_invalido(apelido):
    """Retorna a mensagem de erro do apelido, ou "" se estiver válido.

    Regra: UMA palavra só, apenas letras e números. str.isalnum() já entrega
    exatamente isso e ainda aceita acento ("João" é alfanumérico em Python),
    o que importa em português — por isso não usamos regex aqui.

    O apelido é a chave primária do aluno no banco: é por ele que o progresso é
    encontrado no login seguinte. Espaço no meio faz o aluno digitar "Ana Paula"
    hoje e "AnaPaula" amanhã, virando dois perfis e perdendo o XP. O limite de
    caracteres também protege a coluna 'Login' do relatório em PDF, que tem
    38mm — acima disso o texto seria cortado com reticências."""
    if len(apelido) < TAMANHO_MIN_APELIDO:
        return f"Use pelo menos {TAMANHO_MIN_APELIDO} caracteres."
    if len(apelido) > TAMANHO_MAX_APELIDO:
        return f"Use no máximo {TAMANHO_MAX_APELIDO} caracteres."
    if not apelido.isalnum():
        return "Só letras e números, sem espaços."
    return ""


def entrar_como_aluno(nome):
    """Entrar como aluno ENCERRA a sessão do professor. Os dois papéis dividem a
    mesma sessão do navegador (é a mesma aba, no computador da sala), então sem
    isso o aluno herda o painel já destravado — notas da turma inteira, excluir
    aluno, apagar o banco e trocar a senha do professor — sem nunca ter digitado
    senha nenhuma. Também sai da página do professor, porque continuar nela
    depois de perder o acesso só mostraria a tela de senha do nada."""
    carregar_perfil_aluno(nome)
    encerrar_sessao_professor()
    if st.session_state.pagina == PAGINA_PROFESSOR:
        st.session_state.pagina = PAGINA_INICIO
    st.rerun()


def ir_para_materia(cid, aba=ABA_TEORIA):
    """Caminho ÚNICO para abrir uma matéria — usado pelo menu lateral e pelos
    cartões da página inicial e do hub de Estatística. Ter uma função só é o
    que impede a divergência de antes, quando cada ponto de entrada montava
    sua própria combinação de 'trocar matéria' + 'trocar de página' e cada um
    parava num lugar diferente."""
    st.session_state.pagina = PAGINA_MATERIA
    st.session_state.conteudo_ativo = cid
    st.session_state.aba_materia = aba
    st.rerun()


def flash(mensagem):
    """Guarda uma mensagem de sucesso pra mostrar DEPOIS do st.rerun(), num
    pop-up fixo no canto superior direito (ver renderizar_flash_pendente,
    chamado uma vez só no roteamento principal — não precisa de "onde"
    mostrar, por isso, ao contrário de renderizar_ultimo_resultado, não
    recebe posição nenhuma)."""
    st.session_state["_flash_pendente"] = mensagem


def renderizar_flash_pendente():
    """Mostra (e consome) a mensagem guardada por flash(), se tiver alguma,
    como um card fixo no canto superior direito — não precisa rolar a tela
    pra ver, ao contrário de um st.success() desenhado no meio do formulário
    (bug relatado pelo Wenes, 2026-09-17: editou um conteúdo longo, salvou, e
    a mensagem ficou fora da tela, lá em cima). st.toast() faria a mesma
    coisa nativamente, mas parou de funcionar neste ambiente."""
    mensagem = st.session_state.pop("_flash_pendente", None)
    if mensagem:
        st.markdown(
            f'<div class="flash-toast">✅ {mensagem}</div>',
            unsafe_allow_html=True,
        )
