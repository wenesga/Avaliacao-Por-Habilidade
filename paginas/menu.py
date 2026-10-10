"""Menu lateral."""

import os
import streamlit as st
from banco import perfil_atual, progresso_resumo_aluno
from config import ARQUIVO_LOGO, PAGINA_INICIO, PAGINA_MATERIA, PAGINA_PROFESSOR
from conteudos import obter_total_missoes
from sessao import apelido_invalido, entrar_como_aluno, ir_para_materia, sessao_professor_ativa


# Ordem fixa, sempre os mesmos blocos, sempre nas mesmas posições:
#   cabeçalho/Início (a própria marca) > identidade (altura reservada) >
#   Matérias > Professor.
# Nada aparece e some conforme a página, e o bloco de identidade tem altura mínima fixa no CSS justamente pra que logar/deslogar não empurre o menu inteiro pra baixo — o Streamlit desenha de cima pra baixo, então qualquer bloco condicional acima da navegação move tudo que vem depois.
def render_menu_lateral():
    """Conteúdo da barra lateral. Chamada dentro de `with st.sidebar:` no app.py."""
    # Botão "🏠 Início" no topo, acima da logo. A logo/título logo abaixo também leva à Início: dois caminhos para o mesmo destino.
    if st.button("🏠  Início", key="nav_inicio", use_container_width=True,
                 type="primary" if st.session_state.pagina == PAGINA_INICIO else "secondary"):
        st.session_state.pagina = PAGINA_INICIO
        st.rerun()

    # A logo/título TAMBÉM leva pra Início ao clicar — é o segundo caminho citado acima. Streamlit não deixa um st.image() disparar clique; por isso quem carrega a ação é o texto do título, estilizado por CSS (ver ".st-key-nav_titulo_inicio") pra não parecer um botão comum.
    with st.container(key="sidebar_cabecalho"):
        if os.path.exists(ARQUIVO_LOGO):
            st.image(ARQUIVO_LOGO, width=64)
        if st.button("Avaliação por Habilidade",
                     key="nav_titulo_inicio", use_container_width=True):
            st.session_state.pagina = PAGINA_INICIO
            st.rerun()

    with st.container(key="sidebar_identidade"):
        if st.session_state.aluno_ativo:
            perfil = perfil_atual()
            st.markdown(f"**👤 {st.session_state.aluno_ativo}**  \n🏆 {perfil['xp_total']} XP acumulados")
            if st.button("❌ Sair", use_container_width=True, key="sidebar_sair"):
                st.session_state.aluno_ativo = ""
                st.rerun()
        else:
            # "Apelido no jogo", não "Nome do Aluno": entrar com um nome inventado é parte da dinâmica, não um detalhe técnico. O aluno joga sem se expor quando erra, e é o professor que liga o apelido ao nome real, na hora do relatório (ver 'Nomes para o relatório').
            #
            # Em st.form: sem form, o texto digitado só é sincronizado com o backend no blur/Enter do campo, num evento separado do clique do botão — clicar em "Acessar" logo depois de digitar podia disparar o rerun do botão ANTES desse sync chegar, e o clique via nome_digitado vazio, sem erro nenhum na tela (só um F5 — que força tudo a sincronizar de novo — resolvia). O form agrupa campo e botão numa única mensagem, então o valor que chega é sempre o mais atual. Custo: a legenda de erro deixa de atualizar a cada tecla e passa a atualizar só ao tentar entrar — a linha continua sempre presente (mesmo motivo de altura de sempre), só a atualização que virou "ao enviar" em vez de "ao digitar".
            with st.form("form_login_aluno", border=False):
                nome_digitado = st.text_input(
                    "🎮 Seu apelido no jogo:", placeholder="Ex.: Goku99",
                    help="Invente um apelido — não precisa ser seu nome de verdade. "
                         "Uma palavra só, letras e números.",
                ).strip()
                erro_apelido = apelido_invalido(nome_digitado) if nome_digitado else ""
                if erro_apelido:
                    st.markdown(f'<div class="apelido-aviso erro">❌ {erro_apelido}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="apelido-aviso">Uma palavra, sem espaços.</div>', unsafe_allow_html=True)
                if st.form_submit_button("✅ Acessar", use_container_width=True):
                    if nome_digitado and not erro_apelido:
                        entrar_como_aluno(nome_digitado)

    # <hr> com classe própria (não "---" cru): o <hr> padrão do Streamlit tem margem maior em cima do que embaixo, então a linha ficava mais perto de "Matéria Padrão" do que do "Acessar" — medido no DOM (51px acima, 32px abaixo), não só impressão visual. Margem assimétrica própria (ver CSS) corrige, compensando o espaço extra que o st.form do login já soma.
    st.markdown('<hr class="sidebar-divisor-identidade">', unsafe_allow_html=True)

    # --- Nível 2: as matérias. Clicar aqui ABRE a matéria (não "seleciona"
    # uma matéria pra usar num botão lá de cima) — é isso que acaba com o modo escondido de antes. O progresso vai no próprio rótulo, então o menu responde "onde parei em cada matéria" sem nenhum bloco extra que cresça ou encolha. ---
    concluidas_por_conteudo = progresso_resumo_aluno()

    st.markdown('<div class="sidebar-secao">Disciplinas</div>', unsafe_allow_html=True)

    for cid, conteudo_info in st.session_state.conteudos.items():
        rotulo = f"{conteudo_info['icone']}  {conteudo_info['titulo']}"
        total_missoes = obter_total_missoes(cid)
        if st.session_state.aluno_ativo and total_missoes:
            feitas = min(concluidas_por_conteudo.get(cid, 0), total_missoes)
            rotulo += "  ✓" if feitas >= total_missoes else f"  ·  {feitas}/{total_missoes}"
        ativo = (st.session_state.pagina == PAGINA_MATERIA and cid == st.session_state.conteudo_ativo)
        if st.button(rotulo, key=f"nav_conteudo_{cid}", use_container_width=True,
                     type="primary" if ativo else "secondary"):
            ir_para_materia(cid)

    # Mesma classe da linha entre Acessar/Matéria Padrão (ver acima): o <hr> cru do Streamlit não fica com espaço igual dos dois lados sozinho.
    st.markdown('<hr class="sidebar-divisor-professor">', unsafe_allow_html=True)

    # --- Nível 1 de novo, separado: não faz parte do fluxo do aluno ---
    # O 🔓 existe porque "estar autenticado como professor" era um modo escondido: dava pra continuar com o painel destravado sem nenhum sinal na tela, e só descobrir isso clicando. Mesmo problema que a navegação tinha.
    rotulo_professor = "🛡️  Painel do Professor"
    if sessao_professor_ativa():
        rotulo_professor += "  🔓"
    if st.button(rotulo_professor, key="nav_professor", use_container_width=True,
                 type="primary" if st.session_state.pagina == PAGINA_PROFESSOR else "secondary"):
        st.session_state.pagina = PAGINA_PROFESSOR
        st.rerun()

    # Botão da pesquisa (formulário externo): só aparece se o professor colou o endereço em Configurações. Abre em outra aba.
    url_pesquisa = st.session_state.config.get("url_pesquisa", "")
    if url_pesquisa:
        st.markdown('<hr class="sidebar-divisor-professor">', unsafe_allow_html=True)
        st.link_button("📝  Responder Pesquisa", url_pesquisa, use_container_width=True)
