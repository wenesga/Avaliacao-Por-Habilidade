"""Painel do Professor: Gerenciar Questões e orientações das disciplinas."""

import streamlit as st
from conteudos import salvar_conteudos, xp_maximo_de_conteudo
from descritores import campo_descritores, descritores_da_missao
from imagens_questoes import caminho_imagem_questao, salvar_imagem_questao
from sessao import flash

TIPOS_RESPOSTA = ["multipla", "numero", "texto"]
ROTULOS_TIPO = {"multipla": "Múltipla escolha", "numero": "Resposta numérica", "texto": "Resposta em texto"}
DISCIPLINAS_PADRAO = (("matematica", "Matemática", "🧮"), ("portugues", "Português", "📚"))
AJUDA_ENUNCIADO = (
    "Para escrever cifrão, use \\$ (ex.: R\\$ 50,00). Um $ sozinho é lido como início de fórmula "
    "matemática e o texto entre dois cifrões desaparece da tela."
)
AJUDA_DESCRITORES = (
    "Descritores do SAETO (como D044_M) que esta questão exercita. Marque só os que a questão "
    "realmente exige: o acerto e o erro contam em todos. Pode digitar um código que não está na "
    "lista. É o que permite ao Painel do Professor relatar o desempenho por habilidade."
)


def _garantir_disciplinas():
    """Cria a disciplina padrão que faltar, para o formulário de questões sempre ter onde gravar."""
    criou = False
    for cid, titulo, icone in DISCIPLINAS_PADRAO:
        if cid not in st.session_state.conteudos:
            st.session_state.conteudos[cid] = {
                "titulo": titulo, "icone": icone, "descricao": "", "tipo": "dinamico",
                "teoria": [], "missoes": [],
            }
            criou = True
    if criou:
        salvar_conteudos(st.session_state.conteudos)


def _rotulo_disciplina(cid):
    c = st.session_state.conteudos[cid]
    return f"{c.get('icone', '')} {c.get('titulo', cid)}".strip()


def _erro_questao(pergunta, resposta, tipo, alternativas):
    """Texto do problema que impede de gravar a questão; vazio se está válida.

    Validado no cadastro, e não na aula: uma múltipla escolha sem alternativas, ou cuja resposta
    correta não esteja entre elas, seria impossível de acertar."""
    if not (pergunta.strip() and resposta.strip()):
        return "Preencha o enunciado e a resposta correta."
    if tipo == "multipla":
        if len(alternativas) < 2:
            return "Múltipla escolha precisa de pelo menos duas alternativas, uma por linha."
        if resposta.strip() not in alternativas:
            return ("A resposta correta precisa ser idêntica a uma das alternativas. "
                    f"Você escreveu \"{resposta.strip()}\", e as alternativas são: "
                    + ", ".join(f'"{a}"' for a in alternativas) + ".")
    return ""


def _linhas(texto):
    return [linha.strip() for linha in texto.splitlines() if linha.strip()]


