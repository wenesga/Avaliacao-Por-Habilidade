"""Painel do Professor: Gerenciar Conteúdos."""

import streamlit.components.v1 as components
import streamlit as st
import uuid
from conteudos import salvar_conteudos, xp_maximo_de_conteudo
from descritores import campo_descritor, carregar_descritores, descricao_curta_descritor, descritores_do_conteudo
from sessao import flash


@st.dialog("🗑️ Excluir conteúdo")
def _dialog_confirmar_exclusao_conteudo(cid, c):
    st.warning(f"⚠️ Tem certeza que deseja excluir **{c['icone']} {c['titulo']}**? As orientações e as questões cadastradas serão perdidas permanentemente.")
    col_conf, col_canc = st.columns(2)
    with col_conf:
        if st.button("✅ Sim, excluir", key=f"confirmar_del_{cid}", type="primary", use_container_width=True):
            del st.session_state.conteudos[cid]
            salvar_conteudos(st.session_state.conteudos)
            if st.session_state.conteudo_ativo == cid:
                st.session_state.conteudo_ativo = ""
            st.rerun()
    with col_canc:
        if st.button("❌ Cancelar", key=f"cancelar_del_{cid}", use_container_width=True):
            st.rerun()


def mover_conteudo(cid, direcao):
    """Sobe (direcao=-1) ou desce (direcao=+1) um conteúdo CADASTRADO PELO
    PROFESSOR uma posição."""
    chaves = list(st.session_state.conteudos.keys())
    idx = chaves.index(cid)
    novo_idx = idx + direcao
    if not (0 <= novo_idx < len(chaves)):
        return
    chaves[idx], chaves[novo_idx] = chaves[novo_idx], chaves[idx]
    st.session_state.conteudos = {k: st.session_state.conteudos[k] for k in chaves}
    salvar_conteudos(st.session_state.conteudos)


