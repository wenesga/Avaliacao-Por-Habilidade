"""CSS da aplicação e carregamento da logo."""

import base64
import os
import streamlit as st
from config import ARQUIVO_LOGO


# ---------- Logo do projeto (opcional) ----------
def obter_logo_base64():
    """Retorna o logo.svg em base64 para uso em HTML customizado (banner), ou None se o arquivo não existir."""
    if os.path.exists(ARQUIVO_LOGO):
        try:
            with open(ARQUIVO_LOGO, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            return None
    return None


def aplicar_estilo():
    st.markdown("""
<style>
    /* Limita a largura do conteúdo principal e centraliza (estilo ChatGPT/X.com)
       em vez de esticar de ponta a ponta em monitores grandes. Não afeta a
       barra lateral, que tem sua própria largura fixa. O Streamlit já aplica
       um padding interno grande por padrão; reduzimos ele aqui pra sobrar
       mais espaço de conteúdo dentro do limite. */
    .stMainBlockContainer {
        max-width: 870px;
        padding-left: 2rem;
        padding-right: 2rem;
        margin-left: auto;
        margin-right: auto;
        /* O Streamlit reserva 96px (6rem) de padding-top por padrão, pra
           sobrar espaço embaixo da barra flutuante (Deploy/menu) — mas
           aqui essa barra é baixa e o conteúdo já tem título próprio logo
           abaixo, então sobrava um vão vazio grande no topo de toda
           página, banner ou não (relatado pelo Wenes, 2026-09-17,
           print mostrando o espaço em ambos os casos). Medido: era 96px,
           cortado pra 24px, depois pra 0 — aí ficou colado demais ("vixe,
           agora ficou colado"), então 38px (~1cm a 96dpi) de volta, pra
           dar uma folga mínima. Mais 19px (~5mm) depois que a barra de
           ferramentas do Streamlit voltou a mostrar o ícone de abrir/
           fechar a barra lateral, pra não ficar colado nele — depois
           ajustado à mão pelo Wenes direto no arquivo pra 60px ("ficou
           perfeito", 2026-09-17). */
        padding-top: 60px;
    }

    /* Só o botão "Deploy" (chrome do Streamlit Cloud) — NÃO a barra inteira.
       O "⋮" fica visível (2026-09-25, pedido do Wenes) pra trocar o tema
       claro/escuro. Versão
       anterior escondia a barra toda (`[data-testid="stHeader"]
       {display:none}`), e isso quebrou o botão de expandir a barra
       lateral: quando o Wenes encolhia a barra lateral e recarregava a
       página, o botão pra abrir de novo (`stExpandSidebarButton`) mora
       DENTRO dessa mesma barra escondida, então ficava sem jeito nenhum
       de reabrir (bug relatado 2026-09-17). Escondendo só os dois botões
       específicos, o resto da barra (inclusive esse controle) continua
       funcionando normalmente. */
    [data-testid="stAppDeployButton"] {
        display: none;
    }

    /* Cada bloco invisível (os 5 components.html(..., height=0) que injetam
       JS — bloqueio de espaço no apelido, aviso de saída, clique na logo etc.
       — e o próprio <style> deste CSS) ainda ocupa uma "vaga" na lista vertical
       da página, com o gap de 16px entre itens contando mesmo pra quem tem
       altura zero. No topo da página isso somava 96px de vão vazio — medido
       ao vivo, era o resto do espaço que sobrava depois do padding-top e da
       barra Deploy já cortados (Wenes, 2026-09-17: "ainda tá uns 2cm"). Achado
       inspecionando o DOM: 6 stElementContainer de altura 0 antes do primeiro
       botão. display:none tira da lista de vez, sem gap nenhum — e um <style>
       escondido continua valendo normalmente, isso é comportamento padrão do
       HTML/CSS, não depende do elemento estar visível. */
    .stElementContainer:has([data-testid="stIFrame"]),
    .stElementContainer:has(style) {
        display: none;
    }

    .metric-card { background-color: #ffffff; border-left: 5px solid #1e40af; border-radius: 8px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin-bottom: 15px; }
    .metric-title { color: #64748b; font-size: 14px; font-weight: 700; text-transform: uppercase; }
    .metric-value { color: #1e3a8a; font-size: 28px; font-weight: 800; margin-top: 5px; }
    .gamification-box { background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); color: white; padding: 15px 20px; border-radius: 10px; font-size: 16px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3); }
    /* .gamification-box acima nunca chegou a ser usada em lugar nenhum do app —
       sobra de uma versão antiga. Deixada como está (não é deste ajuste),
       mas fica o registro pra quem for limpar código depois. */

    /* Selo de XP acima da Avaliação (2026-09-05) — pedido do usuário
       pra dar mais destaque ao XP acumulado, além do texto pequeno que já
       existe na barra lateral. Gradiente opaco + texto branco (mesma técnica
       do .home-banner), não rgba() semi-transparente: aqui o objetivo é
       "saltar aos olhos" como um emblema de jogo, não se misturar ao tema. */
    .xp-destaque-missoes {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: #ffffff;
        padding: 10px 24px;
        border-radius: 999px;
        box-shadow: 0 4px 10px rgba(59, 130, 246, 0.35);
        margin-bottom: 18px;
    }
    .xp-destaque-missoes .icone { font-size: 22px; }
    .xp-destaque-missoes .valor { font-size: 19px; font-weight: 700; letter-spacing: 0.01em; }

    /* Banner da página inicial */
    .home-banner {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 60%, #60a5fa 100%);
        color: white;
        padding: 40px 35px;
        border-radius: 16px;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px -5px rgba(30, 64, 175, 0.4);
    }
    .home-banner-logo { font-size: 48px; margin-bottom: 8px; }
    .home-banner-logo-img { width: 76px; height: 76px; object-fit: cover; border-radius: 16px; margin-bottom: 10px; background-color: #ffffff; padding: 4px; box-shadow: 0 4px 10px rgba(0,0,0,0.15); }
    .home-banner-arte {
        aspect-ratio: 1792 / 592;
        background-size: cover;
        background-position: center;
        border-radius: 16px;
        margin-bottom: 16px;
        padding: 0 5%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        color: white;
        box-shadow: 0 10px 25px -5px rgba(30, 64, 175, 0.4);
    }
    .home-banner-arte p.home-banner-arte-titulo { font-size: clamp(20px, 4.2vw, 48px) !important; font-weight: 800; line-height: 1.1; margin: 0; max-width: 48%; }
    .home-banner-arte p.home-banner-arte-subtitulo { font-size: clamp(11px, 1.6vw, 20px) !important; opacity: 0.92; margin: 8px 0 0; max-width: 46%; }
    .home-banner-titulo { font-size: 32px; font-weight: 800; margin: 0; }
    .home-banner-subtitulo { font-size: 16px; opacity: 0.92; margin-top: 6px; max-width: 640px; }

    /* O tema claro/escuro do Streamlit pode ser trocado dentro do próprio
       app (menu ⋮ > Settings), sem relação com o tema do sistema — então
       "@media (prefers-color-scheme)" não pega essa troca de jeito nenhum
       (é por isso que a versão anterior falhou: fundo claro + texto branco
       herdado do tema escuro real = ilegível). A saída é não tentar
       detectar o tema: rgba() semi-transparente vira um "tingimento" sobre
       o que estiver por trás, então se adapta sozinho. Opacidade calibrada
       pra bater com os tons reais que o Streamlit usa (~#f0f2f6 no claro,
       ~#262730 no escuro — conferido ao vivo nos dois). Sem "color" no
       texto, ele herda a cor certa do tema automaticamente. */
    .home-step-card {
        background-color: rgba(148, 163, 184, 0.16); border: 1px solid rgba(148, 163, 184, 0.4); border-radius: 12px;
        padding: 18px; height: 100%; box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        margin-bottom: 16px;
    }
    /* Placar da turma. Mesma técnica de cor dos cartões da home: rgba() por
       cima do fundo, sem "color" fixo no texto, pra funcionar no tema claro e
       no escuro sem tentar detectar qual está ativo. */
    .placar-caixa {
        border: 1px solid rgba(148, 163, 184, 0.4);
        border-radius: 12px;
        overflow: hidden;
    }
    .placar-linha {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 16px;
        border-bottom: 1px solid rgba(148, 163, 184, 0.22);
    }
    .placar-linha:last-child { border-bottom: none; }
    .placar-linha.eu {
        background-color: rgba(59, 130, 246, 0.14);
        font-weight: 700;
    }
    .placar-pos {
        min-width: 34px;
        font-size: 17px;
        text-align: center;
        opacity: 0.85;
    }
    .placar-nome { flex: 1; font-size: 16px; }
    .placar-xp {
        font-variant-numeric: tabular-nums;  /* números alinhados entre as linhas */
        font-weight: 700;
        color: #16a34a;
    }

    .home-step-numero { color: #3b82f6; font-size: 13px; font-weight: 800; text-transform: uppercase; }
    .home-step-titulo { font-size: 17px; font-weight: 700; margin: 4px 0 6px 0; }
    .home-step-texto { opacity: 0.75; font-size: 14px; }

    /* Cartões com borda (st.container(border=True)) dentro de colunas lado a
       lado: por padrão cada um só cresce até onde o próprio texto termina,
       ficando com alturas diferentes. A coluna em si já é esticada pelo
       Streamlit pra acompanhar a mais alta do grupo, mas isso é feito via
       flexbox (não uma altura fixa), então "height: 100%" sozinho não
       resolve — precisa de flex-grow pra herdar esse espaço extra. */
    div[data-testid="stColumn"] div[data-testid="stLayoutWrapper"] {
        flex-grow: 1;
    }
    div[data-testid="stColumn"] div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"] {
        height: 100%;
    }

    /* Cores suaves dos cartões de "Conteúdos disponíveis" (ver PALETA_CORES_CARTAO
       e o key="cartao_..._cor_X" passado a st.container). Usa rgba() com opacidade
       baixa em vez de cor sólida, pra funcionar bem tanto no tema claro quanto no
       escuro — a cor vira um "tingimento" leve por cima do fundo de cada tema,
       em vez de uma cor fixa que combina com um só dos dois. */
    [class*="_cor_azul"]    { background-color: rgba(59, 130, 246, 0.12) !important; border-color: rgba(59, 130, 246, 0.4) !important; }
    [class*="_cor_roxo"]    { background-color: rgba(168, 85, 247, 0.12) !important; border-color: rgba(168, 85, 247, 0.4) !important; }
    [class*="_cor_rosa"]    { background-color: rgba(236, 72, 153, 0.12) !important; border-color: rgba(236, 72, 153, 0.4) !important; }
    [class*="_cor_amarelo"] { background-color: rgba(245, 158, 11, 0.14) !important; border-color: rgba(245, 158, 11, 0.45) !important; }
    [class*="_cor_verde"]   { background-color: rgba(16, 185, 129, 0.12) !important; border-color: rgba(16, 185, 129, 0.4) !important; }
    [class*="_cor_ciano"]   { background-color: rgba(6, 182, 212, 0.12) !important; border-color: rgba(6, 182, 212, 0.4) !important; }

    /* Título dos painéis expansíveis (st.expander) um pouco maior — vale tanto
       pro conteúdo estático (Estatística) quanto pros conteúdos dinâmicos,
       já que os dois usam o mesmo componente e ficam consistentes entre si. */
    div[data-testid="stExpander"] summary [data-testid="stMarkdownContainer"] p {
        font-size: 20px !important;
        font-weight: 600 !important;
    }

    /* Título principal de cada página (st.title = h1) vinha no tamanho padrão do
       Streamlit (44px), bem maior que os títulos de seção da própria home
       ("Como funciona", "Conteúdos disponíveis", 28px/600 via h3) — igualado
       aqui pra manter a mesma hierarquia visual em todas as páginas (Painel do
       Professor, Avaliação, Conteúdo). Line-height é relativo (em), então
       acompanha o font-size automaticamente. */
    h1 {
        font-size: 28px !important;
        font-weight: 600 !important;
    }

    /* Título dentro dos cartões de "Conteúdos disponíveis" (h4, ver PALETA_CORES_CARTAO)
       vinha em 24px, maior que o título dos cartões "Como funciona" (17px/700,
       .home-step-titulo) — reduzido pra bater com esse tamanho. Escopado só aos
       cartões de conteúdo via [class*="_cor_"] (mesma classe usada pra cor de fundo),
       pra não afetar outros h4 do app. */
    [class*="_cor_"] h4 {
        font-size: 17px !important;
        font-weight: 700 !important;
    }

    /* Cartões "Como funciona" (Passo 1/2/3) usam st.markdown com HTML cru
       (.home-step-card), não st.container(border=True) — por isso o fix de altura
       igual acima (stLayoutWrapper) não se aplica a eles: o texto do Passo 3 é mais
       longo, então só aquele cartão cresce. stVerticalBlock/stColumn já esticam pra
       acompanhar o mais alto do grupo (comportamento nativo do Streamlit), mas o
       stElementContainer por dentro não geda esse espaço extra sem flex-grow.
       :has() escopa a regra só aos cartões com .home-step-card, sem mexer em outras
       colunas do app. */
    div[data-testid="stElementContainer"]:has(.home-step-card) {
        flex-grow: 1;
        display: flex;
    }
    div[data-testid="stElementContainer"]:has(.home-step-card) [data-testid="stMarkdown"],
    div[data-testid="stElementContainer"]:has(.home-step-card) [data-testid="stMarkdown"] > div,
    div[data-testid="stElementContainer"]:has(.home-step-card) [data-testid="stMarkdownContainer"] {
        height: 100%;
    }

    /* Cada conteúdo cadastrado (Painel do Professor > Gerenciar Conteúdos) é
       um st.container(border=True) — cartão de verdade, com borda e cantos
       arredondados, em vez da lista em colunas com uma linha horizontal
       entre cada item. Pedido do Wenes (2026-09-14): "mais elegante e
       estilizado", mas com estilo PRÓPRIO do painel do professor — não é
       pra copiar o card do aluno na Início, que mostra outra informação. */
    div[class*="st-key-card_conteudo_"] {
        margin-bottom: 12px;
    }

    /* Badges (pílulas) dentro do cartão: resumo do tipo/quantidade de
       questões e do descritor mapeado, visível sem precisar abrir
       "Editar". */
    .badge-conteudo {
        display: inline-block;
        padding: 5px 14px;
        border-radius: 999px;
        font-size: 14px;
        font-weight: 700;
        margin: 6px 6px 0 0;
    }
    .badge-conteudo-tipo {
        background: #eef2ff;
        color: #4338ca;
    }
    .badge-conteudo-descritor {
        background: #ecfdf5;
        color: #047857;
    }

    /* Cards suaves dos 3 totais de XP em Configurações (Matéria Padrão /
       Matérias Cadastradas / Total do catálogo) — antes usava st.metric(),
       que só desenha número preto puro sem nenhuma cor de fundo; o Wenes
       achou "feio" pro Painel do Professor (2026-09-17), queria algo mais
       suave. Reaproveita as MESMAS cores dos badges de card (indigo dos
       badges de tipo, verde do descritor) + um terceiro tom neutro pro total,
       que é soma dos outros dois, não uma categoria própria. */
    .resumo-xp-card {
        border-radius: 12px;
        padding: 14px 16px;
        text-align: center;
    }
    .resumo-xp-card .rotulo {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        opacity: 0.75;
        margin-bottom: 4px;
    }
    .resumo-xp-card .valor {
        font-size: 21px;
        font-weight: 700;
    }
    /* Em tela estreita (celular), st.columns empilha os 3 cards um embaixo
       do outro — e aí eles ficavam colados (relatado pelo Wenes, 2026-09-22).
       Causa: o stMarkdownContainer do Streamlit já vem com margin-bottom:
       -16px por padrão (serve pra cancelar um espaçamento dele mesmo quando
       tem mais coisa depois dentro do mesmo bloco). Em coluna lado a lado
       isso não se nota — o espaço entre colunas é horizontal (column-gap),
       não vertical. Empilhado, essa margem negativa passa a comer o
       row-gap vertical entre as colunas, cancelando os 16px de respiro.
       Zerar a margem só nas colunas com .resumo-xp-card devolve o respiro
       sem mexer no espaçamento de mais nada no app. */
    div[data-testid="stColumn"]:has(.resumo-xp-card) div[data-testid="stMarkdownContainer"] {
        margin-bottom: 0 !important;
    }
    .resumo-xp-total { background: #f1f5f9; }
    .resumo-xp-total .rotulo, .resumo-xp-total .valor { color: #334155; }

    /* Pop-up de "Salvo com sucesso" (ver renderizar_flash_pendente): fixo no
       canto superior direito, por cima de tudo, pra não precisar rolar a
       tela pra ver — bug relatado pelo Wenes (2026-09-17), editou um
       conteúdo longo, salvou, e a mensagem apareceu lá em cima, fora da
       tela. st.toast() faria isso nativamente (mesma posição, canto
       superior direito), mas parou de funcionar neste ambiente. Pequeno de
       propósito ("espero que não seja grandão", Wenes 2026-09-17): não é um
       modal, não bloqueia clique em nada por trás. Some sozinho em 3s via
       animação CSS (Wenes, 2026-09-17: "rápido, um dois três segundos, não
       pode ficar lá a vida toda") — st.markdown não executa <script>, então
       não dá pra usar um timer JS; keyframes resolve sem precisar de JS. */
    @keyframes flash-toast-sumir {
        0%, 80% { opacity: 1; }
        100% { opacity: 0; }
    }
    .flash-toast {
        position: fixed;
        top: 70px;
        right: 20px;
        z-index: 999999;
        max-width: 300px;
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        color: #047857;
        font-size: 14px;
        font-weight: 600;
        padding: 12px 16px;
        border-radius: 10px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
        animation: flash-toast-sumir 3s ease forwards;
        pointer-events: none;
    }

    /* Botões "Editar"/"Excluir" de cada conteúdo cadastrado: por padrão as duas
       colunas do st.columns(2) dividem o espaço em duas metades iguais, então
       sobra um vão grande entre os botões (cada um bem mais estreito que sua
       metade da coluna) e o par fica "flutuando" à esquerda do espaço
       reservado. Aqui as colunas encolhem pro tamanho do próprio botão
       (flex: 0 0 auto), o vão entre elas fica pequeno, e o par todo é
       empurrado pra direita — só dentro do key deste container. */
    div[class*="st-key-acoes_conteudo_"] div[data-testid="stHorizontalBlock"] {
        gap: 8px !important;
        justify-content: flex-end;
    }
    div[class*="st-key-acoes_conteudo_"] div[data-testid="stColumn"] {
        width: auto !important;
        flex: 0 0 auto !important;
    }
    /* Em tela estreita (celular), o Streamlit faz duas coisas ao mesmo tempo
       que juntas quebravam essa fileira de botões (confirmado testando ao
       vivo no celular, 2026-09-14): empilha QUALQUER st.columns() na
       vertical, E força min-width: calc(100% - 24px) em cada coluna —
       quase a largura inteira do card, pensado pra layout empilhado. A
       primeira tentativa de correção só forçou a linha a ficar horizontal
       (flex-wrap: nowrap), mas cada coluna continuou "querendo" quase 100%
       de largura por causa do min-width — o resultado foi as 4 colunas se
       empurrando pra fora do card, e só a última ("Excluir") sobrava
       visível. A correção de verdade precisa zerar esse min-width também,
       senão width:auto não tem efeito nenhum (min-width vence no flexbox). */
    @media (max-width: 640px) {
        div[class*="st-key-acoes_conteudo_"] div[data-testid="stHorizontalBlock"] {
            flex-direction: row !important;
            flex-wrap: nowrap !important;
        }
        div[class*="st-key-acoes_conteudo_"] div[data-testid="stColumn"] {
            width: auto !important;
            min-width: 0 !important;
        }
    }

    /* Botão "Sair" do Painel do Professor: empurra pra borda direita da
       coluna sem esticar o botão. Duas pegadinhas encontradas medindo ao
       vivo (2026-09-14), não adivinhando:
       1) O container do Streamlit por baixo dos panos já é flex-direction:
          COLUNA — então justify-content controla o eixo VERTICAL, não o
          horizontal (por isso não tinha efeito nenhum). Quem alinha no eixo
          horizontal, numa coluna, é align-items.
       2) O filho direto do container vem com width:100% do próprio
          Streamlit — um filho largo assim não sobra espaço nenhum pra
          alinhar, então a largura dele também precisa ser travada pro
          tamanho do próprio conteúdo. */
    div[class*="st-key-acao_sair_professor"] {
        display: flex;
        align-items: flex-end;
    }
    div[class*="st-key-acao_sair_professor"] > div {
        width: fit-content !important;
    }

    /* Sobe o conteúdo inteiro da barra lateral (Início + tudo abaixo) uns 5mm
       (~19px) pra cima — pedido do Wenes (2026-09-13). O espaço de origem não
       é nosso: é margin-bottom:16px do próprio cabeçalho do Streamlit (ícone
       de recolher a barra), medido ao vivo via getBoundingClientRect(); não
       dá pra mexer nesse cabeçalho sem arriscar cortar o ícone, então o ajuste
       é uma margem negativa no bloco de conteúdo logo abaixo dele. */
    div[data-testid="stSidebarUserContent"] {
        margin-top: -19px;
    }

    /* Menu lateral estilo app (Gmail/ChatGPT): botões colados, alinhados à esquerda,
       com destaque visual para o item ativo e hover suave no restante. */
    div[data-testid="stSidebar"] button {
        margin-bottom: 4px;
        text-align: left;
        justify-content: flex-start;
        border-radius: 8px;
        transition: background-color 0.15s ease;
    }
    div[data-testid="stSidebar"] button p {
        text-align: left;
    }
    div[data-testid="stSidebar"] button[kind="secondary"]:hover {
        background-color: #eef2ff;
        border-color: #c7d2fe;
    }
    div[data-testid="stSidebar"] button[kind="primary"] {
        box-shadow: none;
    }

    /* A cor principal do app é azul (.streamlit/config.toml), mas os botões
       de confirmar exclusão ("Sim, excluir", "Sim, apagar tudo") continuam
       vermelhos: ali a cor avisa do perigo. */
    div[class*="st-key-confirmar_"] button[kind="primary"] {
        background-color: #dc2626;
        border-color: #dc2626;
    }
    div[class*="st-key-confirmar_"] button[kind="primary"]:hover {
        background-color: #b91c1c;
        border-color: #b91c1c;
    }

    /* Cartões dos conteúdos (Gerenciar Conteúdos): fundo cinza suave, pra separar um
       do outro. Transparência, pra valer no tema claro e no escuro. */
    div[class*="st-key-card_conteudo_"] {
        background-color: rgba(128, 128, 128, 0.06);
    }

    /* Abas do Detalhamento por Conteúdo: formato de aba de navegador. A aba
       ativa leva o azul do tema (traço no topo e fundo azulado); as outras ficam
       cinza discretas. Cores com transparência, pra valer no tema claro e no escuro. */
    div[role="tablist"] {
        gap: 4px;
        border-bottom: 1px solid rgba(128, 128, 128, 0.35);
    }
    div[role="tablist"] .react-aria-SelectionIndicator {
        display: none;
    }
    div[data-testid="stTab"] {
        background-color: rgba(128, 128, 128, 0.10);
        border: 1px solid rgba(128, 128, 128, 0.30);
        border-bottom: none;
        border-radius: 10px 10px 0 0;
        padding: 8px 16px;
        margin-bottom: 0;
    }
    div[data-testid="stTab"]:hover {
        background-color: rgba(31, 78, 154, 0.10);
    }
    div[data-testid="stTab"][aria-selected="true"] {
        background-color: rgba(31, 78, 154, 0.14);
        border-color: rgba(31, 78, 154, 0.55);
        border-top: 3px solid #1f4e9a;
        font-weight: 600;
    }

    /* Barrinha na borda esquerda dos itens do menu — diferencia "Matéria
       Padrão" (roxo/azul) de "Matérias Cadastradas" (verde) mesmo em
       repouso, sem pintar o botão inteiro (encostaria na cor do item
       ativo e viraria parque de diversão). Primeira versão era cinza neutro,
       mas ficou imperceptível demais — trocada por cor de verdade a pedido
       do Wenes (2026-09-14), mantendo elegante por ser só um traço fino, não
       um preenchimento. Cores emprestadas dos badges do Painel do Professor
       (.badge-conteudo-tipo / .badge-conteudo-descritor), pra usar a mesma
       linguagem visual em vez de inventar uma terceira paleta. Some quando o
       botão está ativo (kind="primary", já azul): a barrinha só faz
       sentido como pista discreta no estado normal. */
    div[class*="st-key-nav_conteudo_"] button[kind="secondary"] {
        border-left: 3px solid #10b981;
    }

    /* Bloco de identidade do aluno no topo da barra lateral: as duas versões
       (deslogado = campo de nome + "Acessar"; logado = nome + XP + "Sair")
       têm alturas naturais diferentes, e como o Streamlit desenha de cima pra
       baixo, essa diferença empurrava TODO o menu de navegação alguns pixels
       pra baixo ao logar. A altura mínima reserva o espaço da versão mais
       alta (a deslogada), então os itens do menu ficam sempre na mesma
       coordenada — dá pra clicar "Início" no mesmo lugar antes e depois de
       entrar. Valor conferido no DOM real das duas versões, não estimado. */
    div[class*="st-key-sidebar_identidade"] {
        min-height: 148px;
        /* O conteúdo logado (nome + XP + Sair) é mais baixo que o deslogado
           (campo + dica + Acessar), que é quem define os 148px. Sem isso,
           a sobra de altura ficava toda embaixo, abrindo um vão grande entre
           o botão "Sair" e o divisor — display:flex + justify-content:center
           reparte essa sobra em cima e embaixo, sem mudar a altura total
           (o que continua garantindo que o menu abaixo não se mexa). */
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* Linha de dica/erro do apelido. Existe sempre (com a dica ou com o erro),
       nunca aparece e some — senão o bloco de identidade mudaria de altura e
       empurraria o menu, que é justamente o que o min-height acima evita. */
    .apelido-aviso {
        font-size: 12px;
        opacity: 0.65;
        margin: -8px 0 6px 2px;
        min-height: 18px;
    }
    .apelido-aviso.erro {
        color: #ff4b4b;
        opacity: 1;
    }

    /* Rótulo do grupo "Matérias": não é um item clicável, é o cabeçalho do
       nível 2 da navegação. Menor, em caixa alta e apagado justamente pra
       não competir com os botões e deixar a hierarquia visível de relance
       (Início e Painel do Professor são nível 1, sem rótulo de grupo). */
    .sidebar-secao {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        opacity: 0.55;
        margin: 4px 0 6px 4px;
    }

    /* "Matérias Cadastradas" fica um pouco mais separada do botão de cima
       ("📊 Estatística") do que o espaçamento padrão do .sidebar-secao —
       reforça visualmente que é o início de um grupo novo, não uma
       continuação do mesmo. */
    .sidebar-secao-espacada {
        margin-top: 16px;
    }

    /* Linha entre "Acessar" e "Início": margem ASSIMÉTRICA de propósito, não
       erro — o st.form do login (que fica logo acima) soma ~19px de espaço
       próprio que o <hr> sozinho não tem embaixo. Medido no DOM (não
       chutado): sem isso, o espaço de cima ficava 27px e o de baixo só 8px.
       margin-top:0 (deixa só o espaço que o form já garante) e
       margin-bottom:19px (iguala ao que sobra em cima) deixam os dois lados
       com a MESMA distância final. */
    .sidebar-divisor-identidade {
        border: none;
        border-top: 1px solid rgba(128, 128, 128, 0.25);
        margin: 0px 4px 19px 4px !important;
    }

    /* Linha entre a última matéria cadastrada e "Painel do Professor":
       margem assimétrica de propósito (mesmo raciocínio da
       .sidebar-divisor-identidade) — medido no DOM, com 8px dos dois lados o
       espaço de cima ficava 24px e o de baixo só 8px. margin-bottom maior
       iguala os dois. */
    .sidebar-divisor-professor {
        border: none;
        border-top: 1px solid rgba(128, 128, 128, 0.25);
        margin: 8px 4px 24px 4px !important;
    }

    /* Cabeçalho da barra lateral: logo EM CIMA, título EMBAIXO, os dois
       centralizados — não lado a lado (a versão anterior deixava o título
       desalinhado com a logo, com cara de gambiarra). */
    div[class*="st-key-sidebar_cabecalho"] {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        /* Aproxima o título da logo — pedido do Wenes (2026-09-13). O
           espaçamento de origem (16px) não vem de nenhuma margem nossa: é o
           "gap" padrão que o Streamlit aplica entre elementos empilhados
           dentro de um container, confirmado medindo ao vivo (getBoundingClientRect
           batendo exatamente com o "gap" do flex, 16px). Reduzir esse gap é o
           jeito direto de aproximar; um "margin-top" negativo no botão do
           título, tentado antes, tem efeito inconsistente aqui porque o botão
           fica dentro de um item flex (que não deixa a margem colapsar com o
           container do jeito esperado) — medido ao vivo, não deu o resultado
           previsto, por isso o ajuste é no gap, não em margem. */
        gap: 2px;
    }
    div[class*="st-key-sidebar_cabecalho"] img {
        margin: 0 auto 0 auto;
        cursor: pointer;
    }

    /* Título "Trilha de Aprendizagem": é um st.button de verdade (leva pra
       Início ao clicar — ver bloco 9), mas precisa PARECER um título, não
       um botão, senão ficaria estranho um retângulo com borda logo abaixo
       da logo. Zera fundo/borda/sombra do botão padrão do Streamlit e deixa
       só o texto, em negrito, centralizado; o :hover sutil (fundo leve) é a
       única pista visual de que aquilo é clicável. */
    div[class*="st-key-nav_titulo_inicio"] button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 4px 6px !important;
        justify-content: center !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        color: inherit !important;
    }
    div[class*="st-key-nav_titulo_inicio"] button:hover {
        background: rgba(128, 128, 128, 0.12) !important;
    }
</style>
""", unsafe_allow_html=True)
