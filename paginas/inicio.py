"""Página Inicial."""

import os
import streamlit as st
from banco import perfil_atual, ranking_turma
from config import ARQUIVO_BANNER, PALETA_CORES_CARTAO
from estilo import obter_logo_base64
from sessao import ir_para_materia


# 6. PÁGINA INICIAL (BANNER + ATALHOS)
@st.fragment(run_every="5s")
def render_placar_turma():
    """Placar da turma, no estilo Kahoot: apelido + XP, atualizando sozinho.

    O @st.fragment(run_every="5s") faz SÓ este bloco recarregar de 5 em 5
    segundos, sem repintar a página nem interromper o aluno que está no meio de
    uma questão. Não é push — o Streamlit não avisa as outras sessões; é o
    navegador de cada aluno consultando o banco. Com uma turma pequena e a
    consulta enxuta de ranking_turma(), a carga é desprezível.

    Mostrar o desempenho em público só é aceitável porque o aluno entra com
    apelido: o objetivo não é
    anonimato, é não expor o nome de quem está atrás. Quem quiser se revelar,
    se revela — e isso vira parte da brincadeira."""
    placar = ranking_turma()
    if not placar:
        return

    eu = st.session_state.aluno_ativo
    medalhas = {1: "🥇", 2: "🥈", 3: "🥉"}
    linhas_html = []
    for posicao, (apelido, xp) in enumerate(placar, start=1):
        destaque = " eu" if apelido == eu else ""
        marcador = medalhas.get(posicao, f"{posicao}º")
        linhas_html.append(
            f'<div class="placar-linha{destaque}">'
            f'<span class="placar-pos">{marcador}</span>'
            f'<span class="placar-nome">{apelido}</span>'
            f'<span class="placar-xp">{xp} XP</span>'
            f"</div>"
        )
    st.markdown(
        f'<div class="placar-caixa">{"".join(linhas_html)}</div>',
        unsafe_allow_html=True,
    )
    if not eu:
        st.caption("Entre com um apelido na barra lateral para aparecer no placar.")


def renderizar_grade_cartoes(cartoes, prefixo_key):
    """Grade de cartões (ícone, título, descrição, botão "Acessar →"), 3 por
    linha. cartoes é uma lista de dicts {icone, titulo, descricao, on_click,
    progresso} — on_click é uma função SEM argumento, chamada ao clicar no
    botão (varia: pode abrir uma matéria direto, ou abrir o hub de
    Estatística). "progresso" é opcional: uma string tipo "3/8" ou "✓" pra
    mostrar quantas questões DAQUELE card específico já foram concluídas.
    Necessário porque o "8/44" do menu lateral soma os 6
    sub-temas de Estatística juntos e não dá pra saber, olhando só ali, quanto
    cada um já rendeu individualmente.

    Usada tanto pelos "Conteúdos disponíveis" da Início quanto pelos 6
    sub-temas do hub de Estatística — prefixo_key garante keys únicas nos
    widgets mesmo quando a mesma matéria aparece nas duas telas."""
    for inicio_linha in range(0, len(cartoes), 3):
        colunas = st.columns(3)
        for i, cartao in enumerate(cartoes[inicio_linha:inicio_linha + 3]):
            idx_global = inicio_linha + i
            cor = PALETA_CORES_CARTAO[idx_global % len(PALETA_CORES_CARTAO)]
            with colunas[i]:
                with st.container(border=True, key=f"{prefixo_key}_cartao_{idx_global}_cor_{cor}"):
                    # Progresso na MESMA linha do título, texto simples (sem badge colorido) — mesmo padrão já usado no menu lateral ("📊 Estatística · 1/44"). Uma versão anterior usava um badge numa linha própria, mas isso deixava o card mais alto que o necessário só por causa de uma informação curta.
                    titulo_linha = f"#### {cartao['icone']} {cartao['titulo']}"
                    if cartao.get("progresso"):
                        titulo_linha += f"  ·  {cartao['progresso']}"
                    st.markdown(titulo_linha)
                    st.caption(cartao.get("descricao", ""))
                    if st.button("Acessar →", key=f"{prefixo_key}_btn_{idx_global}", use_container_width=True):
                        cartao["on_click"]()


