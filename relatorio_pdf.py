"""Geração do relatório em PDF."""

from fpdf import FPDF
from PIL import Image
import os
import re
import streamlit as st
import unicodedata
from datetime import date
from config import ARQUIVO_CABECALHO
from faixas import cor_por_percentual_concluido, fundo_acerto, percentual_acerto, texto_acerto


def hex_para_rgb(cor_hex):
    """'#2ecc71' -> (46, 204, 113). fpdf2 quer três inteiros pro set_fill_color,
    não aceita hex direto como o Altair/CSS aceitam."""
    cor_hex = cor_hex.lstrip("#")
    return tuple(int(cor_hex[i:i + 2], 16) for i in (0, 2, 4))


class _PDFComCabecalho(FPDF):
    """FPDF que desenha o timbre institucional (ARQUIVO_CABECALHO) só no topo
    da PRIMEIRA página do relatório (decisão do Wenes, 2026-09-20: as demais
    páginas ficam com o espaço todo para tabelas e gráficos).

    Continua sendo via header() e não um pdf.image() solto depois do
    add_page(): assim a primeira página sempre leva o timbre, e o fpdf2 cuida
    de não desenhá-lo nas páginas seguintes, inclusive nas criadas pela
    quebra automática de página.

    Se o arquivo não existir, o relatório sai sem timbre e nada quebra —
    mesma lógica de fallback do logo.png/banner.png na tela."""

    def header(self):
        if self.page_no() != 1 or not os.path.exists(ARQUIVO_CABECALHO):
            return
        largura = self.w - self.l_margin - self.r_margin
        self.image(ARQUIVO_CABECALHO, x=self.l_margin, y=10, w=largura)
        # pdf.image() não move o cursor no fpdf2, então o Y de onde o conteúdo
        # começa tem que ser calculado: a altura vem da proporção real do
        # arquivo (lida com PIL, não chutada — trocar a arte por uma de outra
        # proporção continua funcionando sem mexer no código).
        with Image.open(ARQUIVO_CABECALHO) as img:
            altura = largura * img.height / img.width
        self.set_y(10 + altura + 6)


def _texto_que_cabe(pdf, texto, largura_celula, folga=2):
    """Encurta o texto com '...' até caber na célula.

    pdf.cell() não quebra linha nem corta: texto maior que a largura vaza por
    cima da célula vizinha. Foi o que aconteceu no teste com o login
    'VingadorDoFuturo3' invadindo a coluna do nome completo ao lado. Login e
    nome no relatório são digitados livremente pelo aluno e pelo professor, então
    não dá pra confiar em limite fixo de caracteres — aqui a medida é em mm, na
    fonte que está ativa no momento da chamada."""
    texto = str(texto)
    limite = largura_celula - folga
    if pdf.get_string_width(texto) <= limite:
        return texto
    while texto and pdf.get_string_width(texto + "...") > limite:
        texto = texto[:-1]
    return texto + "..." if texto else ""


MESES_PT = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]


def formatar_data_relatorio(cidade=""):
    """Data de hoje por extenso (ex.: 'Arraias - TO, 07 de setembro de 2026').

    Calculada fora da função cacheada (gerar_pdf_relatorio) e passada como
    argumento: assim ela entra na chave do @st.cache_data, e o cache se
    renova sozinho quando o dia muda, sem precisar excluir a função do cache."""
    hoje = date.today()
    texto = f"{hoje.day:02d} de {MESES_PT[hoje.month - 1]} de {hoje.year}"
    return f"{cidade}, {texto}" if cidade else texto


LARGURA_ROTULO_CABECALHO_PDF = 32  # mm — cabe "Professor(a):" em negrito 10pt


