"""Página de uma disciplina (orientações e questões)."""

import streamlit as st
from banco import perfil_atual, progresso_atual
from config import ABA_MISSOES, ABA_TEORIA, PAGINA_INICIO
from conteudos import obter_total_missoes
from missoes import render_missoes_dinamicas, renderizar_ultimo_resultado


def render_pagina_conteudo_dinamico(conteudo):
    # Título desenhado pelo roteador (bloco 10), junto com os botões Teoria/Questões.
    if conteudo.get("descricao"):
        st.markdown(f"*{conteudo['descricao']}*")
    st.write("---")

    secoes = conteudo.get("teoria", [])
    if not secoes:
        st.info("📭 Esta disciplina ainda não possui orientações cadastradas. Peça ao professor para adicioná-las no Painel do Professor.")
        return

    # st.expander de verdade (o mesmo componente do conteúdo estático, não uma
    # imitação) com expanded=True — já abre mostrando o conteúdo, mas o aluno
    # pode recolher se quiser limpar a tela.
    for i, secao in enumerate(secoes, start=1):
        with st.expander(f"{i}️⃣ {secao.get('titulo', '')}", expanded=True):
            st.markdown(secao.get("texto", ""))
        st.write("")


def render_pagina_materia():
    # Se o professor excluiu a matéria que estava aberta, volta pro Início
    # em vez de estourar KeyError.
    if st.session_state.conteudo_ativo not in st.session_state.conteudos:
        st.session_state.pagina = PAGINA_INICIO
        st.rerun()
    cid = st.session_state.conteudo_ativo
    conteudo = st.session_state.conteudos[cid]

    # Botão "← Voltar" em TODA matéria — sem ele, quem chegou aqui clicando
    # num cartão da Início ou no hub de Estatística só tem como sair clicando
    # de novo no menu lateral, o que nem todo aluno pensa em fazer sozinho. O
    # botão Voltar do navegador não ajuda aqui (é uma SPA, não existe "página
    # anterior" de verdade pro navegador voltar). Rótulo só "Voltar", sem
    # dizer pra onde — não precisa, é óbvio pelo lugar. Os 6 sub-temas de
    # Estatística voltam pro hub (é de lá que vieram); as demais matérias
    # (cadastradas pelo professor) voltam direto pra Início, que é o único
    # lugar de onde elas são abertas.
    if st.button("← Voltar", key="voltar_materia"):
        st.session_state.pagina = PAGINA_INICIO
        st.rerun()

    st.title(f"{conteudo['icone']} {conteudo['titulo']}")

    # Teoria x Questões é uma troca DENTRO da matéria (e a de maior frequência no
    # app: o aluno lê a fórmula, tenta a questão, volta na fórmula), por isso fica
    # colada no conteúdo e não no menu lateral. Dois botões em vez de
    # st.segmented_control de propósito: o segmented_control desmarca a opção
    # quando você clica nela de novo (vira None), e aqui não existe "nenhuma
    # seção selecionada". Botões também mantêm a mesma linguagem visual do menu
    # lateral (ativo = type="primary").
    col_teoria, col_missoes, _ = st.columns([1, 1, 3])
    with col_teoria:
        if st.button(ABA_TEORIA, use_container_width=True, key="aba_btn_teoria",
                     type="primary" if st.session_state.aba_materia == ABA_TEORIA else "secondary"):
            st.session_state.aba_materia = ABA_TEORIA
            st.rerun()
    with col_missoes:
        rotulo_missoes = ABA_MISSOES
        total_missoes = obter_total_missoes(cid)
        if st.session_state.aluno_ativo and total_missoes:
            feitas = min(max(progresso_atual(cid)["missao_atual"] - 1, 0), total_missoes)
            rotulo_missoes += f"  {feitas}/{total_missoes}"
        if st.button(rotulo_missoes, use_container_width=True, key="aba_btn_missoes",
                     type="primary" if st.session_state.aba_materia == ABA_MISSOES else "secondary"):
            st.session_state.aba_materia = ABA_MISSOES
            st.rerun()

    st.markdown("")

    if st.session_state.aba_materia == ABA_MISSOES:
        if not st.session_state.aluno_ativo:
            st.warning("⚠️ Olá! Escolha um apelido na barra lateral à esquerda para carregar o seu perfil e começar a ganhar XP.")
        else:
            # Selo de XP em destaque no topo da Avaliação — um lugar só,
            # vale tanto pro conteúdo nativo de Estatística quanto pros
            # cadastrados pelo professor, sem duplicar em cada função de questão.
            xp_atual = perfil_atual()["xp_total"]
            st.markdown(
                f'<div class="xp-destaque-missoes">'
                f'<span class="icone">🏆</span><span class="valor">{xp_atual} XP</span>'
                f"</div>",
                unsafe_allow_html=True,
            )
            render_missoes_dinamicas(conteudo)
            # Embaixo, não em cima: é onde o olhar do aluno já está depois de
            # clicar em "Verificar Resposta" (mesma posição do "❌ Resposta
            # incorreta", que fica logo abaixo do botão). Uma versão anterior
            # mostrava isso no topo, junto do selo de XP — só visível rolando
            # a tela pra cima, o que o Wenes apontou (2026-09-14) que recriava
            # o mesmo problema de antes (informação fora de vista), só que
            # em vez de sumir rápido, ficava escondida longe do clique.
            renderizar_ultimo_resultado(cid)
    else:
        render_pagina_conteudo_dinamico(conteudo)
