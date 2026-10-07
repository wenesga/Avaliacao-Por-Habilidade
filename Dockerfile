FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Título, descrição e imagem da prévia do link (WhatsApp etc. leem só o HTML base do Streamlit).
RUN f=$(python -c "import streamlit,os;print(os.path.join(os.path.dirname(streamlit.__file__),'static','index.html'))") \
 && sed -i 's|<title>Streamlit</title>|<title>Avaliação por Habilidade</title><meta name="description" content="Acerto de cada aluno por habilidade, em Matemática e Português" /><meta property="og:type" content="website" /><meta property="og:title" content="Avaliação por Habilidade" /><meta property="og:description" content="Acerto de cada aluno por habilidade, em Matemática e Português" /><meta property="og:image" content="https://trilhaestatistica.com.br/app/static/previa.png" /><meta property="og:image:width" content="512" /><meta property="og:image:height" content="512" />|' "$f" \
 && grep -q "og:title" "$f"

COPY *.py descritores_saeto.json ./
COPY paginas ./paginas
COPY .streamlit ./.streamlit
COPY fonts ./fonts
COPY imagens ./imagens
COPY static ./static

# Valores iniciais: só são copiados pro volume se ele ainda não tiver o arquivo.
COPY conteudos.json config_sistema.json ./seed/

COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

ENV TRILHA_DIR_DADOS=/data
EXPOSE 8080
CMD ["./docker-entrypoint.sh"]
