# 🎯 Avaliação por Habilidade

> *Saber **em qual habilidade** cada aluno precisa de ajuda, e não só a nota da turma.*

Sistema web para o professor acompanhar o **acerto de cada aluno em cada habilidade da BNCC**. Os alunos respondem às questões pelo celular, tablet ou computador, e o painel do professor mostra, em tempo real, quem está bem e quem precisa de reforço.

📌 *Protótipo de proposta de intervenção do Estágio Supervisionado IV (Gestão Escolar), Licenciatura em Computação, UFT/UAB.*

---

## ✨ O que ele faz

- 📝 **Questões por habilidade**: o professor cadastra as questões e liga cada uma a uma habilidade da BNCC, escolhida numa lista pesquisável.
- 📱 **Resposta com correção na hora**: o aluno entra com um apelido, responde e já sabe se acertou.
- 🟢🟡🔴 **Tabela de acerto por habilidade**: um aluno por linha, uma habilidade por coluna, com cores:
  - 🟢 **verde**: a partir de 70%;
  - 🟡 **amarelo**: de 40% a 69%;
  - 🔴 **vermelho**: abaixo de 40%.
- 👥 **Linha da turma**: o acerto da turma inteira em cada habilidade, no topo da tabela.
- 📄 **Relatório em PDF**: exportado por conteúdo, pronto para imprimir ou levar à reunião pedagógica.

## 🛣️ Próximos passos

- 🏫 Aceitar os **descritores do SAEB/SAETO**, usados pela escola nas avaliações diagnósticas.
- 🗓️ Filtrar por **período** (quinzena e bimestre) e por **disciplina**.
- 🧪 Piloto com o **8º ano, em Matemática**.

## 🚀 Como rodar

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\streamlit run trilha_aprendizagem.py
```

🔑 Senha padrão do painel do professor: `computa258`. *Troque em Configurações.*

## 🙌 Origem

Adaptado da **Trilha de Aprendizagem**, sistema gamificado para o ensino de Estatística desenvolvido por **Wenes Gomes Aquino** no TCC de Licenciatura em Computação (UFT/UAB).

## 📜 Licença

**MIT**. As fontes CMU Serif seguem a licença OFL (ver `fonts/OFL.txt`).