def render_gerenciar_conteudos():
    st.session_state.setdefault("editando_conteudo_id", None)
    st.session_state.setdefault("mostrar_form_conteudo", False)

    conteudos_em_ordem = list(st.session_state.conteudos.keys())

    def _renderizar_card_conteudo(cid):
        c = st.session_state.conteudos[cid]
        with st.container(border=True, key=f"card_conteudo_{cid}"):
            col_titulo, col_acoes = st.columns([3, 2])
            with col_titulo:
                st.markdown(f"##### {c['icone']} {c['titulo']}")
            with col_acoes:
                with st.container(key=f"acoes_conteudo_{cid}"):
                    col_subir, col_descer, col_editar, col_excluir = st.columns(4)
                    posicao = conteudos_em_ordem.index(cid)
                    with col_subir:
                        if st.button("▲", key=f"subir_{cid}", disabled=(posicao == 0),
                                     help="Mover para cima"):
                            mover_conteudo(cid, -1)
                            st.rerun()
                    with col_descer:
                        if st.button("▼", key=f"descer_{cid}", disabled=(posicao == len(conteudos_em_ordem) - 1),
                                     help="Mover para baixo"):
                            mover_conteudo(cid, 1)
                            st.rerun()
                    with col_editar:
                        if st.button("✏️ Editar", key=f"edit_{cid}"):
                            st.session_state.editando_conteudo_id = cid
                            st.session_state.mostrar_form_conteudo = True
                            st.session_state.novas_secoes_teoria = [dict(s) for s in c.get("teoria", [])]
                            st.session_state.novas_missoes = [dict(m) for m in c.get("missoes", [])]
                            st.session_state["novo_titulo_conteudo"] = c["titulo"]
                            st.session_state["novo_icone_conteudo"] = c["icone"]
                            st.session_state["nova_descricao_conteudo"] = c.get("descricao", "")
                            st.rerun()
                    with col_excluir:
                        if st.button("🗑️ Excluir", key=f"del_{cid}"):
                            _dialog_confirmar_exclusao_conteudo(cid, c)

            if c.get("descricao"):
                st.caption(c["descricao"])

            n_missoes = len(c.get("missoes", []))
            badges = [f'<span class="badge-conteudo badge-conteudo-tipo">🧩 {n_missoes} questão(ões)</span>']
            badges.append(f'<span class="badge-conteudo badge-conteudo-tipo">💯 Total {xp_maximo_de_conteudo(cid, c)} XP</span>')
            habilidades = descritores_do_conteudo(cid, c)
            if habilidades:
                badges.append(f'<span class="badge-conteudo badge-conteudo-descritor">🎯 Habilidades: {", ".join(habilidades)}</span>')
            st.markdown(" ".join(badges), unsafe_allow_html=True)
            com_descricao = [h for h in habilidades if descricao_curta_descritor(h)]
            for hab in com_descricao:
                st.caption(f"🎯 **{hab}** · {descricao_curta_descritor(hab, limite=170)}")

    if conteudos_em_ordem:
        st.subheader("📚 Conteúdos Cadastrados")
        for cid in conteudos_em_ordem:
            _renderizar_card_conteudo(cid)

    st.markdown('<div id="ancora-form-conteudo"></div>', unsafe_allow_html=True)
    st.markdown("---")

    if not st.session_state.mostrar_form_conteudo:
        if st.button("➕ Criar Novo Conteúdo"):
            st.session_state.mostrar_form_conteudo = True
            st.rerun()
        return

    editando = st.session_state.editando_conteudo_id
    if editando:
        conteudo_original = st.session_state.conteudos.get(editando, {})
        st.subheader(f"✏️ Editando: {conteudo_original.get('icone', '')} {conteudo_original.get('titulo', '')}")
        st.caption("Altere o que quiser abaixo — título, orientações, questões — e clique em Salvar. "
                   "Os campos já vieram preenchidos com o que existe hoje.")
        """
        Ao clicar em "Editar" na lista, o formulário aparece mais abaixo sem aviso; a tela rola
        sozinha até ele.
        """
        components.html(
            """
            <script>
            const ancora = window.parent.document.getElementById('ancora-form-conteudo');
            if (ancora) { ancora.scrollIntoView({behavior: 'smooth', block: 'start'}); }
            </script>
            """,
            height=0,
            width=0,
        )
    else:
        st.subheader("➕ Criar Novo Conteúdo")
        st.caption("Cadastre um conteúdo de Matemática ou Português.")

    novo_titulo = st.text_input("Título do conteúdo:", key="novo_titulo_conteudo")
    col_ic, col_desc = st.columns([1, 4])
    with col_ic:
        novo_icone = st.text_input("Ícone (emoji):", value="📘", key="novo_icone_conteudo")
    with col_desc:
        nova_descricao = st.text_input("Descrição curta:", key="nova_descricao_conteudo")

    st.markdown("#### Orientações")
    st.caption("Adicione quantas seções quiser.")
    with st.expander("❔ Como formatar o texto"):
        st.markdown(
            "**Texto**\n"
            "- Negrito: `**texto**`\n"
            "- Itálico: `*texto*`\n"
            "- Sublinhado: o Markdown não tem esse comando — use negrito ou itálico pra destacar.\n"
            "- Título de sub-seção dentro do texto: `## Título`\n"
            "- Lista: uma linha por item, começando com `-`\n"
            "- Bloco destacado (exemplo, fórmula, etc.): três crases ` ``` ` antes e depois do trecho\n\n"
            "**Matemática (LaTeX)** — entre `$...$` pra ficar no meio da frase, ou `$$...$$` "
            "numa linha própria pra centralizar:\n"
            "- Fração: `$\\frac{a}{b}$`\n"
            "- Raiz: `$\\sqrt{x}$`\n"
            "- Expoente: `$x^2$`"
        )
    for i, secao in enumerate(st.session_state.novas_secoes_teoria):
        with st.container(border=True):
            c1, c2 = st.columns([5, 1])
            with c1:
                secao["titulo"] = st.text_input(f"Título da seção {i + 1}", value=secao.get("titulo", ""), key=f"edit_titulo_secao_{i}")
                secao["texto"] = st.text_area(f"Conteúdo da seção {i + 1} (aceita markdown)", value=secao.get("texto", ""), key=f"edit_texto_secao_{i}", height=140)
            with c2:
                if st.button("🗑️ Excluir", key=f"del_secao_{i}"):
                    st.session_state.novas_secoes_teoria.pop(i)
                    st.rerun()

    with st.form("form_add_secao", clear_on_submit=True):
        titulo_secao = st.text_input("Título da seção")
        texto_secao = st.text_area("Conteúdo da seção (aceita markdown)")
        if st.form_submit_button("➕ Adicionar Seção de Orientações"):
            if titulo_secao and texto_secao:
                st.session_state.novas_secoes_teoria.append({"titulo": titulo_secao, "texto": texto_secao})
                st.rerun()
            else:
                st.error("Preencha o título e o texto da seção.")

    st.markdown("#### Questões da Avaliação")
    st.caption("Adicione as perguntas do jogo.")
    for i, missao in enumerate(st.session_state.novas_missoes):
        with st.container(border=True):
            c1, c2 = st.columns([5, 1])
            with c1:
                missao["titulo"] = st.text_input(f"Título curto da questão {i + 1}", value=missao.get("titulo", ""), key=f"edit_titulo_missao_{i}")
                missao["pergunta"] = st.text_area(f"Pergunta/desafio {i + 1}", value=missao.get("pergunta", ""), key=f"edit_pergunta_missao_{i}")
                col_r, col_t, col_p = st.columns(3)
                with col_r:
                    missao["resposta"] = st.text_input(f"Resposta correta {i + 1}", value=str(missao.get("resposta", "")), key=f"edit_resposta_missao_{i}")
                with col_t:
                    tipos = ["numero", "texto", "multipla"]
                    tipo_atual = missao.get("tipo", "numero")
                    missao["tipo"] = st.selectbox(
                        f"Tipo de resposta {i + 1}", tipos,
                        index=tipos.index(tipo_atual) if tipo_atual in tipos else 0,
                        key=f"edit_tipo_missao_{i}",
                        format_func=lambda t: {"numero": "número", "multipla": "múltipla escolha"}.get(t, t),
                    )
                with col_p:
                    missao["pontos"] = int(st.number_input(
                        f"Pontos (XP) {i + 1}", min_value=1, value=int(missao.get("pontos", 10)),
                        step=1, key=f"edit_pontos_missao_{i}",
                    ))
                if missao["tipo"] == "multipla":
                    texto_alts = st.text_area(
                        f"Alternativas {i + 1} — uma por linha",
                        value="\n".join(missao.get("alternativas", [])),
                        key=f"edit_alts_missao_{i}",
                        help="A resposta correta precisa ser idêntica a uma destas linhas.",
                    )
                    missao["alternativas"] = [l.strip() for l in texto_alts.splitlines() if l.strip()]
                    if len(missao["alternativas"]) < 2:
                        st.warning(f"⚠️ Questão {i + 1}: múltipla escolha precisa de pelo menos duas alternativas.")
                    elif str(missao.get("resposta", "")).strip() not in missao["alternativas"]:
                        st.warning(
                            f"⚠️ Questão {i + 1}: a resposta correta \"{missao.get('resposta', '')}\" "
                            "não está entre as alternativas. O aluno não teria como acertar."
                        )
                elif "alternativas" in missao:
                    del missao["alternativas"]
                missao["descritor"] = campo_descritor(
                    f"Descritor SAETO {i + 1} (opcional)", valor_atual=missao.get("descritor", ""),
                    chave=f"edit_descritor_missao_{i}",
                    ajuda="Descritor do SAETO (como D044_M) que esta questão exercita. "
                          "Pode digitar um código que não está na lista. Deixe em branco se não quiser mapear.",
                )
                if missao["descritor"] and descricao_curta_descritor(missao["descritor"]):
                    st.caption(carregar_descritores()[missao["descritor"]])
            with c2:
                if st.button("🗑️ Excluir", key=f"del_missao_{i}"):
                    st.session_state.novas_missoes.pop(i)
                    st.rerun()

    with st.form("form_add_missao", clear_on_submit=True):
        titulo_missao = st.text_input("Título curto da questão")
        pergunta_missao = st.text_area(
            "Pergunta/desafio apresentado ao aluno",
            help="Para escrever cifrão, use \\$ (ex.: R\\$ 50,00). Um $ sozinho é lido como "
                 "início de fórmula matemática e o texto entre dois cifrões desaparece da tela.",
        )
        col_r, col_t, col_p = st.columns(3)
        with col_r:
            resposta_missao = st.text_input("Resposta correta")
        with col_t:
            tipo_missao = st.selectbox(
                "Tipo de resposta", ["numero", "texto", "multipla"],
                format_func=lambda t: {"numero": "número", "multipla": "múltipla escolha"}.get(t, t),
            )
        with col_p:
            pontos_missao = st.number_input("Pontos (XP)", min_value=1, value=10, step=1)
        """
        O campo de alternativas fica sempre visível, mesmo quando o tipo não é múltipla escolha:
        dentro de um st.form os widgets não disparam rerun, então não há como mostrá-lo só depois
        que o professor escolhe o tipo.
        """
        alternativas_missao = st.text_area(
            "Alternativas (só para múltipla escolha) — uma por linha",
            placeholder="média\nmediana\nmoda",
            help="Escreva uma alternativa por linha. A \"Resposta correta\" acima precisa ser "
                 "idêntica a uma delas. Na múltipla escolha o aluno não digita nada, só escolhe, "
                 "então não erra por causa de acento ou de letra trocada.",
        )
        descritor_missao = campo_descritor(
            "Descritor SAETO (opcional)", chave="nova_descritor_missao",
            ajuda="Descritor do SAETO (como D044_M) que esta questão exercita. "
                  "Pode digitar um código que não está na lista. É o que permite ao Painel do Professor relatar o desempenho por habilidade.",
        )
        if st.form_submit_button("➕ Adicionar Questão"):
            alternativas = [linha.strip() for linha in alternativas_missao.splitlines() if linha.strip()]
            erro_missao = ""
            if not (titulo_missao and pergunta_missao and resposta_missao):
                erro_missao = "Preencha o título, a pergunta e a resposta correta."
            elif tipo_missao == "multipla":
                """
                Validado no cadastro, e não na aula: uma questão de múltipla escolha sem
                alternativas, ou cuja resposta correta não esteja entre elas, seria impossível de
                acertar.
                """
                if len(alternativas) < 2:
                    erro_missao = "Múltipla escolha precisa de pelo menos duas alternativas, uma por linha."
                elif resposta_missao.strip() not in alternativas:
                    erro_missao = ("A resposta correta precisa ser idêntica a uma das alternativas. "
                                   f"Você escreveu \"{resposta_missao.strip()}\", e as alternativas são: "
                                   + ", ".join(f'"{a}"' for a in alternativas) + ".")
            if erro_missao:
                st.error(erro_missao)
            else:
                nova_missao = {
                    "titulo": titulo_missao,
                    "pergunta": pergunta_missao,
                    "resposta": resposta_missao.strip(),
                    "tipo": tipo_missao,
                    "pontos": int(pontos_missao),
                    "descritor": descritor_missao.strip(),
                }
                if tipo_missao == "multipla":
                    nova_missao["alternativas"] = alternativas
                st.session_state.novas_missoes.append(nova_missao)
                st.rerun()

    st.markdown("---")

    def limpar_formulario_conteudo():
        st.session_state.editando_conteudo_id = None
        st.session_state.mostrar_form_conteudo = False
        st.session_state.novas_secoes_teoria = []
        st.session_state.novas_missoes = []
        for campo in ("novo_titulo_conteudo", "novo_icone_conteudo", "nova_descricao_conteudo"):
            st.session_state.pop(campo, None)

    col_salvar, col_cancelar, _ = st.columns([1, 1, 4])
    with col_salvar:
        if st.button("💾 Salvar", type="primary", key="salvar_conteudo_btn"):
            if not novo_titulo:
                st.error("Dê um título ao conteúdo antes de salvar.")
            elif not st.session_state.novas_secoes_teoria and not st.session_state.novas_missoes:
                st.error("Adicione ao menos uma seção de orientações ou uma questão antes de salvar.")
            else:
                alvo_id = editando if editando else f"conteudo_{uuid.uuid4().hex[:8]}"
                st.session_state.conteudos[alvo_id] = {
                    "titulo": novo_titulo,
                    "icone": novo_icone or "📘",
                    "descricao": nova_descricao,
                    "tipo": "dinamico",
                    "teoria": st.session_state.novas_secoes_teoria,
                    "missoes": st.session_state.novas_missoes,
                }
                salvar_conteudos(st.session_state.conteudos)
                limpar_formulario_conteudo()
                flash("Salvo com sucesso!")
                st.rerun()
    with col_cancelar:
        if st.button("❌ Cancelar", key="cancelar_edicao_btn"):
            limpar_formulario_conteudo()
            st.rerun()
