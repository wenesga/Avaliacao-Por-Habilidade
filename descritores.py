"""Descritores SAETO (ex.: D044_M): lista, descrições e desempenho por descritor."""

import json
import os
import streamlit as st
from config import ARQUIVO_DESCRITORES_SAETO
from conteudos import obter_total_missoes


def obter_descritor_missao(conteudo_id, indice_missao):
    """Descritor SAETO de uma questão (string vazia se não mapeada).
    indice_missao é 1-based, igual ao usado em progresso['missao_atual']."""
    missoes = st.session_state.conteudos.get(conteudo_id, {}).get("missoes", [])
    if 1 <= indice_missao <= len(missoes):
        return str(missoes[indice_missao - 1].get("descritor", "")).strip()
    return ""


@st.cache_data
def _ler_descritores(data_do_arquivo):
    # O parâmetro só existe para o cache se renovar quando o arquivo mudar.
    try:
        with open(ARQUIVO_DESCRITORES_SAETO, encoding="utf-8") as f:
            return json.load(f).get("descritores", {})
    except (OSError, ValueError):
        return {}


def carregar_descritores():
    """{código: descrição} dos descritores que o professor pode escolher (Matemática
    e Português). Dicionário vazio se o arquivo não existir — aí o campo vira texto livre."""
    try:
        data = os.path.getmtime(ARQUIVO_DESCRITORES_SAETO)
    except OSError:
        data = 0
    return _ler_descritores(data)


def descricao_curta_descritor(codigo, limite=85):
    """Começo da descrição oficial, cortado numa palavra inteira. Vazio se o
    código não está no banco (por exemplo, um código digitado à mão antes)."""
    texto = carregar_descritores().get(str(codigo).strip(), "")
    if len(texto) <= limite:
        return texto
    return texto[:limite].rsplit(" ", 1)[0].rstrip(",;:") + "…"


def campo_descritor(rotulo, valor_atual="", chave=None, ajuda=""):
    """Campo de descritor SAETO: lista pesquisável (código + descrição curta) quando
    o banco existe; texto livre quando não. Devolve só o código ('' se vazio)."""
    habilidades = carregar_descritores()
    valor_atual = str(valor_atual or "").strip()
    if not habilidades:
        return st.text_input(rotulo, value=valor_atual, placeholder="Ex.: D044_M ou EM13MAT316", key=chave, help=ajuda).strip()
    opcoes = sorted(habilidades)
    if valor_atual and valor_atual not in habilidades:
        opcoes.append(valor_atual)  # código antigo, digitado à mão: não some do cadastro
    indice = opcoes.index(valor_atual) if valor_atual else None
    escolhida = st.selectbox(
        rotulo, opcoes, index=indice, key=chave, help=ajuda,
        # Rótulo com a descrição INTEIRA: o Streamlit só pesquisa dentro do rótulo, e
        # a lista já corta a linha sozinha. Assim dá para achar "mediana" mesmo que a
        # palavra esteja no fim da descrição.
        format_func=lambda c: f"{c} · {habilidades[c]}" if c in habilidades else c,
        placeholder="Digite o código ou uma palavra da habilidade",
        accept_new_options=True,  # descritor fora da lista: o professor digita o código
    )
    return (escolhida or "").strip()


def descritores_do_conteudo(cid, c):
    """Descritores (sem repetição, ordenados) usados pelas questões de um
    conteúdo cadastrado pelo professor. Lista vazia se nenhuma
    questão foi mapeada. Usado só no Painel do Professor (Gerenciar
    Conteúdos): é informação de planejamento curricular, sem utilidade pro
    aluno durante o jogo — decisão do Wenes (2026-09-14)."""
    codigos = {str(m.get("descritor", "")).strip() for m in c.get("missoes", [])}
    codigos.discard("")
    return sorted(codigos)


def desempenho_por_descritor(alunos, conteudo_id=None):
    """Agrega o progresso da turma por descritor (só de um conteúdo,
    se conteudo_id for dado: é o caso do PDF exportado de uma aba).

    Retorna [{Habilidade, Questões, Conclusões, Possíveis, % Concluído}], onde
    'Conclusões' conta cada par (aluno, questão concluída) das questões marcadas
    com aquela habilidade, e 'Possíveis' é o total se todos concluíssem tudo.

    Nota sobre o que este número significa: o banco guarda o ponto onde o aluno
    parou na avaliação (missao_atual) e o total de erros por conteúdo — não o acerto
    de cada questão isolada. Então 'concluída' aqui é 'o aluno passou por ela',
    que na mecânica da avaliação só acontece após acertar. Não confundir com
    'acertou de primeira'."""
    acumulado = {}
    for cid in st.session_state.conteudos:
        if conteudo_id and cid != conteudo_id:
            continue
        total_missoes = obter_total_missoes(cid)
        for idx in range(1, total_missoes + 1):
            habilidade = obter_descritor_missao(cid, idx)
            if not habilidade:
                continue
            registro = acumulado.setdefault(habilidade, {"missoes": 0, "feitas": 0, "possiveis": 0})
            registro["missoes"] += 1
            for perfil in alunos.values():
                prog = perfil.get("progresso", {}).get(cid, {"missao_atual": 1})
                concluidas = max(prog.get("missao_atual", 1) - 1, 0)
                registro["possiveis"] += 1
                if idx <= concluidas:
                    registro["feitas"] += 1

    linhas = []
    for habilidade in sorted(acumulado):
        r = acumulado[habilidade]
        pct = (r["feitas"] / r["possiveis"] * 100) if r["possiveis"] else 0
        linhas.append({
            "Habilidade": habilidade,
            "Questões": r["missoes"],
            "Conclusões": r["feitas"],
            "Possíveis": r["possiveis"],
            "% Concluído": round(pct),
        })
    return linhas
