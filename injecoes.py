"""Trechos de JavaScript e manifest do app instalado injetados na página."""

import streamlit.components.v1 as components
import os


def _injetar_manifest_pwa():
    """Substitui o <link rel="manifest"> e o <link rel="apple-touch-icon"> no
    <head> real da página (via window.parent, já que este componente roda
    num iframe à parte) pelos nossos, apontando pros ícones da logo do projeto
    servidos como arquivo de verdade em /static (ver .streamlit/config.toml,
    "enableStaticServing").

    O próprio Streamlit já injeta essas duas tags por padrão (manifest
    genérico com name "Streamlit" e favicon_256.png do framework) — por isso
    não dá pra só acrescentar quando "não existir": a tag do Streamlit sempre
    existe primeiro, então é preciso achar a que já está lá e trocar o href.

    Importante: o href do manifest e dos ícones precisa ser uma URL de
    arquivo real — uma tentativa anterior usando "data:" URI embutida veio
    vazia porque não é um formato garantido pra src de ícone de manifest, e
    o Android silenciosamente ignorava e caía no ícone genérico."""
    if not os.path.exists("static/manifest.json"):
        return
    components.html(
        """
        <script>
        (function() {
            const doc = window.parent.document;
            let manifestLink = doc.querySelector('link[rel="manifest"]');
            if (!manifestLink) {
                manifestLink = doc.createElement('link');
                manifestLink.rel = 'manifest';
                doc.head.appendChild(manifestLink);
            }
            manifestLink.href = 'app/static/manifest.json?v=8';

            let appleIcon = doc.querySelector('link[rel="apple-touch-icon"]');
            if (!appleIcon) {
                appleIcon = doc.createElement('link');
                appleIcon.rel = 'apple-touch-icon';
                doc.head.appendChild(appleIcon);
            }
            appleIcon.href = 'app/static/logo.svg?v=3';
        })();
        </script>
        """,
        height=0,
        width=0,
    )


def _injetar_bloqueio_espaco_apelido():
    """Tira o espaço do campo de apelido assim que ele aparece, como em campo
    de nome de usuário de site — funciona digitando, colando ou em qualquer
    teclado, inclusive o virtual de celular.

    Versão anterior escutava 'keydown' (a tecla sendo pressionada) e bloqueava
    o espaço antes de entrar. Funcionava em teclado físico, mas boa parte dos
    teclados virtuais de celular (Android, iPhone) não dispara um 'keydown' de
    verdade pra cada tecla — o texto entra no campo por outro caminho, sem
    passar pelo evento que a versão antiga escutava. Resultado: bloqueava no
    computador e deixava passar no celular.

    A correção ouve 'input' em vez de 'keydown'. 'input' dispara sempre que o
    VALOR do campo muda de verdade, não importa como — teclado físico, teclado
    virtual, colar, ditado por voz. Deixa o espaço entrar e tira na mesma hora,
    então o efeito visual pro aluno é o mesmo (o espaço nunca fica ali), só que
    funciona em qualquer aparelho.

    O guard `if (limpo === el.value) return` evita loop infinito: só mexemos
    no campo quando há espaço de verdade pra tirar; sem espaço, o handler não
    reescreve o valor e não dispara a si mesmo de novo.

    Isto é conveniência de digitação, NÃO validação: apelido_invalido() continua
    valendo no servidor e é ela que garante a regra mesmo se o JS estiver
    desligado ou o navegador se comportar diferente do esperado."""
    components.html(
        """
        <script>
        (function() {
            const win = window.parent;
            if (win.__bloqueioEspacoApelido) return;
            win.__bloqueioEspacoApelido = true;

            function ehCampoApelido(el) {
                return el && el.tagName === 'INPUT'
                    && (el.getAttribute('aria-label') || '').toLowerCase().includes('apelido');
            }

            win.document.addEventListener('input', function(e) {
                const el = e.target;
                if (!ehCampoApelido(el)) return;
                const limpo = el.value.replace(/\\s+/g, '');
                if (limpo === el.value) return;
                const setter = Object.getOwnPropertyDescriptor(win.HTMLInputElement.prototype, 'value').set;
                setter.call(el, limpo);
                el.dispatchEvent(new Event('input', {bubbles: true}));
            }, true);
        })();
        </script>
        """,
        height=0,
        width=0,
    )