def _campos_questao(prefixo, inicial):
    """
    Campos de uma questão, usados no cadastro e na edição. `inicial` traz os valores de partida
    (dict vazio para uma questão nova). Fora de um st.form, para que as alternativas apareçam só
    quando o tipo é múltipla escolha. Devolve a questão montada e o texto do erro, se houver.
    """
    titulo = st.text_input("Título curto (opcional)", value=inicial.get("titulo", ""), key=f"{prefixo}_titulo")
    pergunta = st.text_area(
        "Enunciado da questão", value=inicial.get("pergunta", ""), key=f"{prefixo}_pergunta",
        help=AJUDA_ENUNCIADO,
    )
    imagem_atual = inicial.get("imagem", "")
    manter_imagem = bool(imagem_atual)
    if imagem_atual:
        caminho_atual = caminho_imagem_questao(imagem_atual)
        if caminho_atual:
            st.image(caminho_atual, width=240)
        else:
            st.caption("A imagem desta questão não foi encontrada neste servidor.")
        manter_imagem = not st.checkbox("Remover a imagem do enunciado", key=f"{prefixo}_remover_imagem")
    enviado = st.file_uploader(
        "Imagem do enunciado (opcional)", type=["png", "jpg", "jpeg"], key=f"{prefixo}_imagem",
        help="Use quando o enunciado fala de uma figura, gráfico ou tabela. Pode ser um arquivo "
             "exportado de um editor de figuras. A imagem é reduzida ao tamanho em que aparece "
             "para o aluno, o que a deixa leve e nítida. Enviar outra imagem substitui a atual.",
    )
    if enviado:
        st.image(enviado, width=240)
    legenda_imagem = st.text_input(
        "Legenda da imagem (opcional)", value=inicial.get("legenda_imagem", ""),
        key=f"{prefixo}_legenda_imagem", help="Texto curto que aparece embaixo da imagem.",
    )
    tipo_atual = inicial.get("tipo", "multipla")
    tipo = st.radio(
        "Tipo de resposta", TIPOS_RESPOSTA, horizontal=True, key=f"{prefixo}_tipo",
        index=TIPOS_RESPOSTA.index(tipo_atual) if tipo_atual in TIPOS_RESPOSTA else 0,
        format_func=ROTULOS_TIPO.get,
    )
    alternativas = []
    if tipo == "multipla":
        texto_alts = st.text_area(
            "Alternativas, uma por linha", value="\n".join(inicial.get("alternativas", [])),
            key=f"{prefixo}_alternativas", placeholder="média\nmediana\nmoda",
            help="Na múltipla escolha o aluno só escolhe, então não erra por causa de acento ou de "
                 "letra trocada.",
        )
        alternativas = _linhas(texto_alts)
    resposta = st.text_input(
        "Resposta correta", value=str(inicial.get("resposta", "")), key=f"{prefixo}_resposta",
        help="Na múltipla escolha, escreva exatamente como uma das alternativas.",
    )
    pontos = int(st.number_input(
        "Pontos (XP)", min_value=1, value=int(inicial.get("pontos", 10)), step=1, key=f"{prefixo}_pontos",
    ))
    descritores = campo_descritores(
        "Descritores SAETO (opcional)", valores_atuais=descritores_da_missao(inicial),
        chave=f"{prefixo}_descritores", ajuda=AJUDA_DESCRITORES,
    )
    questao = {
        "titulo": titulo.strip(), "pergunta": pergunta, "resposta": resposta.strip(),
        "tipo": tipo, "pontos": pontos, "descritores": descritores,
    }
    if tipo == "multipla":
        questao["alternativas"] = alternativas
    if manter_imagem:
        questao["imagem"] = imagem_atual
    if legenda_imagem.strip() and (manter_imagem or enviado):
        questao["legenda_imagem"] = legenda_imagem.strip()
    return questao, _erro_questao(pergunta, resposta, tipo, alternativas), enviado


def _anexar_imagem(questao, enviado):
    """Grava a imagem enviada e põe o nome na questão. Devolve o texto do erro, se houver."""
    if enviado is None:
        return ""
    try:
        questao["imagem"] = salvar_imagem_questao(enviado)
    except ValueError:
        return "Não foi possível ler a imagem. Envie um arquivo PNG ou JPG."
    return ""


def _form_adicionar_questao():
    st.subheader("➕ Adicionar questão")
    st.caption("Escolha a disciplina, escreva a questão e marque os descritores da habilidade que ela exige.")
    """
    A versão entra na chave de cada campo: ao gravar, ela sobe e os campos reaparecem vazios, sem
    mexer em st.session_state de widgets já instanciados (o que o Streamlit não permite).
    """
    versao = st.session_state.setdefault("versao_form_questao", 0)
    cid = st.radio(
        "Disciplina", list(st.session_state.conteudos), horizontal=True,
        key="disciplina_nova_questao", format_func=_rotulo_disciplina,
    )
    questao, erro, enviado = _campos_questao(f"nova_questao_{versao}", {})
    if st.button("➕ Adicionar questão", type="primary", key="btn_adicionar_questao"):
        erro = erro or _anexar_imagem(questao, enviado)
        if erro:
            st.error(erro)
            return
        st.session_state.conteudos[cid].setdefault("missoes", []).append(questao)
        salvar_conteudos(st.session_state.conteudos)
        st.session_state.versao_form_questao = versao + 1
        flash(f"Questão adicionada em {_rotulo_disciplina(cid)}.")
        st.rerun()


