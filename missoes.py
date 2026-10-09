"""Verificação de respostas e tela de questões."""

import streamlit as st
from banco import erros_da_questao, perfil_atual, progresso_atual, registrar_tentativa_missao, salvar_perfil_e_progresso
from config import DESCONTO_XP_POR_ERRO, PISO_XP_FRACAO


def calcular_xp_por_desempenho(pontos_base, erros_nesta_missao):
    """XP realmente concedido por uma questão, considerando quantas vezes o
    aluno errou ELA (não o conteúdo inteiro) antes de acertar.

    É proporcional ao XP que o professor configurou, então funciona igual pra
    questão de 10, de 20 ou de 100 pontos. Com XP muito baixo (1 ou 2), o
    desconto pode não aparecer por causa do arredondamento — o piso de "ganha
    pelo menos 1" prevalece. Aceito como caso raro: professor dificilmente
    configura XP tão baixo a ponto de a diferença sumir."""
    fracao = max(1 - erros_nesta_missao * DESCONTO_XP_POR_ERRO, PISO_XP_FRACAO)
    return max(round(pontos_base * fracao), 1)


def verificar_resposta(conteudo_id, missao_id, resposta_aluno, resposta_certa, pontos, tipo="numero"):
    # Rótulo curto: o cabeçalho "### 📍 Questão N: ..." logo acima já diz qual
    # questão é — repetir "da Questão N" no botão era informação redundante
    # (mesmo padrão de simplificação pedido pelo Wenes em 2026-09-14 pros
    # botões do Painel do Professor, aplicado aqui porque este é o botão de
    # questão que aparece em TODO conteúdo do app, nativo ou cadastrado).
    if st.button("Verificar Resposta", key=f"btn_{conteudo_id}_{missao_id}"):
        if resposta_aluno is None or str(resposta_aluno).strip() == "":
            st.error("⚠️ Escolha uma alternativa antes de verificar!" if tipo == "multipla"
                     else "⚠️ Digite um valor antes de verificar!")
            return

        acertou = False
        if tipo == "multipla":
            # Comparação exata: o aluno não digita nada, apenas escolhe uma das
            # alternativas cadastradas, então os dois lados vêm do mesmo texto.
            # É justamente isso que a múltipla escolha resolve — em resposta
            # digitada, "media" e "média" são strings diferentes e o aluno perde
            # o ponto por causa do acento, não por causa do conteúdo.
            acertou = str(resposta_aluno).strip() == str(resposta_certa).strip()
        elif tipo == "numero":
            try:
                acertou = abs(float(resposta_aluno) - float(resposta_certa)) < 0.1
            except (ValueError, TypeError):
                acertou = False
        elif tipo == "texto":
            resp_txt, certa_txt = str(resposta_aluno).strip().lower(), str(resposta_certa).strip().lower()
            if resp_txt == certa_txt:
                acertou = True
            else:
                try:
                    if abs(float(resp_txt.replace(",", ".")) - float(certa_txt.replace(",", "."))) < 0.1:
                        acertou = True
                except Exception:
                    pass

        perfil = perfil_atual()
        prog = progresso_atual(conteudo_id)

        nome_aluno = st.session_state.aluno_ativo
        if str(missao_id) in prog.get("respostas", {}):
            return  # questão já concluída: não conta de novo
        registrar_tentativa_missao(nome_aluno, conteudo_id, missao_id, acertou)

        if acertou:
            erros_desta_missao = erros_da_questao(nome_aluno, conteudo_id, missao_id)
            xp_ganho = calcular_xp_por_desempenho(pontos, erros_desta_missao)
            if erros_desta_missao > 0:
                mensagem = f"🎉 Correto! +{xp_ganho} XP de {pontos} XP (descontado pelas tentativas)"
            else:
                mensagem = f"🎉 Correto! +{xp_ganho} XP!"
            # Guardado em session_state em vez de um st.success() mostrado
            # aqui na hora: o st.rerun() logo abaixo troca a tela quase
            # instantaneamente, e a mensagem só ficava visível por uma fração
            # de segundo — sem tempo de leitura nenhum (relatado pelo Wenes,
            # 2026-09-14: não dava tempo de ler nem tirando
            # print). Quem desenha esse texto na tela, de forma PERSISTENTE
            # (sem sumir sozinha), é renderizar_ultimo_resultado(), chamada
            # embaixo de tudo na aba Questões (perto de onde o aluno clicou).
            st.session_state[f"ultimo_resultado_{conteudo_id}"] = mensagem
            perfil["xp_total"] = perfil.get("xp_total", 0) + xp_ganho
            prog["historico"].append(f"✅ Questão {missao_id} concluída. Resposta: `{resposta_aluno}` (+{xp_ganho} XP)")
            st.session_state[f"m_{conteudo_id}_{missao_id}"] = resposta_aluno
            # Guarda TAMBÉM no banco (prog["respostas"], persistido por
            # salvar_perfil_e_progresso): o session_state acima é só desta
            # aba do navegador, some numa sessão nova. Sem isso, quem volta
            # depois via outra sessão via as questões já feitas mostrando
            # "(Resposta: None)" — bug relatado pelo Wenes (2026-09-14).
            prog.setdefault("respostas", {})[str(missao_id)] = resposta_aluno
            # missao_atual = questões concluídas + 1: é o número que o resto do sistema
            # usa para contar progresso, e agora não depende mais da ordem das questões.
            prog["missao_atual"] = len(prog["respostas"]) + 1
            st.session_state[f"ultima_questao_{conteudo_id}"] = missao_id
            salvar_perfil_e_progresso(nome_aluno, conteudo_id, perfil, prog)
            st.rerun()
        else:
            prog["erros"] = prog.get("erros", 0) + 1
            salvar_perfil_e_progresso(nome_aluno, conteudo_id, perfil, prog)
            # Limpa o "🎉 Correto!" da questão anterior: sem isso, ele ficava
            # em session_state pra sempre (só é sobrescrito num ACERTO) e
            # aparecia junto do "❌ Resposta incorreta" da tentativa atual —
            # as duas mensagens empilhadas, tumultuado (relatado pelo Wenes,
            # 2026-09-14). Errar tem que apagar o acerto de antes, não só
            # somar mais uma mensagem em cima.
            st.session_state.pop(f"ultimo_resultado_{conteudo_id}", None)
            st.error("❌ Resposta incorreta. Revise o conteúdo e tente de novo!")


