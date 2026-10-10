"""Banco de dados SQLite: alunos, progresso, acessos e consultas."""

import json
import os
import sqlite3
import streamlit as st
import time
from datetime import datetime, timedelta, timezone
from config import ARQUIVO_ALUNOS, ARQUIVO_ALUNOS_DB
from descritores import obter_descritor_missao


# ---------- Banco de alunos (SQLite) ----------
# Trocado de JSON pra SQLite porque, numa aula de verdade, vários alunos respondem questões ao mesmo tempo. O jeito antigo lia o arquivo inteiro, mudava um pedaço e regravava o arquivo inteiro — se dois alunos salvassem quase juntos, o segundo podia sobrescrever e apagar o progresso do primeiro. Com SQLite, cada aluno grava só a própria linha (UPDATE/INSERT pontual), então um não pisa no dado do outro.
def perfil_padrao():
    return {"xp_total": 0, "progresso": {}, "inicio_sessao": time.time()}


def progresso_padrao():
    return {"missao_atual": 1, "erros": 0, "erros_missao_atual": 0, "historico": [], "respostas": {}}


def obter_conexao_db():
    conn = sqlite3.connect(ARQUIVO_ALUNOS_DB, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")     # permite ler e escrever ao mesmo tempo sem travar
    conn.execute("PRAGMA busy_timeout=10000")   # se o banco estiver ocupado, espera até 10s em vez de falhar na hora
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_banco_db():
    conn = obter_conexao_db()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS alunos (
                nome TEXT PRIMARY KEY,
                xp_total INTEGER NOT NULL DEFAULT 0,
                inicio_sessao REAL NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS progresso (
                aluno TEXT NOT NULL,
                conteudo_id TEXT NOT NULL,
                missao_atual INTEGER NOT NULL DEFAULT 1,
                erros INTEGER NOT NULL DEFAULT 0,
                historico TEXT NOT NULL DEFAULT '[]',
                PRIMARY KEY (aluno, conteudo_id)
            )
        """)
        # "erros" (acima) é o total do conteúdo inteiro, usado no relatório do professor. "erros_missao_atual" é zerado a cada vez que o aluno avança de questão — é o que alimenta o desconto de XP por tentativa (ver calcular_xp_por_desempenho): sem separar os dois, não teria como saber quantas vezes o aluno errou NA QUESTÃO ATUAL antes de acertar.
        colunas_progresso = {row["name"] for row in conn.execute("PRAGMA table_info(progresso)")}
        if "erros_missao_atual" not in colunas_progresso:
            conn.execute("ALTER TABLE progresso ADD COLUMN erros_missao_atual INTEGER NOT NULL DEFAULT 0")
        # "respostas" guarda {"1": "8", "2": "61.7", ...} — a resposta que o aluno deu em cada questão já concluída. Faltava desde o começo: só ficava em st.session_state (memória da sessão do navegador), nunca no banco. "missao_atual" sim é salvo, então o aluno reabrindo o app noutra sessão continuava exatamente de onde parou, mas as linhas "✅ Questão N Concluída! (Resposta: ...)" das questões anteriores apareciam com "None" — a sessão nova nunca teve aquele valor em memória.
        if "respostas" not in colunas_progresso:
            conn.execute("ALTER TABLE progresso ADD COLUMN respostas TEXT NOT NULL DEFAULT '{}'")
        # Nome que o professor quer ver NO RELATÓRIO ("João Batista"), separado do "nome" com que o aluno faz login ("Goku99", "Player1"). São coisas diferentes de propósito: "nome" é chave primária e liga o aluno ao progresso dele, então renomear quebraria o vínculo — no próximo login o aluno cairia num perfil vazio e perderia o XP. Esta coluna é só exibição, nunca é usada pra buscar nada.
        colunas_alunos = {row["name"] for row in conn.execute("PRAGMA table_info(alunos)")}
        if "nome_relatorio" not in colunas_alunos:
            conn.execute("ALTER TABLE alunos ADD COLUMN nome_relatorio TEXT NOT NULL DEFAULT ''")
        # Contador de acessos: uma linha por dia com quantas vezes o app foi aberto (cada sessão nova do navegador conta uma vez). Só o número: não guarda IP, aparelho nem quem abriu.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS acessos (
                dia TEXT PRIMARY KEY,
                total INTEGER NOT NULL DEFAULT 0
            )
        """)
        # Uma linha por TENTATIVA de resposta (acerto ou erro). É daqui que sai o "acerto por aluno em cada habilidade" do Painel do Professor: o campo "missao_atual" só diz até onde o aluno chegou, não quanto ele acertou. Só passa a existir a partir da primeira resposta depois desta versão: o histórico antigo não guardava o resultado de cada questão.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tentativas_missao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno TEXT NOT NULL,
                conteudo_id TEXT NOT NULL,
                missao INTEGER NOT NULL,
                acertou INTEGER NOT NULL,
                momento TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tentativas_aluno ON tentativas_missao (aluno)")
        conn.commit()
    finally:
        conn.close()


def dia_de_hoje_brasilia():
    """Data de hoje no horário de Brasília (UTC-3, sem horário de verão). O
    servidor do Fly.io roda em UTC, então date.today() viraria o dia às 21h."""
    return datetime.now(timezone(timedelta(hours=-3))).strftime("%Y-%m-%d")


def registrar_acesso_se_novo():
    """Conta um acesso por sessão do navegador (não a cada clique). Atualizar
    a página (F5) abre sessão nova e conta de novo."""
    if st.session_state.get("_acesso_registrado"):
        return
    st.session_state["_acesso_registrado"] = True
    conn = obter_conexao_db()
    try:
        conn.execute(
            "INSERT INTO acessos (dia, total) VALUES (?, 1) "
            "ON CONFLICT(dia) DO UPDATE SET total = total + 1",
            (dia_de_hoje_brasilia(),),
        )
        conn.commit()
    finally:
        conn.close()


def contar_acessos():
    """Devolve (acessos de hoje, acessos no total)."""
    conn = obter_conexao_db()
    try:
        hoje = conn.execute("SELECT total FROM acessos WHERE dia = ?", (dia_de_hoje_brasilia(),)).fetchone()
        total = conn.execute("SELECT COALESCE(SUM(total), 0) FROM acessos").fetchone()[0]
        return (hoje[0] if hoje else 0), total
    finally:
        conn.close()


def migrar_json_para_sqlite_se_necessario():
    """Importa o banco_alunos.json antigo pro SQLite, uma única vez (se o
    banco novo ainda estiver vazio e o arquivo antigo existir)."""
    if not os.path.exists(ARQUIVO_ALUNOS):
        return
    conn = obter_conexao_db()
    try:
        ja_tem_dados = conn.execute("SELECT COUNT(*) FROM alunos").fetchone()[0] > 0
        if ja_tem_dados:
            return
        try:
            with open(ARQUIVO_ALUNOS, "r", encoding="utf-8") as f:
                dados_antigos = json.load(f)
        except Exception:
            return

        alunos_antigos = dados_antigos.get("alunos", {})
        for nome, perfil in alunos_antigos.items():
            conn.execute(
                "INSERT OR REPLACE INTO alunos (nome, xp_total, inicio_sessao) VALUES (?, ?, ?)",
                (nome, perfil.get("xp_total", 0), perfil.get("inicio_sessao", time.time())),
            )
            for conteudo_id, prog in perfil.get("progresso", {}).items():
                conn.execute(
                    """INSERT OR REPLACE INTO progresso
                       (aluno, conteudo_id, missao_atual, erros, historico)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        nome, conteudo_id,
                        prog.get("missao_atual", 1),
                        prog.get("erros", 0),
                        json.dumps(prog.get("historico", []), ensure_ascii=False),
                    ),
                )
        conn.commit()
        try:
            os.rename(ARQUIVO_ALUNOS, ARQUIVO_ALUNOS + ".migrado_para_sqlite.bak")
        except OSError:
            pass
    finally:
        conn.close()


def carregar_todos_alunos_do_banco():
    """Lê o estado atual de TODOS os alunos direto do banco. Usado no Painel
    do Professor, que precisa ver o progresso da turma inteira em tempo
    real — não só o que a sessão do navegador do professor carregou uma vez."""
    conn = obter_conexao_db()
    try:
        alunos = {}
        for row in conn.execute("SELECT nome, xp_total, inicio_sessao, nome_relatorio FROM alunos"):
            alunos[row["nome"]] = {
                "xp_total": row["xp_total"],
                "inicio_sessao": row["inicio_sessao"],
                "nome_relatorio": row["nome_relatorio"] or "",
                "progresso": {},
            }
        for row in conn.execute("SELECT aluno, conteudo_id, missao_atual, erros, historico, respostas FROM progresso"):
            if row["aluno"] in alunos:
                alunos[row["aluno"]]["progresso"][row["conteudo_id"]] = {
                    "missao_atual": row["missao_atual"],
                    "erros": row["erros"],
                    "historico": json.loads(row["historico"]) if row["historico"] else [],
                    "respostas": json.loads(row["respostas"]) if row["respostas"] else {},
                }
        return alunos
    finally:
        conn.close()


def perfil_atual():
    """Lê o perfil do aluno logado direto do banco (não fica em cache na
    sessão) — assim cada leitura já reflete o que foi salvo por último."""
    nome = st.session_state.aluno_ativo
    if not nome:
        return None
    conn = obter_conexao_db()
    try:
        row = conn.execute("SELECT xp_total, inicio_sessao FROM alunos WHERE nome = ?", (nome,)).fetchone()
        if row is None:
            agora = time.time()
            conn.execute("INSERT INTO alunos (nome, xp_total, inicio_sessao) VALUES (?, 0, ?)", (nome, agora))
            conn.commit()
            return {"xp_total": 0, "inicio_sessao": agora}
        return {"xp_total": row["xp_total"], "inicio_sessao": row["inicio_sessao"]}
    finally:
        conn.close()


def progresso_atual(conteudo_id=None):
    conteudo_id = conteudo_id or st.session_state.conteudo_ativo
    nome = st.session_state.aluno_ativo
    if not nome:
        return progresso_padrao()
    conn = obter_conexao_db()
    try:
        row = conn.execute(
            "SELECT missao_atual, erros, erros_missao_atual, historico, respostas FROM progresso WHERE aluno = ? AND conteudo_id = ?",
            (nome, conteudo_id),
        ).fetchone()
        if row is None:
            return progresso_padrao()
        respostas = json.loads(row["respostas"]) if row["respostas"] else {}
        # Recoloca as respostas salvas em st.session_state: é de lá que todo "✅ Questão N Concluída! (Resposta: ...)" já espalhado pelo código lê o valor (ver verificar_resposta) — sem essa "hidratação" aqui, cada um desses 40+ pontos de exibição precisaria ser reescrito pra ler de outro lugar. Só preenche o que ainda não está em memória (não pisa numa resposta desta MESMA sessão, mais recente que a gravada no banco no meio de uma questão em andamento).
        for idx_str, resp in respostas.items():
            chave = f"m_{conteudo_id}_{idx_str}"
            if chave not in st.session_state:
                st.session_state[chave] = resp
        return {
            "missao_atual": row["missao_atual"],
            "erros": row["erros"],
            "erros_missao_atual": row["erros_missao_atual"],
            "historico": json.loads(row["historico"]) if row["historico"] else [],
            "respostas": respostas,
        }
    finally:
        conn.close()


def salvar_perfil_e_progresso(nome, conteudo_id, perfil, prog):
    """Grava só a linha desse aluno (xp) e só a linha desse aluno+conteúdo
    (progresso) — nunca o banco inteiro. É isso que permite vários alunos
    salvando ao mesmo tempo sem um sobrescrever o outro."""
    conn = obter_conexao_db()
    try:
        conn.execute("UPDATE alunos SET xp_total = ? WHERE nome = ?", (perfil.get("xp_total", 0), nome))
        conn.execute(
            """INSERT INTO progresso (aluno, conteudo_id, missao_atual, erros, erros_missao_atual, historico, respostas)
               VALUES (?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(aluno, conteudo_id) DO UPDATE SET
                   missao_atual = excluded.missao_atual,
                   erros = excluded.erros,
                   erros_missao_atual = excluded.erros_missao_atual,
                   historico = excluded.historico,
                   respostas = excluded.respostas""",
            (
                nome, conteudo_id,
                prog.get("missao_atual", 1),
                prog.get("erros", 0),
                prog.get("erros_missao_atual", 0),
                json.dumps(prog.get("historico", []), ensure_ascii=False),
                json.dumps(prog.get("respostas", {}), ensure_ascii=False),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def carregar_perfil_aluno(nome):
    st.session_state.aluno_ativo = nome
    conn = obter_conexao_db()
    try:
        existe = conn.execute("SELECT 1 FROM alunos WHERE nome = ?", (nome,)).fetchone()
        if not existe:
            conn.execute("INSERT INTO alunos (nome, xp_total, inicio_sessao) VALUES (?, 0, ?)", (nome, time.time()))
            conn.commit()
    finally:
        conn.close()


def limpar_banco():
    conn = obter_conexao_db()
    try:
        conn.execute("DELETE FROM progresso")
        conn.execute("DELETE FROM tentativas_missao")
        conn.execute("DELETE FROM alunos")
        conn.commit()
    finally:
        conn.close()
    st.session_state.aluno_ativo = ""
    st.rerun()


def salvar_nomes_relatorio(mapa_nomes):
    """{nome_de_login: nome_no_relatorio}. Só grava a coluna de exibição —
    a chave 'nome' nunca é tocada, é o que garante que o aluno continue
    encontrando o progresso dele no próximo login."""
    conn = obter_conexao_db()
    try:
        for nome, nome_relatorio in mapa_nomes.items():
            conn.execute("UPDATE alunos SET nome_relatorio = ? WHERE nome = ?",
                         ((nome_relatorio or "").strip(), nome))
        conn.commit()
    finally:
        conn.close()


def excluir_alunos(nomes):
    conn = obter_conexao_db()
    try:
        for nome in nomes:
            conn.execute("DELETE FROM progresso WHERE aluno = ?", (nome,))
            conn.execute("DELETE FROM tentativas_missao WHERE aluno = ?", (nome,))
            conn.execute("DELETE FROM alunos WHERE nome = ?", (nome,))
        conn.commit()
    finally:
        conn.close()
    if st.session_state.aluno_ativo in nomes:
        st.session_state.aluno_ativo = ""
    st.rerun()


def registrar_tentativa_missao(aluno, conteudo_id, missao, acertou):
    """Grava uma tentativa de resposta (acerto ou erro). Falha em silêncio: o
    registro serve só ao relatório do professor, e um erro de banco aqui não
    pode travar o aluno no meio da questão."""
    if not aluno:
        return
    try:
        conn = obter_conexao_db()
        try:
            conn.execute(
                "INSERT INTO tentativas_missao (aluno, conteudo_id, missao, acertou, momento) VALUES (?, ?, ?, ?, ?)",
                (aluno, conteudo_id, int(missao), 1 if acertou else 0, dia_de_hoje_brasilia()),
            )
            conn.commit()
        finally:
            conn.close()
    except sqlite3.Error:
        pass


def acerto_por_aluno_e_habilidade(conteudo_id=None, de="", ate="", sufixo=""):
    """Acerto de cada aluno em cada descritor, a partir das tentativas
    (só as de um conteúdo se conteudo_id for dado), só das tentativas entre as datas
    `de` e `ate` (AAAA-MM-DD, inclusive; vazio = sem limite) e só dos descritores que
    terminam em `sufixo` ("_M" Matemática, "_P" Português; vazio = todos).

    Retorna (acertos, desde): acertos é {(aluno, habilidade): [acertos, questões]}
    e desde é o dia (AAAA-MM-DD) da primeira tentativa gravada, ou '' se não há
    nenhuma. Só a PRIMEIRA tentativa de cada questão conta: acertou de primeira =
    1 acerto; errou, mesmo que depois tenha acertado, = 0. O segundo número é
    quantas questões do descritor o aluno já respondeu. As tentativas seguintes
    são treino e não entram aqui. Só as questões que têm descritor mapeado."""
    acertos = {}
    desde = ""
    try:
        conn = obter_conexao_db()
        try:
            linhas = conn.execute(
                "SELECT aluno, conteudo_id, missao, acertou, momento FROM tentativas_missao ORDER BY id"
            ).fetchall()
        finally:
            conn.close()
    except sqlite3.Error:
        return acertos, desde
    primeiras = set()
    for linha in linhas:
        # A primeira tentativa é decidida antes dos filtros: se o filtro de período cortasse a primeira, as seguintes não podem passar por primeira.
        chave = (linha["aluno"], linha["conteudo_id"], linha["missao"])
        if chave in primeiras:
            continue
        primeiras.add(chave)
        if conteudo_id and linha["conteudo_id"] != conteudo_id:
            continue
        if (de and linha["momento"][:10] < de) or (ate and linha["momento"][:10] > ate):
            continue
        if not desde or linha["momento"] < desde:
            desde = linha["momento"]
        habilidade = obter_descritor_missao(linha["conteudo_id"], linha["missao"])
        if not habilidade or (sufixo and not habilidade.endswith(sufixo)):
            continue
        par = acertos.setdefault((linha["aluno"], habilidade), [0, 0])
        par[0] += linha["acertou"]
        par[1] += 1
    return acertos, desde


def erros_da_questao(aluno, conteudo_id, missao):
    """Quantas vezes o aluno errou ESTA questão até agora. Como as questões podem ser
    respondidas em qualquer ordem, o desconto de XP por erro sai daqui, e não de um
    contador da 'questão atual'."""
    try:
        conn = obter_conexao_db()
        try:
            return conn.execute(
                "SELECT COUNT(*) FROM tentativas_missao WHERE aluno = ? AND conteudo_id = ? AND missao = ? AND acertou = 0",
                (aluno, conteudo_id, int(missao)),
            ).fetchone()[0]
        finally:
            conn.close()
    except sqlite3.Error:
        return 0


def ranking_turma(limite=10):
    """[(apelido, xp)] dos alunos com mais XP, em ordem decrescente.

    Consulta enxuta de propósito: só nome e xp_total, ordenado e limitado pelo
    próprio SQLite. O placar recarrega sozinho a cada poucos segundos no
    navegador de cada aluno (ver render_placar_turma), então ele roda muito mais
    vezes que o resto do app — não pode carregar o progresso da turma inteira
    como carregar_todos_alunos_do_banco() faz."""
    conn = obter_conexao_db()
    try:
        return [
            (linha["nome"], linha["xp_total"])
            for linha in conn.execute(
                "SELECT nome, xp_total FROM alunos ORDER BY xp_total DESC, nome ASC LIMIT ?",
                (limite,),
            )
        ]
    finally:
        conn.close()


def progresso_resumo_aluno():
    """{conteudo_id: missoes_concluidas} do aluno logado, em UMA consulta.
    O menu lateral mostra o progresso de todas as matérias ao mesmo tempo;
    chamar progresso_atual() uma vez por matéria abriria (e fecharia) uma
    conexão pra cada uma, a cada rerun — e a Avaliação faz rerun a
    cada resposta respondida."""
    nome = st.session_state.aluno_ativo
    if not nome:
        return {}
    conn = obter_conexao_db()
    try:
        linhas = conn.execute(
            "SELECT conteudo_id, missao_atual FROM progresso WHERE aluno = ?", (nome,)
        ).fetchall()
    finally:
        conn.close()
    # missao_atual aponta pra PRÓXIMA questão a responder (começa em 1), então o que já foi concluído é sempre missao_atual - 1.
    return {linha["conteudo_id"]: max(linha["missao_atual"] - 1, 0) for linha in linhas}
