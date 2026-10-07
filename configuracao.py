"""Configurações gerais (senha do professor etc.)."""

import hashlib
import json
import os
from config import ARQUIVO_CONFIG, SENHA_PADRAO_PROFESSOR


# ---------- Configurações / Senha do professor ----------
def carregar_config():
    if os.path.exists(ARQUIVO_CONFIG):
        try:
            with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"senha_hash": hashlib.sha256(SENHA_PADRAO_PROFESSOR.encode()).hexdigest()}


def salvar_config(config):
    with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False)


def senha_correta(digitada, config):
    if not digitada:
        return False
    return hashlib.sha256(digitada.encode()).hexdigest() == config.get("senha_hash", "")