def _linha_dado_pdf(pdf, rotulo, valor):
    """Uma linha 'Rótulo: valor' alinhada à esquerda — rótulo em negrito com
    largura fixa, pra várias linhas seguidas alinharem o valor na mesma
    coluna (padrão que o Wenes já usa nos documentos curtos de outras
    disciplinas: Acadêmico / Curso / Disciplina / Professor / Data)."""
    pdf.set_font("CMU", 'B', 10)
    pdf.cell(LARGURA_ROTULO_CABECALHO_PDF, 6, text=f"{rotulo}:", align='L')
    pdf.set_font("CMU", '', 10)
    pdf.cell(0, 6, text=valor, align='L', new_x="LMARGIN", new_y="NEXT")


ALTURA_TITULO_GRAFICO_PDF = 10   # título (8mm) + respiro (2mm)


ALTURA_LINHA_GRAFICO_PDF = 7


MINIMO_BARRAS_POR_PAGINA = 3     # nunca deixa 1 ou 2 barras soltas numa página


def _grafico_barras_pdf(pdf, titulo, itens, x_tabela, largura_tabela):
    """Gráfico de barras horizontais (uma por aluno), desenhado à mão com rect().

    itens: lista de (rótulo, fração 0-1 da barra, texto do valor, cor hex).

    Regras de página (pedido do Wenes, 2026-09-20):
    - cabe no espaço que sobrou na página: fica onde está;
    - não cabe: começa numa página nova, e o gráfico ocupa só a(s) página(s)
      dele (quem chamou deve abrir outra página antes do próximo conteúdo);
    - passa de uma página (turma grande): quebra sem deixar barra solta
      (mínimo de MINIMO_BARRAS_POR_PAGINA por página) e repete o título com
      "(continuação)".
    Retorna True se o gráfico usou páginas próprias, False se coube no lugar."""
    largura_rotulo, largura_valor = 35, 15
    largura_barra_max = largura_tabela - largura_rotulo - largura_valor
    x_inicio_barra = x_tabela + largura_rotulo
    fundo = pdf.h - pdf.b_margin

    def cabecalho(texto):
        pdf.set_font("CMU", 'B', 13)
        pdf.set_x(x_tabela)
        pdf.cell(largura_tabela, 8, text=texto, align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        pdf.set_font("CMU", '', 10)

    def desenhar(bloco):
        for rotulo, fracao, texto_valor, cor in bloco:
            y_linha = pdf.get_y()
            pdf.set_x(x_tabela)
            pdf.cell(largura_rotulo, ALTURA_LINHA_GRAFICO_PDF, text=_texto_que_cabe(pdf, rotulo, largura_rotulo))
            largura_barra = fracao * largura_barra_max
            if largura_barra > 0:
                pdf.set_fill_color(*hex_para_rgb(cor))
                pdf.rect(x_inicio_barra, y_linha + 1, largura_barra, 5, style='F')
            pdf.set_xy(x_inicio_barra + largura_barra_max, y_linha)
            pdf.cell(largura_valor, ALTURA_LINHA_GRAFICO_PDF, text=texto_valor, align='R', new_x="LMARGIN", new_y="NEXT")

    altura_total = ALTURA_TITULO_GRAFICO_PDF + len(itens) * ALTURA_LINHA_GRAFICO_PDF
    if pdf.get_y() + altura_total <= fundo:
        cabecalho(titulo)
        desenhar(itens)
        return False

    pdf.add_page()
    capacidade = int((fundo - pdf.get_y() - ALTURA_TITULO_GRAFICO_PDF) // ALTURA_LINHA_GRAFICO_PDF)
    tamanhos = []
    restante = len(itens)
    while restante > 0:
        tamanhos.append(min(capacidade, restante))
        restante -= tamanhos[-1]
    if len(tamanhos) > 1 and tamanhos[-1] < MINIMO_BARRAS_POR_PAGINA:
        falta = MINIMO_BARRAS_POR_PAGINA - tamanhos[-1]
        tamanhos[-2] -= falta
        tamanhos[-1] += falta
    inicio = 0
    for i, n in enumerate(tamanhos):
        if i > 0:
            pdf.add_page()
        cabecalho(titulo if i == 0 else f"{titulo} (continuação)")
        desenhar(itens[inicio:inicio + n])
        inicio += n
    return True


@st.cache_data
def nome_de_arquivo(texto):
    """'Estatística Descritiva' -> 'estatistica_descritiva' (sem acento nem símbolo)."""
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", sem_acento.lower()).strip("_") or "conteudo"


def gerar_pdf_relatorio(lista_geral, conteudo_titulo, linhas_conteudo, nome_instituicao="", nome_professor="", turma="", data_relatorio="", linhas_descritor=None, acerto=None):
    """Gera o PDF com margens laterais simétricas, título centralizado e as
    duas tabelas: Desempenho da Turma + Detalhamento do conteúdo que estava em tela.

    Cacheado com @st.cache_data: o st.tabs() do Streamlit renderiza TODAS as
    abas por trás mesmo com só uma visível, então sem cache esse PDF (com
    fonte embutida, nada barato de gerar) era recalculado do zero pra cada
    um dos 5 conteúdos a cada clique na página — mesmo sem nada ter mudado.
    Com o cache, só recalcula quando os argumentos (dados do aluno, nome da
    instituição/professor) realmente mudam entre uma chamada e outra.

    Fonte: CMU Serif (Computer Modern Unicode) embutida via TTF em vez da Arial
    padrão do fpdf2 — visual de documento LaTeX/acadêmico. Os arquivos ficam em
    fonts/ (licença OFL, ver fonts/OFL.txt); precisam ser embutidos porque o
    fpdf2 não vem com essa fonte, e "CMU" não existe nos leitores de PDF por
    padrão. Negrito fica só no título, subtítulos e cabeçalho das tabelas —
    linhas de dado ficam em peso normal, de propósito."""
    pdf = _PDFComCabecalho()
    pdf.add_font("CMU", "", "fonts/CMUSerif-Roman.ttf")
    pdf.add_font("CMU", "B", "fonts/CMUSerif-Bold.ttf")
    pdf.set_margins(left=20, top=20, right=20)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    largura_util = pdf.w - pdf.l_margin - pdf.r_margin  # 170mm em A4 com margens de 20mm

    # --- Dados do relatório (Instituição/Professor/Turma opcionais, Data sempre) ---
    # Rótulo em negrito + dois pontos, alinhado à esquerda (pedido do Wenes,
    # 2026-09-07) — é o padrão que ele já usa em documentos curtos de outras
    # disciplinas. Substituiu o bloco centralizado que tinha antes.
    if nome_instituicao:
        _linha_dado_pdf(pdf, "Instituição", nome_instituicao)
    if nome_professor:
        _linha_dado_pdf(pdf, "Professor(a)", nome_professor)
    if turma:
        _linha_dado_pdf(pdf, "Turma", turma)
    _linha_dado_pdf(pdf, "Conteúdo", conteudo_titulo)  # o PDF sai de uma aba e fala só dela
    _linha_dado_pdf(pdf, "Data", data_relatorio)
    pdf.ln(3)

    # --- Título centralizado ---
    pdf.set_font("CMU", 'B', 16)
    pdf.cell(largura_util, 10, text="Relatório de Desempenho - Avaliação por Habilidade", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # --- Tabela 1: Desempenho da turma ---
    # Tabelas mais estreitas que a largura útil e centralizadas na página (em
    # vez de esticadas de margem a margem) — fica com cara de tabela de
    # relatório/artigo, não de planilha crua. pdf.cell() com new_x="LMARGIN"
    # sempre volta pra margem esquerda da página no fim da linha, então cada
    # linha precisa reposicionar o X pro início da tabela centralizada de novo.
    # A coluna "Nome no Relatório" só entra se ALGUÉM tiver preenchido: professor
    # que não usa o recurso continua recebendo o PDF de 3 colunas de sempre, sem
    # uma coluna vazia ocupando espaço. Quem preencheu só metade da turma recebe
    # as células dos outros em branco, de propósito — dá pra completar à caneta
    # depois de imprimir. As larguras abaixo somam os MESMOS 150mm nos dois
    # casos: o espaço da coluna nova sai da folga das colunas numéricas (45mm
    # pra escrever "175" era exagero), não das margens, que ficam intocadas.
    usar_nome_relatorio = any(str(l.get("Nome no Relatório", "")).strip() for l in lista_geral)

    # COM a coluna de nome a tabela ocupa a largura útil inteira (170mm, ou seja,
    # exatamente de margem a margem) — os 20mm que sobravam de cada lado vão
    # todos pra coluna do nome, que passa de 52 pra 72mm e para de cortar nome
    # completo. SEM a coluna de nome ficam os 150mm centralizados de sempre: com
    # 3 colunas curtas, esticar de margem a margem deixaria a tabela com cara de
    # planilha esticada, e aí a folga é proposital (ver comentário abaixo).
    largura_tabela1 = largura_util if usar_nome_relatorio else 150  # 38+72+30+30 | 60+45+45
    x_tabela1 = pdf.l_margin + (largura_util - largura_tabela1) / 2
    pdf.set_font("CMU", 'B', 13)
    pdf.set_x(x_tabela1)
    pdf.cell(largura_tabela1, 8, text="Desempenho da Turma", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("CMU", 'B', 11)
    pdf.set_x(x_tabela1)
    if usar_nome_relatorio:
        pdf.cell(38, 9, text="Login", border=1, align='C')
        pdf.cell(72, 9, text="Aluno", border=1, align='C')
        pdf.cell(30, 9, text="XP Total", border=1, align='C')
        pdf.cell(30, 9, text="Erros", border=1, align='C', new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(60, 9, text="Aluno", border=1, align='C')
        pdf.cell(45, 9, text="XP Total", border=1, align='C')
        pdf.cell(45, 9, text="Erros Totais", border=1, align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("CMU", '', 11)
    for linha in lista_geral:
        pdf.set_x(x_tabela1)
        if usar_nome_relatorio:
            pdf.cell(38, 9, text=_texto_que_cabe(pdf, linha["Aluno"], 38), border=1, align='C')
            pdf.cell(72, 9, text=_texto_que_cabe(pdf, str(linha.get("Nome no Relatório", "")).strip(), 72), border=1, align='C')
            pdf.cell(30, 9, text=str(linha["XP Total"]), border=1, align='C')
            pdf.cell(30, 9, text=str(linha["Erros Totais"]), border=1, align='C', new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.cell(60, 9, text=_texto_que_cabe(pdf, linha["Aluno"], 60), border=1, align='C')
            pdf.cell(45, 9, text=str(linha["XP Total"]), border=1, align='C')
            pdf.cell(45, 9, text=str(linha["Erros Totais"]), border=1, align='C', new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)

    # --- Gráfico de barras: XP por aluno (ver _grafico_barras_pdf: regras de página) ---
    grafico_xp_isolado = False
    if lista_geral:
        maior_xp = max((linha["XP Total"] for linha in lista_geral), default=0) or 1
        itens_xp = [(l["Aluno"], l["XP Total"] / maior_xp, str(l["XP Total"]), l.get("Cor", "#ff4b4b")) for l in lista_geral]
        grafico_xp_isolado = _grafico_barras_pdf(pdf, "Gráfico de XP por Aluno", itens_xp, x_tabela1, largura_tabela1)

    # --- Tabela de habilidades (só se houver questão mapeada) ---
    # Fica logo depois do Desempenho da Turma, ainda na primeira página quando
    # cabe: é a tabela que responde "o que a turma aprendeu", enquanto as outras
    # respondem "quanto cada aluno fez".
    if linhas_descritor:
        if grafico_xp_isolado:
            pdf.add_page()
        else:
            pdf.ln(6)
        largura_descritor = 150  # 45 + 25 + 40 + 40
        x_descritor = pdf.l_margin + (largura_util - largura_descritor) / 2
        pdf.set_font("CMU", 'B', 13)
        pdf.set_x(x_descritor)
        pdf.cell(largura_descritor, 8, text="Desempenho por Habilidade", align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("CMU", 'B', 11)
        pdf.set_x(x_descritor)
        pdf.cell(45, 9, text="Habilidade", border=1, align='C')
        pdf.cell(25, 9, text="Questões", border=1, align='C')
        pdf.cell(40, 9, text="Conclusões", border=1, align='C')
        pdf.cell(40, 9, text="% Concluído", border=1, align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("CMU", '', 11)
        for linha in linhas_descritor:
            pdf.set_x(x_descritor)
            pdf.cell(45, 9, text=_texto_que_cabe(pdf, linha["Habilidade"], 45), border=1, align='C')
            pdf.cell(25, 9, text=str(linha["Questões"]), border=1, align='C')
            pdf.cell(40, 9, text=f'{linha["Conclusões"]}/{linha["Possíveis"]}', border=1, align='C')
            pdf.cell(40, 9, text=f'{linha["% Concluído"]}%', border=1, align='C', new_x="LMARGIN", new_y="NEXT")

    # --- Acerto por aluno em cada habilidade (igual à tabela da Visão Geral) ---
    # Em blocos de 5 habilidades por tabela, pra caber na largura da página.
    if acerto and acerto[0]:
        habilidades_ac, linhas_ac = acerto
        pdf.add_page()
        pdf.set_font("CMU", 'B', 13)
        pdf.cell(largura_util, 8, text="Acerto por Habilidade", align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("CMU", '', 10)
        pdf.cell(largura_util, 6, text="Entre parênteses: questões acertadas de primeira e questões respondidas.", align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.cell(largura_util, 6, text="Faixas: até 40% Baixo. 41-60% Médio baixo. 61-79% Médio alto. 80% ou mais Alto. Traço: sem tentativa.", align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        por_tabela, larg_nome, larg_hab = 5, 30, 28
        for ini in range(0, len(habilidades_ac), por_tabela):
            bloco_h = habilidades_ac[ini:ini + por_tabela]
            x_ac = pdf.l_margin + (largura_util - (larg_nome + larg_hab * len(bloco_h))) / 2
            pdf.set_font("CMU", 'B', 9)
            pdf.set_x(x_ac)
            pdf.cell(larg_nome, 9, text="Aluno", border=1, align='C')
            for k, h in enumerate(bloco_h):
                fim = "LMARGIN" if k == len(bloco_h) - 1 else "RIGHT"
                pdf.cell(larg_hab, 9, text=h, border=1, align='C', new_x=fim, new_y="NEXT" if fim == "LMARGIN" else "TOP")
            pdf.set_font("CMU", '', 10)
            for rotulo, pares in linhas_ac:
                eh_turma = rotulo == "Turma"
                pdf.set_font("CMU", 'B' if eh_turma else '', 10)
                if eh_turma:
                    pdf.set_text_color(31, 58, 110)
                else:
                    pdf.set_text_color(0, 0, 0)
                pdf.set_x(x_ac)
                if eh_turma:
                    pdf.set_fill_color(241, 243, 245)  # cinza com texto azul escuro, cor própria da linha da turma
                    pdf.cell(larg_nome, 9, text=rotulo, border=1, align='C', fill=True)
                else:
                    pdf.cell(larg_nome, 9, text=_texto_que_cabe(pdf, rotulo, larg_nome), border=1, align='C')
                for k, par in enumerate(pares[ini:ini + por_tabela]):
                    pct = percentual_acerto(par)
                    if eh_turma:
                        pdf.set_fill_color(241, 243, 245)
                    elif pct is None:
                        pdf.set_fill_color(255, 255, 255)
                    else:
                        cor = fundo_acerto(pct).split("#")[1][:6]
                        pdf.set_fill_color(int(cor[0:2], 16), int(cor[2:4], 16), int(cor[4:6], 16))
                    fim = "LMARGIN" if k == len(bloco_h) - 1 else "RIGHT"
                    pdf.cell(larg_hab, 9, text=texto_acerto(par), border=1, align='C', fill=True,
                             new_x=fim, new_y="NEXT" if fim == "LMARGIN" else "TOP")
            pdf.set_text_color(0, 0, 0)
            pdf.ln(6)

    # Desempenho da Turma (tabela + gráfico de XP) numa página, Detalhamento
    # por Conteúdo (tabela + gráfico de %) começando limpo na próxima — em vez
    # de deixar as duas seções disputarem espaço na mesma página e a quebra
    # automática cair no meio de qualquer coisa.
    pdf.add_page()

    # --- Tabela 2: Detalhamento do conteúdo que o professor estava vendo ---
    # Mesma regra da tabela 1: com nome vai de margem a margem (170mm) pra dar
    # 68mm ao nome completo; sem nome, 150mm centralizados.
    largura_tabela2 = largura_util if usar_nome_relatorio else 150  # 38+68+26+20+18 | 50+30+40+30
    x_tabela2 = pdf.l_margin + (largura_util - largura_tabela2) / 2
    pdf.set_font("CMU", 'B', 13)
    pdf.set_x(x_tabela2)
    pdf.cell(largura_tabela2, 8, text=f"Detalhamento - {conteudo_titulo}", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("CMU", 'B', 11)
    pdf.set_x(x_tabela2)
    if usar_nome_relatorio:
        # 38+68+26+20+18 = 170 (largura útil inteira). A coluna de login tem os
        # mesmos 38mm da tabela 1 de propósito: com 32mm um login comprido
        # colidia com o nome da coluna vizinha (visto no teste). Cabeçalhos
        # encurtados ("Total" em vez de "Total Questões") porque com 5 colunas o
        # texto longo não cabe mais.
        pdf.cell(38, 9, text="Login", border=1, align='C')
        pdf.cell(68, 9, text="Aluno", border=1, align='C')
        pdf.cell(26, 9, text="Concluídas", border=1, align='C')
        pdf.cell(20, 9, text="Total", border=1, align='C')
        pdf.cell(18, 9, text="Erros", border=1, align='C', new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(50, 9, text="Aluno", border=1, align='C')
        pdf.cell(30, 9, text="Concluídas", border=1, align='C')
        pdf.cell(40, 9, text="Total Questões", border=1, align='C')
        pdf.cell(30, 9, text="Erros", border=1, align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("CMU", '', 11)
    for linha in linhas_conteudo:
        pdf.set_x(x_tabela2)
        if usar_nome_relatorio:
            pdf.cell(38, 9, text=_texto_que_cabe(pdf, linha["Aluno"], 38), border=1, align='C')
            pdf.cell(68, 9, text=_texto_que_cabe(pdf, str(linha.get("Nome no Relatório", "")).strip(), 68), border=1, align='C')
            pdf.cell(26, 9, text=str(linha["Questões Concluídas"]), border=1, align='C')
            pdf.cell(20, 9, text=str(linha["Total de Questões"]), border=1, align='C')
            pdf.cell(18, 9, text=str(linha["Erros"]), border=1, align='C', new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.cell(50, 9, text=_texto_que_cabe(pdf, linha["Aluno"], 50), border=1, align='C')
            pdf.cell(30, 9, text=str(linha["Questões Concluídas"]), border=1, align='C')
            pdf.cell(40, 9, text=str(linha["Total de Questões"]), border=1, align='C')
            pdf.cell(30, 9, text=str(linha["Erros"]), border=1, align='C', new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)

    # --- Gráfico de barras: % concluído nesse conteúdo, por aluno (escala 0-100) ---
    if linhas_conteudo:
        itens_pct = []
        for linha in linhas_conteudo:
            total_linha = linha["Total de Questões"]
            pct = (linha["Questões Concluídas"] / total_linha * 100) if total_linha else 0
            itens_pct.append((linha["Aluno"], pct / 100, f"{pct:.0f}%", cor_por_percentual_concluido(pct)))
        _grafico_barras_pdf(pdf, "Gráfico de % Concluído", itens_pct, x_tabela2, largura_tabela2)

    return bytes(pdf.output())
