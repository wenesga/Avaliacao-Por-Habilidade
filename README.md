# 🎯 Avaliação por Habilidade

> *Saber **em qual habilidade** cada aluno precisa de ajuda, e não só a nota da turma.*

Sistema web com atividades gamificadas de prática para o SAETO (Matemática e Português). Os alunos respondem, pelo celular, tablet ou computador, a questões de provas anteriores ligadas aos descritores da prova, com pontuação. O painel do professor mostra, em tempo real, o acerto de cada aluno em cada descritor, para identificar quem tem defasagem e em qual habilidade e fazer o reforço antes da prova real.

📌 *Protótipo de proposta de intervenção do Estágio Supervisionado IV (Gestão Escolar), Licenciatura em Computação, UFT/UAB.*

---

## ✨ O que ele faz

- 📝 **Questões por descritor**: o professor adiciona cada questão direto em Matemática ou Português (múltipla escolha ou resposta única) e a liga a um ou mais descritores do SAETO (como `D044_M`), escolhidos numa lista pesquisável.
- 📱 **Resposta com correção na hora**: o aluno entra com um apelido, responde e já sabe se acertou.
- 🟢🟡🔴 **Tabela de acerto por habilidade**: um aluno por linha, um descritor por coluna, nas 4 faixas da escola:
  - 🔴 **Baixo**: até 40%;
  - 🟠 **Médio baixo**: de 41% a 60%;
  - 🟡 **Médio alto**: de 61% a 79%;
  - 🟢 **Alto**: 80% ou mais.
- 🗓️ **Filtros** por período e por disciplina (Matemática ou Português).
- 👥 **Linha da turma**: o acerto da turma inteira em cada habilidade, no topo da tabela.
- 📄 **Relatório em PDF**: exportado por conteúdo, pronto para imprimir ou levar à reunião pedagógica.

## 🛣️ Próximos passos

- 🧪 Piloto com o **8º ano, em Matemática**.
- 🗓️ Usar as datas reais dos bimestres da escola no filtro de período.

## 🚀 Como rodar

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\streamlit run app.py
```

🔑 Senha padrão do painel do professor: `computa258`. *Troque em Configurações.*

## 🙌 Origem

Adaptado da **Trilha de Aprendizagem**, sistema gamificado para o ensino de Estatística desenvolvido por **Wenes Gomes Aquino** no TCC de Licenciatura em Computação (UFT/UAB).

## 📜 Licença

**MIT**. As fontes CMU Serif seguem a licença OFL (ver `fonts/OFL.txt`).
