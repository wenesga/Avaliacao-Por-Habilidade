"""Descritores SAETO (ex.: D044_M): lista, descrições e desempenho por descritor."""

import json
import os
import streamlit as st
from config import ARQUIVO_DESCRITORES_SAETO
from conteudos import obter_total_missoes


def descritores_da_missao(missao):
    """
    Códigos de descritor SAETO de uma questão, sem repetição e na ordem cadastrada (lista vazia
    se não mapeada). Lê a lista "descritores"; se ela não existir, lê o campo "descritor", que
    guarda um código só.
    """
    bruto = missao.get("descritores")
    if bruto is None:
        bruto = [missao.get("descritor", "")]
    codigos = []
    for codigo in bruto:
        codigo = str(codigo).strip()
        if codigo and codigo not in codigos:
            codigos.append(codigo)
    return codigos


def obter_descritores_missao(conteudo_id, indice_missao):
    """Descritores SAETO de uma questão (lista vazia se não mapeada).
    indice_missao é 1-based, igual ao usado em progresso['missao_atual']."""
    missoes = st.session_state.conteudos.get(conteudo_id, {}).get("missoes", [])
    if 1 <= indice_missao <= len(missoes):
        return descritores_da_missao(missoes[indice_missao - 1])
    return []


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


def campo_descritores(rotulo, valores_atuais=(), chave=None, ajuda="", maximo=None):
    """Campo de descritores SAETO: seleção pesquisável (código + descrição) quando o banco
    existe; texto livre, com códigos separados por vírgula, quando não. `maximo` limita quantos
    podem ser escolhidos na seleção. Devolve a lista de códigos."""
    habilidades = carregar_descritores()
    atuais = [str(v).strip() for v in valores_atuais if str(v).strip()]
    if not habilidades:
        texto = st.text_input(
            rotulo, value=", ".join(atuais), placeholder="Ex.: D044_M, D035_M", key=chave, help=ajuda,
        )
        return [c.strip() for c in texto.split(",") if c.strip()]
    opcoes = sorted(habilidades)
    opcoes += [c for c in atuais if c not in habilidades]  # código digitado à mão: não some do cadastro
    escolhidos = st.multiselect(
        rotulo, opcoes, default=atuais, key=chave, help=ajuda, max_selections=maximo,
        # Rótulo com a descrição inteira, pois o Streamlit só pesquisa dentro do rótulo.
        format_func=lambda c: f"{c} · {habilidades[c]}" if c in habilidades else c,
        placeholder="Digite o código ou uma palavra da habilidade",
        accept_new_options=True,  # descritor fora da lista: o professor digita o código
    )
    return [c.strip() for c in escolhidos if c.strip()]


def descritores_do_conteudo(cid, c):
    """
    Descritores (sem repetição, ordenados) usados pelas questões de um conteúdo cadastrado. Lista
    vazia se nenhuma questão foi mapeada. Usado só no Painel do Professor (planejamento curricular).
    """
    codigos = set()
    for m in c.get("missoes", []):
        codigos.update(descritores_da_missao(m))
    return sorted(codigos)


def desempenho_por_descritor(alunos, conteudo_id=None):
    """
    Agrega o progresso da turma por descritor (de um conteúdo, se conteudo_id for dado).

    Retorna [{Habilidade, Questões, Conclusões, Possíveis, % Concluído}]: 'Conclusões' conta cada
    par (aluno, questão concluída) das questões com aquele descritor, e 'Possíveis' é o total se
    todos concluíssem tudo.

    O banco guarda onde o aluno parou (missao_atual) e o total de erros, não o acerto de cada
    questão. 'Concluída' significa 'o aluno passou por ela', o que só ocorre após acertar; não
    equivale a 'acertou de primeira'.
    """
    acumulado = {}
    for cid in st.session_state.conteudos:
        if conteudo_id and cid != conteudo_id:
            continue
        total_missoes = obter_total_missoes(cid)
        for idx in range(1, total_missoes + 1):
            for habilidade in obter_descritores_missao(cid, idx):
                registro = acumulado.setdefault(habilidade, {"missoes": 0, "feitas": 0, "possiveis": 0})
                registro["missoes"] += 1
                for perfil in alunos.values():
                    prog = perfil.get("progresso", {}).get(cid, {})
                    respostas = prog.get("respostas")
                    if respostas is not None:
                        feita = str(idx) in respostas
                    else:  # registro antigo, sem a lista de respostas: vale a ordem
                        feita = idx <= max(prog.get("missao_atual", 1) - 1, 0)
                    registro["possiveis"] += 1
                    if feita:
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
