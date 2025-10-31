# Gestor de Tarefas em Python (To-Do List)
## 1. Descrição do Projeto
O projeto consiste numa aplicação em Python para gestão de tarefas pessoais (To-Do List). O utilizador pode adicionar, listar, concluir, remover tarefas e gerir subtarefas, comentários, prazos, etiquetas, prioridades e temporizador integrado. Esta aplicação resolve o problema de organização pessoal, permitindo que o utilizador acompanhe prazos, tarefas importantes, mantenha um histórico das ações realizadas e salve automaticamente os dados para evitar perda de informação entre sessões.

### 🎯Destaques Principais
- Definição de prioridade (Alta, Média, Baixa).
- Avisos de tarefas com prazo próximo ou atrasadas.
- Etiquetas para categorizar tarefas e filtragem por etiqueta.
- Histórico de ações para desfazer a última operação.
- Tarefas recorrentes, subtarefas e comentários.
- Temporizador integrado na interface para modo foco.
- Interface gráfica em Tkinter com suporte a modo claro/escuro.
- Salvamento automático em JSON, evitando perda de dados entre sessões.
- Exportação para Excel via Pandas (necessário módulo openpyxl).

## 2. Tecnologias
🐍 Python 3
🖼 Tkinter (GUI)
💾 JSON (armazenamento de dados)
𓊂  Pandas + openpyxl (exportação Excel)

## 3. Instruções de Utilização
1.Certifique-se de que possui Python 3 instalado.
2. O Tkinter já vem incluído na maioria das distribuições Python.
3. Instale o Pandas e numpy: pip install numpy pandas
4. Instale o módulo openpyxl: pip install openpyxl.
5. Execute o programa: python GestorTarefas.py.
6. As tarefas salvas em BaseDados.json serão carregadas automaticamente.
7. Use o GUI (Tkinter) para:
 o Adicionar / Concluir / Remover Tarefas;
 o Gerir Subtarefas e Comentários;
 o Iniciar o Temporizador;
 o Alternar entre tema claro/escuro.

## 4. Funcionalidades Implementadas
- Criar e listar tarefas com título, prioridade, prazo e etiquetas.
- Detetar tarefas duplicadas (pergunta se deseja criar cópia).
- Ordenar por prioridade.
- Filtrar por etiquetas.
- Histórico de ações com opção de desfazer.
- Gestão de tarefas recorrentes (diárias e semanais).
- Temporizador integrado (modo foco).
- Subtarefas e comentários em cada tarefa.
- Salvar dados automaticamente via JSON.
- Interface gráfica com Tkinter (Treeview, botões de ação, comentários integrados, tema claro/escuro).
- Exportar a lista de tarefas para ficheiro Excel (.xlsx) usando Pandas e openpyxl.

## 5. Estrutura e Funcionalidades
### 5.1 Gestão de Prioridades e Prazos
- Definição de prioridade: Alta, Média, Baixa.
- Destaque para tarefas próximas do prazo.
- Avisos para tarefas atrasadas.
### 5.2 Etiquetas e Filtros
- Associação de etiquetas personalizadas.
- Filtragem por etiquetas no terminal e no GUI.
### 5.3 Histórico e “Desfazer”
- Registo de ações: adicionar, remover e concluir.
- Permite desfazer a última ação.
### 5.4 Tarefas Recorrentes
- Criação automática de novas tarefas recorrentes ao concluir uma existente.
### 5.5 Temporizador Integrado
- Temporizador integrado para focar em tarefas durante os minutos desejados.
- Notificações simples de início, término e pausas via ‘messagebox’.
- Contagem em tempo real sem bloquear a interface.
### 5.6 Subtarefas
- Adição, listagem e conclusão de subtarefas para tarefas principais via GUI.
- Conclusão automática da tarefa principal quando todas subtarefas são finalizadas.
### 5.7 Comentários
- Adicionar, listar e remover comentários.
- Exibição em tempo real na interface.
### 5.8 Base de Dados (JSON)
- Todas as tarefas, subtarefas, etiquetas, comentários e histórico são salvos automaticamente num arquivo JSON (‘BaseDados.json’).
- Dados carregados ao iniciar o programa, evitando perdas entre execuções.
### 5.9 Interface Tkinter
- Janela principal com Treeview para listar tarefas.
- Botões para todas as operações principais.
- Campo de comentários integrado.
- Alternância entre tema claro e escuro.
### 5.10 Exportação para Excel
- Permite exportar todas as tarefas para um ficheiro Excel .xlsx.
- Usa Pandas para criar o DataFrame e openpyxl para salvar.
- Método disponível no gestor: exportar_para_excel().
- Diálogo para escolher o ficheiro de destino via asksaveasfilename.

## 6. Estrutura do Projeto
- Classe Tarefa: Representa uma tarefa (atributos: título, prioridade, etiquetas, prazo, recorrência, subtarefas, comentários e estado).
- Classe GestorTarefas: Gere a lista de tarefas, subtarefas, comentários, histórico e integração com JSON.
- Classe App: Interface Tkinter (Treeview, botões, comentários, subtarefas, temporizador, tema claro/escuro).
- Histórico: Lista de ações para suportar a função desfazer.
- Temporizador: integrado ao GUI, não bloqueia a interface e exibe alertas de término.
- Salvar dados em JSON: garante que os dados sejam gravados em disco.

## 7. Funcionalidades Futuras
- Melhorias no temporizador com pausas longas e ciclos:
 o Implementar pausas (ex.: 5 minutos após um Temporizador);
 o Contar ciclos e avisar após 4 Temporizadors para uma pausa longa;
 o Usar threading para permitir ver o tempo enquanto faz outras coisas tarefas.
- Notificações visuais ou sonoras para tarefas urgentes.
- Filtros combinados (prioridade + múltiplas etiquetas).
- Edição de tarefas, subtarefas e comentários via GUI.
- Adicionar o registo da data de conclusão.

## 8. Estrutura de Arquivos:
projeto_GestorTarefas/
├─ 1EsqueletoBase.py     # Interface Terminal Base
├─ 2Consola.py           # Interface Terminal Final
├─ 3Widget.py            # Interface desktop (GUI)
├─ BaseDados.json        # Base de Dados Interface desktop
├─ BaseDadosExemplo.txt  # Exemplos de Base de Dados
├─ tarefas.json          # Base de Dados Interface Terminal
└─ README.pdf            # Documentação
