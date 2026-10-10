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
    """
    XP máximo de um conteúdo cadastrado, acertando tudo de primeira (soma o "Pontos (XP)" de cada
    questão). Usado no badge "Total X XP" de cada card (Gerenciar Conteúdos) e no seletor de "Meta
    de XP" em Configurações.
    """
    return sum(m.get("pontos", 10) for m in c.get("missoes", []))


def xp_maximo_catalogo_atual():
    """
    XP máximo de todo o catálogo atual, acertando tudo de primeira. É recalculado a cada chamada,
    então acompanha novos conteúdos. Aparece em Configurações como referência para definir a Meta de
    XP.
    """
    return sum(xp_maximo_de_conteudo(cid, c) for cid, c in st.session_state.conteudos.items())


def obter_total_missoes(conteudo_id):
    conteudo = st.session_state.conteudos.get(conteudo_id, {})
    return len(conteudo.get("missoes", []))