def render_pagina_inicial():
    aluno = st.session_state.aluno_ativo

    if aluno:
        perfil = perfil_atual()
        saudacao = f"Bem-vindo(a) de volta, {aluno}! 🏆 Você já tem {perfil['xp_total']} XP acumulados."
    else:
        saudacao = "Escolha um apelido na barra lateral para começar a acumular XP e salvar seu progresso."

    logo_b64 = obter_logo_base64()
    if logo_b64:
        logo_html = f'<img class="home-banner-logo-img" src="data:image/svg+xml;base64,{logo_b64}" alt="Logo" />'
    else:
        logo_html = '<div class="home-banner-logo">🎓</div>'

    if os.path.exists(ARQUIVO_BANNER):
        # Arte pronta (static/banner.jpg, com a metade esquerda livre) como fundo; o título vai por cima em HTML.
        st.markdown(
            f'''
            <div class="home-banner-arte" style="background-image: url('app/{ARQUIVO_BANNER}')">
                <p class="home-banner-arte-titulo">Avaliação por Habilidade</p>
                <p class="home-banner-arte-subtitulo">Veja, por habilidade, onde cada aluno acertou e onde precisa de reforço.</p>
            </div>
            ''',
            unsafe_allow_html=True,
        )
        st.markdown(f"##### {saudacao}")
    else:
        st.markdown(f"""
        <div class="home-banner">
            {logo_html}
            <p class="home-banner-titulo">Avaliação por Habilidade</p>
            <p class="home-banner-subtitulo">
                Uma plataforma interativa para estudar Matemática e Português e mostrar à escola
                em quais habilidades cada aluno precisa de reforço.
                {saudacao}
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Dentro de um expander, FECHADO por padrão — quem tem curiosidade clica e vê, quem não tem, nem repara que existe. Cada navegador é uma sessão isolada do Streamlit: o professor abrir ou fechar no notebook projetado no data show não afeta o que aparece no celular de nenhum aluno. Também ajuda com turma grande, onde a lista ficaria comprida antes do resto da página.
    with st.expander("🏆 Placar da Turma", expanded=False):
        render_placar_turma()
    st.write("")

    st.markdown("### 🧭 Como funciona")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="home-step-card">
            <div class="home-step-numero">Passo 1</div>
            <div class="home-step-titulo">📚 Escolha uma matéria</div>
            <div class="home-step-texto">Clique em uma das matérias na barra lateral (ou nos cartões abaixo) para abrir a disciplina que quer estudar.</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="home-step-card">
            <div class="home-step-numero">Passo 2</div>
            <div class="home-step-titulo">📖 Leia as orientações</div>
            <div class="home-step-texto">Veja as orientações antes de responder as questões.</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="home-step-card">
            <div class="home-step-numero">Passo 3</div>
            <div class="home-step-titulo">🎮 Jogue as Questões</div>
            <div class="home-step-texto">Na própria matéria, troque para a aba Questões: responda os desafios, ganhe XP e acompanhe seu progresso.</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.markdown("### 📚 Disciplinas")
    st.caption("Clique para ir direto ao conteúdo.")

    cartoes = [
        {
            "icone": info["icone"], "titulo": info["titulo"], "descricao": info.get("descricao", ""),
            "on_click": (lambda cid=cid: ir_para_materia(cid)),
        }
        for cid, info in st.session_state.conteudos.items()
    ]
    renderizar_grade_cartoes(cartoes, prefixo_key="home")

    if not aluno:
        st.info("💡 Dica: professores encontram o cadastro de novos conteúdos e as senhas em **🛡️ Painel do Professor**, na barra lateral.")
