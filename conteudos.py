"""Leitura e gravação dos conteúdos cadastrados e contas de XP."""

import json
import os
import streamlit as st
from config import ARQUIVO_CONTEUDOS


# ---------- Conteúdos (menu / sumário) ----------
def carregar_conteudos():
    conteudos = {}
    if os.path.exists(ARQUIVO_CONTEUDOS):
        try:
            with open(ARQUIVO_CONTEUDOS, "r", encoding="utf-8") as f:
                conteudos = json.load(f)
        except Exception:
            conteudos = {}
    return conteudos


def salvar_conteudos(conteudos):
    with open(ARQUIVO_CONTEUDOS, "w", encoding="utf-8") as f:
        json.dump(conteudos, f, ensure_ascii=False, indent=2)


def xp_maximo_de_conteudo(cid, c):
    """XP máximo de UM conteúdo específico, acertando tudo de primeira —
    cadastrado pelo professor (soma o "Pontos (XP)" de cada questão dele). Usado tanto pro badge "Total X XP" em cada card
    (Painel do Professor > Gerenciar Conteúdos) quanto pro seletor de
    "Meta de XP" em Configurações — pedido do Wenes (2026-09-17) e sugestão
    parecida do orientador (ver "Conversar com orientador 02.txt": escolher
    a disciplina, mostrar o XP dela, definir a meta como % disso)."""
    return sum(m.get("pontos", 10) for m in c.get("missoes", []))


def xp_maximo_catalogo_atual():
    """XP máximo do catálogo INTEIRO agora, acertando tudo de primeira.
    Recalculado toda vez que é chamado, então cresce sozinho quando o
    professor cadastra conteúdo novo. Mostrado em Configurações como
    referência pra decidir a Meta de XP."""
    return sum(xp_maximo_de_conteudo(cid, c) for cid, c in st.session_state.conteudos.items())


def obter_total_missoes(conteudo_id):
    conteudo = st.session_state.conteudos.get(conteudo_id, {})
    return len(conteudo.get("missoes", []))