@st.dialog("🗑️ Excluir questão")
def _dialog_excluir_questao(cid, indice):
    questao = st.session_state.conteudos[cid]["missoes"][indice]
    st.warning(
        f"Excluir a questão {indice + 1} de **{_rotulo_disciplina(cid)}**"
        f"{': ' + questao['titulo'] if questao.get('titulo') else ''}? "
        "As respostas dos alunos são guardadas pelo número da questão: excluir uma questão do meio "
        "da lista desloca o número das seguintes e desalinha o histórico delas. Para corrigir um "
        "erro, prefira editar a questão."
    )
    col_conf, col_canc = st.columns(2)
    with col_conf:
        if st.button("✅ Sim, excluir", key=f"confirmar_del_q_{cid}_{indice}", type="primary", use_container_width=True):
            del st.session_state.conteudos[cid]["missoes"][indice]
            salvar_conteudos(st.session_state.conteudos)
            st.session_state.pop("questao_em_edicao", None)
            st.rerun()
    with col_canc:
        if st.button("❌ Cancelar", key=f"cancelar_del_q_{cid}_{indice}", use_container_width=True):
            st.rerun()


def _editor_questao(cid, indice):
    questao_atual = st.session_state.conteudos[cid]["missoes"][indice]
    questao, erro, enviado = _campos_questao(f"edit_questao_{cid}_{indice}", questao_atual)
    col_salvar, col_cancelar, _ = st.columns([1, 1, 3])
    with col_salvar:
        if st.button("💾 Salvar", type="primary", key=f"salvar_q_{cid}_{indice}"):
            erro = erro or _anexar_imagem(questao, enviado)
            if erro:
                st.error(erro)
            else:
                st.session_state.conteudos[cid]["missoes"][indice] = questao
                salvar_conteudos(st.session_state.conteudos)
                st.session_state.pop("questao_em_edicao", None)
                flash("Questão salva.")
                st.rerun()
    with col_cancelar:
        if st.button("❌ Cancelar", key=f"cancelar_q_{cid}_{indice}"):
            st.session_state.pop("questao_em_edicao", None)
            st.rerun()


def _linha_questao(cid, indice, questao):
    codigos = descritores_da_missao(questao)
    with st.container(border=True, key=f"linha_questao_{cid}_{indice}"):
        col_info, col_editar, col_excluir = st.columns([6, 1, 1])
        with col_info:
            resumo = questao.get("titulo") or questao.get("pergunta", "")[:90]
            st.text(f"{indice + 1}. {resumo}")
            detalhes = [ROTULOS_TIPO.get(questao.get("tipo", "numero"), ""), f"{questao.get('pontos', 10)} XP"]
            detalhes.append("🎯 " + ", ".join(codigos) if codigos else "sem descritor")
            if questao.get("imagem"):
                detalhes.append("🖼️ com imagem")
            st.caption(" · ".join(d for d in detalhes if d))
        with col_editar:
            if st.button("✏️", key=f"edit_q_{cid}_{indice}", help="Editar questão"):
                st.session_state.questao_em_edicao = (cid, indice)
                st.rerun()
        with col_excluir:
            if st.button("🗑️", key=f"del_q_{cid}_{indice}", help="Excluir questão"):
                _dialog_excluir_questao(cid, indice)


