"""As 4 faixas de desempenho da escola (modelo SAEB/SAETO) e as cores de cada uma."""

# (nome, limite superior em %, cor forte, fundo suave da célula, bolinha da legenda). Até 40% Baixo, 41–60% Médio baixo, 61–79% Médio alto, 80% ou mais Alto. O PDF do SAETO chama de "Médio alto" um descritor com 80% em uma tabela, mas a legenda da primeira página diz que 80% ou mais é "Alto": aqui vale a legenda.
FAIXAS = [
    ("Baixo",       40,  "#e74c3c", "#f6c9c4", "🔴"),
    ("Médio baixo", 60,  "#e67e22", "#fbd9b5", "🟠"),
    ("Médio alto",  79,  "#f1c40f", "#fbefb5", "🟡"),
    ("Alto",        100, "#2ecc71", "#c9f0d6", "🟢"),
]
CORES_DESEMPENHO = [f[2] for f in FAIXAS]

LEGENDA_FAIXAS = "  ·  ".join(
    f"{bolinha} {nome} ({'até 40%' if i == 0 else f'{FAIXAS[i - 1][1] + 1}–{limite}%' if i < 3 else f'{FAIXAS[i - 1][1] + 1}% ou mais'})"
    for i, (nome, limite, _, _, bolinha) in enumerate(FAIXAS)
)


def faixa_do_percentual(percentual):
    """Posição (0 a 3) da faixa em FAIXAS. O percentual é arredondado para inteiro,
    como aparece na tela: 40,4% conta como 40% (Baixo)."""
    p = round(percentual)
    for i, (_, limite, _, _, _) in enumerate(FAIXAS):
        if p <= limite:
            return i
    return len(FAIXAS) - 1


def nome_da_faixa(percentual):
    return FAIXAS[faixa_do_percentual(percentual)][0]


def cor_por_percentual_concluido(percentual):
    """Cor forte da faixa (para barras e gráficos)."""
    return FAIXAS[faixa_do_percentual(percentual)][2]


def fundo_acerto(percentual):
    """Fundo suave da célula na cor da faixa, com texto escuro para ler bem nos dois temas."""
    return f"background-color: {FAIXAS[faixa_do_percentual(percentual)][3]}; color: #1f2937"


def percentual_acerto(par):
    """Porcentagem de acerto de um [acertos, tentativas], ou None se não houve tentativa."""
    if not par or not par[1]:
        return None
    return round(par[0] / par[1] * 100)


def texto_acerto(par):
    """Texto da célula: '62% (24/39)', ou '—' sem tentativa."""
    pct = percentual_acerto(par)
    return "—" if pct is None else f"{pct}% ({par[0]}/{par[1]})"
