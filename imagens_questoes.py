"""Imagens anexadas ao enunciado das questões."""

import hashlib
import io
import os
from PIL import Image, ImageOps
from config import DIR_DADOS

PASTA_IMAGENS = "imagens_questoes"
DIR_IMAGENS_GRAVACAO = os.path.join(DIR_DADOS, PASTA_IMAGENS)
LARGURA_MAXIMA = 1400
QUALIDADE_JPEG = 88
LARGURA_EXIBICAO = 340  # largura (px) da imagem na tela do aluno; o botão de ampliar mostra o tamanho todo
LIMITE_RAZAO_PNG = 3  # PNG só é usado se tiver até 3 vezes o tamanho do JPEG
PESO_MAXIMO_JPEG = 250_000  # bytes; acima disso a qualidade é reduzida aos poucos
QUALIDADE_JPEG_MINIMA = 60


def _codificar_jpeg(imagem, qualidade):
    buffer = io.BytesIO()
    imagem.save(buffer, "JPEG", quality=qualidade, optimize=True)
    return buffer


def salvar_imagem_questao(arquivo):
    """
    Reduz a imagem enviada e a grava na pasta de imagens das questões. Devolve o nome do arquivo.

    A largura é limitada para a imagem carregar rápido no celular do aluno e ocupar pouco espaço no
    repositório, sem perder a leitura de texto pequeno. Entre PNG e JPEG de boa qualidade, vale o
    formato que dá o melhor resultado para o tipo de imagem (ver LIMITE_RAZAO_PNG). O nome vem do
    conteúdo, então a mesma imagem enviada duas vezes vira um arquivo só. Levanta ValueError se o
    arquivo não for uma imagem legível.
    """
    try:
        imagem = ImageOps.exif_transpose(Image.open(arquivo))
        if imagem.mode in ("RGBA", "LA", "P"):
            # JPEG não tem transparência: o fundo transparente vira branco.
            imagem = imagem.convert("RGBA")
            fundo = Image.new("RGB", imagem.size, (255, 255, 255))
            fundo.paste(imagem, mask=imagem.getchannel("A"))
            imagem = fundo
        else:
            imagem = imagem.convert("RGB")
        if imagem.width > LARGURA_MAXIMA:
            altura = round(imagem.height * LARGURA_MAXIMA / imagem.width)
            imagem = imagem.resize((LARGURA_MAXIMA, altura), Image.LANCZOS)
        em_png = io.BytesIO()
        imagem.save(em_png, "PNG", optimize=True)
        qualidade = QUALIDADE_JPEG
        em_jpeg = _codificar_jpeg(imagem, qualidade)
        while em_jpeg.tell() > PESO_MAXIMO_JPEG and qualidade > QUALIDADE_JPEG_MINIMA:
            qualidade -= 6
            em_jpeg = _codificar_jpeg(imagem, qualidade)
        # Desenhos, gráficos e capturas de tela com texto ficam bem menores ou pouco maiores em PNG,
        # que é nítido; em fotos o PNG é várias vezes maior que o JPEG.
        if em_png.tell() <= LIMITE_RAZAO_PNG * em_jpeg.tell():
            buffer, extensao = em_png, ".png"
        else:
            buffer, extensao = em_jpeg, ".jpg"
    except Exception as erro:
        raise ValueError("arquivo de imagem inválido") from erro
    dados = buffer.getvalue()
    nome = hashlib.sha1(dados).hexdigest()[:12] + extensao
    os.makedirs(DIR_IMAGENS_GRAVACAO, exist_ok=True)
    with open(os.path.join(DIR_IMAGENS_GRAVACAO, nome), "wb") as f:
        f.write(dados)
    return nome


def caminho_imagem_questao(nome):
    """
    Caminho do arquivo de imagem de uma questão, ou None se não existir. Procura na pasta de dados e
    na pasta que acompanha o código.
    """
    if not nome or os.path.basename(nome) != nome:
        return None  # nome com caminho: ignora, para não sair da pasta de imagens
    for pasta in (DIR_IMAGENS_GRAVACAO, PASTA_IMAGENS):
        caminho = os.path.join(pasta, nome)
        if os.path.isfile(caminho):
            return caminho
    return None