def _injetar_aviso_saida():
    """Aviso nativo do navegador ('Sair do site? Alterações podem não ser
    salvas') antes de fechar a aba, atualizar ou navegar pra fora.

    Esse app é uma SPA (single page application, ver conversa de 2026-09-03):
    tudo acontece dentro de uma única página carregada, trocando de conteúdo
    via WebSocket — nunca existe uma "página anterior" de verdade. Por isso
    o botão Voltar do navegador não tem pra onde voltar dentro do app, e sai
    fora dele sem aviso nenhum, confundindo quem tá usando. O texto do aviso
    é fixo, definido pelo próprio navegador por segurança (nenhum site pode
    customizar essa mensagem desde ~2011) — só dá pra ligar/desligar, não
    mudar a aparência."""
    components.html(
        """
        <script>
        (function() {
            const win = window.parent;
            if (win.__avisoSaidaAtivo) return;
            win.__avisoSaidaAtivo = true;
            win.addEventListener('beforeunload', function (e) {
                e.preventDefault();
                e.returnValue = '';
            });
        })();
        </script>
        """,
        height=0,
        width=0,
    )


def _injetar_liberar_scroll_grafico():
    """Deixa a página rolar normalmente quando o mouse está em cima de um
    gráfico (Altair/Vega-Lite).

    O wrapper do próprio Streamlit (.stVegaLiteChart) intercepta o scroll do
    mouse em cima de QUALQUER gráfico, mesmo sem nenhuma opção de zoom/pan
    ligada no gráfico em si — confirmado direto no navegador (nenhum gráfico
    deste app usa .interactive(), e mesmo assim o scroll travava; e trocar
    st.bar_chart por Altair puro, testado antes, não resolveu — o bloqueio
    vem do wrapper do Streamlit, não da biblioteca do gráfico). Quem tenta
    rolar a página com o cursor em cima de um gráfico ficava "preso" ali.

    Como a captura acontece num listener interno do Streamlit/Vega, não dá
    pra simplesmente "desligar" essa opção — a correção é ouvir o evento de
    scroll ANTES dele (fase de captura, que sempre roda primeiro, não importa
    o que outro listener faça depois) e, se o alvo for dentro de um gráfico,
    rolar a área principal da página (.stMain, que é quem de fato tem a
    barra de rolagem no Streamlit) manualmente."""
    components.html(
        """
        <script>
        (function() {
            const win = window.parent;
            if (win.__liberaScrollGraficoAtivo) return;
            win.__liberaScrollGraficoAtivo = true;
            win.document.addEventListener('wheel', function (e) {
                const dentroDeGrafico = e.target.closest && e.target.closest('.stVegaLiteChart');
                if (!dentroDeGrafico) return;
                const areaPrincipal = win.document.querySelector('.stMain');
                if (!areaPrincipal) return;
                areaPrincipal.scrollTop += e.deltaY;
                e.preventDefault();
            }, { capture: true, passive: false });
        })();
        </script>
        """,
        height=0,
        width=0,
    )


def _injetar_clique_logo_inicio():
    """Faz a LOGO (imagem) também levar pra Início ao clicar, não só o texto
    "Trilha de Aprendizagem" ao lado — pedido do Wenes (2026-09-13): pra ele
    logo+título são "um objeto só" (é assim que funciona em praticamente todo
    site/app), então clicar em qualquer parte tem que navegar.

    st.image() não tem on_click nem aceita link. A solução é ouvir clique em
    qualquer lugar dentro do cabeçalho (".st-key-sidebar_cabecalho") e, se não
    foi um clique direto no botão de título, simular um clique nele — reaproveita
    a navegação que o botão já faz, sem duplicar lógica de rerun/session_state."""
    components.html(
        """
        <script>
        (function() {
            const win = window.parent;
            if (win.__cliqueLogoInicioAtivo) return;
            win.__cliqueLogoInicioAtivo = true;
            win.document.addEventListener('click', function (e) {
                const cabecalho = e.target.closest && e.target.closest('div[class*="st-key-sidebar_cabecalho"]');
                if (!cabecalho) return;
                const botao = cabecalho.querySelector('div[class*="st-key-nav_titulo_inicio"] button');
                if (!botao || e.target.closest('button') === botao) return;
                botao.click();
            }, { capture: true });
        })();
        </script>
        """,
        height=0,
        width=0,
    )


def aplicar_injecoes():
    _injetar_manifest_pwa()
    _injetar_bloqueio_espaco_apelido()
    _injetar_aviso_saida()
    _injetar_liberar_scroll_grafico()
    _injetar_clique_logo_inicio()
