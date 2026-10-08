"""Painel do Professor: Configurações."""

import hashlib
import streamlit as st
from configuracao import salvar_config, senha_correta
from conteudos import xp_maximo_catalogo_atual, xp_maximo_de_conteudo
from sessao import flash


def render_configuracoes():
    st.subheader("🏫 Instituição")
    st.caption("Exibidos no cabeçalho do relatório em PDF. Deixe em branco pra não mostrar.")
    with st.form("form_instituicao"):
        nome_instituicao = st.text_input(
            "Nome da instituição",
            value=st.session_state.config.get("nome_instituicao", ""),
        )
        nome_professor = st.text_input(
            "Nome do professor",
            value=st.session_state.config.get("nome_professor", ""),
        )
        turma = st.text_input(
            "Turma/Série",
            value=st.session_state.config.get("turma", ""),
            placeholder="Ex.: 1º Ano - Ensino Médio, EJA, 9º Ano",
        )
        cidade = st.text_input(
            "Cidade (para a data do relatório)",
            value=st.session_state.config.get("cidade", ""),
            placeholder="Ex.: Arraias - TO",
        )
        st.caption("A data do relatório é sempre a data em que ele foi gerado — preenchida sozinha, não precisa digitar.")
        if st.form_submit_button("Salvar"):
            st.session_state.config["nome_instituicao"] = nome_instituicao.strip()
            st.session_state.config["nome_professor"] = nome_professor.strip()
            st.session_state.config["turma"] = turma.strip()
            st.session_state.config["cidade"] = cidade.strip()
            salvar_config(st.session_state.config)
            flash("Salvo com sucesso!")
            st.rerun()

    st.markdown("---")
    st.subheader("🎯 Meta de XP")
    st.caption(
        "Usada só pra colorir o gráfico \"Desempenho da Turma\" (Visão Geral): "
        "a cor segue as 4 faixas da escola: até 40% da meta vermelho, 41–60% laranja, "
        "61–79% amarelo e 80% ou mais verde."
    )
    xp_catalogo_hoje = xp_maximo_catalogo_atual()
    st.markdown(
        f'<div class="resumo-xp-card resumo-xp-total">'
        f'<div class="rotulo">Total das disciplinas</div>'
        f'<div class="valor">{xp_catalogo_hoje} XP</div></div>',
        unsafe_allow_html=True,
    )

    # Seletor de conteúdo — sugestão do orientador ("Conversar com
    # orientador 02.txt", 2026-09-17): o professor escolhe a disciplina do
    # dia e vê o XP dela. Fora do form de propósito — precisa rerodar assim
    # que troca a escolha, pra atualizar o campo de meta antes de clicar
    # Salvar; widget de form só atualiza no submit, o que travaria isso.
    opcoes_conteudo = {"__catalogo__": "Todas"}
    opcoes_conteudo.update({cid: c["titulo"] for cid, c in st.session_state.conteudos.items()})
    opcoes_ids = list(opcoes_conteudo.keys())

    # Lembra a última escolha no PRÓPRIO config_sistema.json, não só em
    # session_state: session_state morre inteiro com um F5 de verdade (é
    # uma sessão nova pro Streamlit), então guardar só na sessão fazia a
    # escolha "sobreviver a trocar de aba" mas sumir de novo ao atualizar a
    # página — reportado pelo Wenes (2026-09-17). meta_xp já é salvo em
    # disco por esse mesmo arquivo; o foco escolhido segue o mesmo caminho.
    #
    # O widget usa key= e NÃO recebe index= — as duas coisas juntas foram a
    # causa de um bug sério, também relatado pelo Wenes (2026-09-17,
    # descrito com muito detalhe): trocar a escolha sem clicar Salvar fazia
    # a seleção "oscilar", voltando pra anterior a cada segunda troca.
    # Calcular index=... a partir de um valor que a MESMA rodada do script
    # também escreve de volta em session_state cria uma corrida — o
    # Streamlit não consegue distinguir com segurança "isso é o clique novo
    # do usuário" de "isso é só o padrão que acabei de recalcular", e às
    # vezes descarta o clique. Com key= só, o valor mora inteiramente em
    # st.session_state[key] e o Streamlit cuida de tudo sozinho, sem essa
    # corrida — é o padrão mais robusto pra widget com estado.
    if "meta_xp_foco_selecionado" not in st.session_state:
        st.session_state["meta_xp_foco_selecionado"] = st.session_state.config.get("ultimo_foco_meta_xp", "__catalogo__")
    if st.session_state["meta_xp_foco_selecionado"] not in opcoes_ids:
        st.session_state["meta_xp_foco_selecionado"] = "__catalogo__"
    conteudo_foco = st.selectbox(
        "Foco de hoje",
        options=opcoes_ids,
        format_func=lambda cid: opcoes_conteudo[cid],
        help="Escolha a disciplina que a turma vai estudar hoje pra já preencher o campo de meta com o XP dela.",
        key="meta_xp_foco_selecionado",
    )
    if conteudo_foco != st.session_state.config.get("ultimo_foco_meta_xp"):
        st.session_state.config["ultimo_foco_meta_xp"] = conteudo_foco
        salvar_config(st.session_state.config)
    if conteudo_foco == "__catalogo__":
        # Todas as disciplinas: a meta já vem com a SOMA delas (Matemática + Português).
        st.caption(f"💡 Todas as disciplinas somam **{xp_catalogo_hoje} XP**, já preenchido abaixo. Reduza se quiser uma meta mais fácil.")
        valor_padrao_meta = xp_catalogo_hoje
    else:
        xp_referencia = xp_maximo_de_conteudo(conteudo_foco, st.session_state.conteudos[conteudo_foco])
        st.caption(f"💡 \"{opcoes_conteudo[conteudo_foco]}\" vale até **{xp_referencia} XP** — já preenchido abaixo. Reduza se quiser uma meta mais fácil.")
        valor_padrao_meta = xp_referencia

    # key inclui o conteúdo escolhido de propósito: assim, trocar a escolha
    # no seletor acima cria um widget "novo" pro Streamlit, que preenche de
    # novo com valor_padrao_meta — sem isso, o campo manteria o número
    # digitado antes mesmo depois de trocar de conteúdo (pedido do Wenes,
    # 2026-09-17: quer o campo preenchendo sozinho a cada troca, e editável
    # se ele quiser uma meta menor do que o total).
    with st.form("form_meta_xp"):
        meta_xp_input = st.number_input(
            "Meta de XP",
            min_value=1, step=10,
            value=int(valor_padrao_meta),
            key=f"meta_xp_input_{conteudo_foco}",
        )
        if st.form_submit_button("Salvar"):
            st.session_state.config["meta_xp"] = int(meta_xp_input)
            salvar_config(st.session_state.config)
            flash("Salvo com sucesso!")
            st.rerun()

    st.markdown("---")
    st.subheader("📝 Pesquisa")
    with st.form("form_pesquisa"):
        url_pesquisa = st.text_input(
            "Endereço do formulário",
            value=st.session_state.config.get("url_pesquisa", ""),
            placeholder="https://docs.google.com/forms/...",
            help="Deixe em branco pra esconder o botão \"Responder Pesquisa\" do menu.",
        )
        if st.form_submit_button("Salvar"):
            url_pesquisa = url_pesquisa.strip()
            if url_pesquisa and not url_pesquisa.startswith("https://"):
                st.error("O endereço precisa começar com https://")
            else:
                st.session_state.config["url_pesquisa"] = url_pesquisa
                salvar_config(st.session_state.config)
                flash("Salvo com sucesso!")
                st.rerun()

    st.markdown("---")
    st.subheader("🔑 Alterar Senha do Professor")
    with st.form("form_senha"):
        senha_atual = st.text_input("Senha atual", type="password")
        senha_nova = st.text_input("Nova senha", type="password")
        senha_nova_conf = st.text_input("Confirme a nova senha", type="password")
        if st.form_submit_button("Alterar Senha"):
            if not senha_correta(senha_atual, st.session_state.config):
                st.error("Senha atual incorreta.")
            elif not senha_nova or senha_nova != senha_nova_conf:
                st.error("As novas senhas não coincidem ou estão vazias.")
            else:
                st.session_state.config["senha_hash"] = hashlib.sha256(senha_nova.encode()).hexdigest()
                salvar_config(st.session_state.config)
                st.success("Senha alterada com sucesso!")