def render_missoes_dinamicas(conteudo):
    """Todas as questões ficam visíveis, e o aluno responde na ordem que quiser.
    A questão já concluída vira uma linha verde com a resposta; a que falta mostra
    o enunciado e o botão. O XP ganho aparece na linha da questão que acabou de ser feita."""
    cid = st.session_state.conteudo_ativo
    missoes = conteudo.get("missoes", [])
    prog = progresso_atual(cid)
    respostas = prog.get("respostas", {})

    if not missoes:
        st.info("📭 Este conteúdo ainda não possui questões cadastradas. Peça ao professor para adicioná-las no Painel do Professor.")
        return

    ultima = st.session_state.get(f"ultima_questao_{cid}")
    mensagem = st.session_state.get(f"ultimo_resultado_{cid}")
    for idx, missao in enumerate(missoes, start=1):
        if str(idx) in respostas:
            texto = f"✅ Questão {idx} Concluída! (Resposta: {respostas[str(idx)]})"
            if ultima == idx and mensagem:
                texto += "  \n" + mensagem
            st.success(texto)
        else:
            st.markdown(f"### 📍 Questão {idx}: {missao.get('titulo', f'Desafio {idx}')}")
            st.write(missao.get("pergunta", ""))
            tipo = missao.get("tipo", "numero")
            if tipo == "multipla":
                # index=None deixa a questão começar SEM alternativa marcada. Com a
                # primeira já selecionada, o aluno poderia clicar em "Verificar"
                # sem ter escolhido nada e levar um erro que não foi escolha dele.
                resposta = st.radio(
                    "Escolha uma alternativa:", missao.get("alternativas", []),
                    index=None, key=f"in_{cid}_{idx}",
                )
            elif tipo == "numero":
                resposta = st.number_input("Sua resposta:", step=0.1, value=None, key=f"in_{cid}_{idx}")
            else:
                resposta = st.text_input("Sua resposta:", key=f"in_{cid}_{idx}")
            verificar_resposta(cid, idx, resposta, missao.get("resposta"), missao.get("pontos", 10), tipo=tipo)

    if len(respostas) >= len(missoes):
        st.balloons()
        st.success("🏆 PARABÉNS! Você concluiu todas as questões desta disciplina!")
