# Avaliação por Habilidade

Sistema para acompanhar o acerto de cada aluno em cada habilidade (BNCC ou descritores do SAEB/SAETO).
O professor cadastra as questões, os alunos respondem e o painel mostra o acerto por aluno e por habilidade, com relatório em PDF.

Adaptado do sistema Trilha de Aprendizagem, desenvolvido por Wenes Gomes Aquino no TCC de Licenciatura em Computação (UFT/UAB).

## Como rodar

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\streamlit run trilha_aprendizagem.py
```

Senha padrão do painel do professor: `computa258` (troque em Configurações).

## Licença

MIT. As fontes CMU Serif seguem a licença OFL (ver `fonts/OFL.txt`).