def _card_disciplina(cid):
    c = st.session_state.conteudos[cid]
    missoes = c.get("missoes", [])
    em_edicao = st.session_state.get("questao_em_edicao")
    with st.container(border=True, key=f"card_conteudo_{cid}"):
        col_titulo, col_orient = st.columns([3, 2])
        with col_titulo:
            st.markdown(f"##### {_rotulo_disciplina(cid)}")
        with col_orient:
            if st.button("📖 Editar orientações", key=f"edit_{cid}"):
                st.session_state.editando_conteudo_id = cid
                st.session_state.mostrar_form_conteudo = True
                st.session_state.novas_secoes_teoria = [dict(s) for s in c.get("teoria", [])]
                st.session_state["novo_titulo_conteudo"] = c["titulo"]
                st.session_state["novo_icone_conteudo"] = c["icone"]
                st.session_state["nova_descricao_conteudo"] = c.get("descricao", "")
                st.rerun()
        if c.get("descricao"):
            st.caption(c["descricao"])

        badges = [f'<span class="badge-conteudo badge-conteudo-tipo">🧩 {len(missoes)} questão(ões)</span>',
                  f'<span class="badge-conteudo badge-conteudo-tipo">💯 Total {xp_maximo_de_conteudo(cid, c)} XP</span>']
        st.markdown(" ".join(badges), unsafe_allow_html=True)

        with st.expander(f"Ver as {len(missoes)} questões", expanded=bool(em_edicao and em_edicao[0] == cid)):
            if not missoes:
                st.info("Nenhuma questão nesta disciplina ainda. Use o formulário acima.")
            for indice, questao in enumerate(missoes):
                if em_edicao == (cid, indice):
                    with st.container(border=True, key=f"editor_questao_{cid}_{indice}"):
                        st.markdown(f"**Editando a questão {indice + 1}**")
                        _editor_questao(cid, indice)
                else:
                    _linha_questao(cid, indice, questao)


def _editor_orientacoes():
    """Edita título, ícone, descrição e orientações de uma disciplina. As questões não passam por aqui."""
    cid = st.session_state.editando_conteudo_id
    original = st.session_state.conteudos.get(cid, {})
    st.subheader(f"📖 Orientações: {_rotulo_disciplina(cid)}")
    st.caption("Altere o que quiser abaixo e clique em Salvar. Os campos já vieram preenchidos com o que existe hoje.")

    novo_titulo = st.text_input("Título da disciplina:", key="novo_titulo_conteudo")
    col_ic, col_desc = st.columns([1, 4])
    with col_ic:
        novo_icone = st.text_input("Ícone (emoji):", key="novo_icone_conteudo")
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

    st.markdown("---")

    def fechar_editor():
        st.session_state.editando_conteudo_id = None
        st.session_state.mostrar_form_conteudo = False
        st.session_state.novas_secoes_teoria = []
        for campo in ("novo_titulo_conteudo", "novo_icone_conteudo", "nova_descricao_conteudo"):
            st.session_state.pop(campo, None)

    col_salvar, col_cancelar, _ = st.columns([1, 1, 4])
    with col_salvar:
        if st.button("💾 Salvar", type="primary", key="salvar_conteudo_btn"):
            if not novo_titulo:
                st.error("Dê um título à disciplina antes de salvar.")
            else:
                st.session_state.conteudos[cid] = {
                    **original,
                    "titulo": novo_titulo,
                    "icone": novo_icone or "📘",
                    "descricao": nova_descricao,
                    "teoria": st.session_state.novas_secoes_teoria,
                }
                salvar_conteudos(st.session_state.conteudos)
                fechar_editor()
                flash("Salvo com sucesso!")
                st.rerun()
    with col_cancelar:
        if st.button("❌ Cancelar", key="cancelar_edicao_btn"):
            fechar_editor()
            st.rerun()


def render_gerenciar_conteudos():
    st.session_state.setdefault("editando_conteudo_id", None)
    st.session_state.setdefault("mostrar_form_conteudo", False)
    _garantir_disciplinas()

    if st.session_state.mostrar_form_conteudo and st.session_state.editando_conteudo_id in st.session_state.conteudos:
        _editor_orientacoes()
        return

    _form_adicionar_questao()
    st.markdown("---")
    st.subheader("📋 Questões cadastradas")
    for cid in st.session_state.conteudos:
        _card_disciplina(cid)
