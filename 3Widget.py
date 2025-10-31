import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import time
from datetime import datetime, timedelta
import json
import pandas as pd

class Tarefa:
    def __init__(self, titulo, prioridade='Média', etiquetas=None, prazo=None, recorrencia=None, comentarios=None, subtarefas=None):
        self.titulo = titulo.strip() if titulo else "Tarefa sem título"
        self.prioridade = prioridade.capitalize() if prioridade else 'Média' # 'Alta', 'Média', 'Baixa'
        self.etiquetas = etiquetas if etiquetas else []
        self.prazo = prazo  # tipo datetime
        self.recorrencia = recorrencia.lower() if recorrencia else None  # 'diaria', 'semanal', None
        self.comentarios = comentarios if comentarios else []
        self.subtarefas = subtarefas if subtarefas else []
        self.concluida = False

    def __str__(self, nivel=0):
        indent = "  " * nivel
        status = "✓" if self.concluida else " "
        prazo_str = self.prazo.strftime("%Y-%m-%d") if self.prazo else "Sem data de conclusão prevista."
        # Gerar string das subtarefas, se existirem
        subtarefas_str = "\n".join([sub.__str__(nivel + 1) for sub in self.subtarefas])
        base_str = f"{indent}[{status}] {self.titulo} (Prioridade: {self.prioridade}, Prazo: {prazo_str}, Etiquetas: {', '.join(self.etiquetas)})"
        return f"{base_str}\n{subtarefas_str}" if subtarefas_str else base_str

    def verificar_conclusao(self):
        # A tarefa só é concluída se todas as subtarefas estiverem concluídas (se houver subtarefas)
        if self.subtarefas:
            self.concluida = all(sub.concluida for sub in self.subtarefas)
        return self.concluida
    
    def to_dict(self): #Converter tarefa em dict para JSON
        return {
            "titulo": self.titulo,
            "prioridade": self.prioridade,
            "etiquetas": self.etiquetas,
            "prazo": self.prazo.strftime("%Y-%m-%d") if self.prazo else None,
            "recorrencia": self.recorrencia,
            "comentarios": self.comentarios,
            "subtarefas": [sub.to_dict() for sub in self.subtarefas],
            "concluida": self.concluida
        }

    @staticmethod
    def from_dict(data):
        prazo = datetime.strptime(data["prazo"], "%Y-%m-%d") if data.get("prazo") else None
        subtarefas = [Tarefa.from_dict(sub) for sub in data.get("subtarefas", [])]
        recorrencia = data.get("recorrencia")
        if recorrencia:
            recorrencia = recorrencia.lower()  # padronizar
        tarefa = Tarefa(
            titulo=data.get("titulo"),
            prioridade=data.get("prioridade"),
            etiquetas=data.get("etiquetas"),
            prazo=prazo,
            recorrencia=data.get("recorrencia"),
            comentarios=data.get("comentarios"),
            subtarefas=subtarefas
        )
        tarefa.concluida = data.get("concluida", False)
        return tarefa

class GestorTarefas:
    def __init__(self, arquivo_json="BaseDados.json"):
        self.tarefas = []
        self.historico = [] # armaneza ações para o desfazer
        self.arquivo_json = arquivo_json
        self.carregar_dados()
    
    def adicionar_tarefa(self, tarefa): 
        for t in self.tarefas: #Verifica duplicados (título igual)
            if t.titulo.lower() == tarefa.titulo.lower():
                resposta = messagebox.askyesno("Tarefa Duplicada", f"Já existe uma tarefa chamada '{tarefa.titulo}'.\nDeseja continuar?")
                if not resposta:
                    print("Operação cancelada pelo utilizador.")
                    return  # não adiciona
        self.tarefas.append(tarefa)
        self.historico.append(('adicionar', tarefa))
        print("Tarefa adicionada com sucesso!")
        self.salvar_dados()  # salva imediatamente

    def listar_tarefas(self, filtro_etiqueta=None, mostrar_comentarios=False):
        tarefas_filtradas = self.tarefas
        if filtro_etiqueta:
            tarefas_filtradas = [t for t in self.tarefas if filtro_etiqueta in t.etiquetas]
        
        # Ordenar por prioridade: Alta > Média > Baixa
        prioridade_ordem = {'Alta': 1, 'Média': 2, 'Baixa': 3}
        tarefas_filtradas.sort(key=lambda x: prioridade_ordem.get(x.prioridade, 4))
        if not tarefas_filtradas: 
            print("Nenhuma tarefa encontrada.")
            return
        for i, t in enumerate(tarefas_filtradas):
            aviso = "" #Avisos de prazo
            if t.prazo:
                dias_restantes = (t.prazo - datetime.now()).days
                if dias_restantes < 0:
                    aviso = " [ATRASADA!]"
                elif dias_restantes <= 3:
                    aviso = " [Prazo Próximo]"
            print(f"{i+1}. {t}{aviso}")

            if mostrar_comentarios and t.comentarios:
                print("   Comentários:")
                for j, comentario in enumerate(t.comentarios):
                    print(f"     {j+1}. {comentario}")

    def concluir_tarefa(self, indice):
        try:
            tarefa = self.tarefas[indice]
            # Se tiver subtarefas, verificar se todas estão concluídas
            if tarefa.subtarefas:
                if not tarefa.verificar_conclusao():
                    print("Não é possível concluir esta tarefa principal pois há subtarefas pendentes.")
                    return False
            tarefa.concluida = True
            self.historico.append(('concluir', tarefa))
            # Se for recorrente, criar nova tarefa para próxima data
            if tarefa.recorrencia:
                nova_data = None
                if tarefa.recorrencia == 'diaria':
                    nova_data = tarefa.prazo + timedelta(days=1) if tarefa.prazo else None
                elif tarefa.recorrencia == 'semanal':
                    nova_data = tarefa.prazo + timedelta(weeks=1) if tarefa.prazo else None
                if nova_data:
                    nova_tarefa = Tarefa(titulo=tarefa.titulo, prioridade=tarefa.prioridade,
                                         etiquetas=list(tarefa.etiquetas), prazo=nova_data,
                                         recorrencia=tarefa.recorrencia, comentarios=list(tarefa.comentarios),
                                         subtarefas=[])
                    self.adicionar_tarefa(nova_tarefa)
            print("Tarefa marcada como concluída!")
            self.salvar_dados()  # salva imediatamente
            return True
        except IndexError:
            print("Índice inválido.")
            return False

    def remover_tarefa(self, indice):
        try:
            tarefa = self.tarefas.pop(indice)
            self.historico.append(('remover', tarefa, indice))
            print(f"Tarefa '{tarefa.titulo}' removida.")
            self.salvar_dados()  # salva imediatamente
        except IndexError:
            print("Índice inválido.")

    def desfazer_ultima_acao(self):
        if not self.historico:
            print("Nada para desfazer.")
            return None        
        ultimo = self.historico.pop()
        if ultimo[0] == 'adicionar':
            _, tarefa = ultimo
            self.tarefas.remove(tarefa)
            print(f"Ação desfeita: tarefa '{tarefa.titulo}' removida.")
            self.salvar_dados()
            return ("adicionar", tarefa)
        elif ultimo[0] == 'remover':
            _, tarefa, indice = ultimo
            self.tarefas.insert(indice, tarefa)
            print(f"Ação desfeita: tarefa '{tarefa.titulo}' restaurada.")
            self.salvar_dados()
            return ("remover", tarefa)
        elif ultimo[0] == 'concluir':
            _, tarefa = ultimo
            tarefa.concluida = False
            print(f"Ação desfeita: tarefa '{tarefa.titulo}' marcada como não concluída.")
            self.salvar_dados()
            return ("concluir", tarefa)
        return None

    def iniciar_temporizador(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para Temporizador.")
            return
        indice = int(selecionado[0])
        tarefa = self.gestor.tarefas[indice]
        minutos = simpledialog.askinteger("Temporizador", "Duração do Temporizador (minutos):", initialvalue=25, minvalue=1)
        if not minutos:
            return
        segundos = minutos * 60
        def finalizar_temporizador():
            messagebox.showinfo("Temporizador", f"Temporizador concluído para a tarefa '{tarefa.titulo}'!")
        self.root.after(segundos * 1000, finalizar_temporizador)
        messagebox.showinfo("Temporizador", f"Temporizador de {minutos} minutos iniciado para '{tarefa.titulo}'.")

# metodos para subtarefas
    def adicionar_subtarefa(self, indice_tarefa_principal, titulo_subtarefa):
        try:
            tarefa_principal = self.tarefas[indice_tarefa_principal]
            for sub in tarefa_principal.subtarefas: #Verifica duplicados (título igual)
                if sub.titulo.strip().lower() == titulo_subtarefa.strip().lower():
                    resposta = messagebox.askyesno(title="Subtarefa Duplicada",
                                                   message=f"Já existe uma subtarefa chamada '{sub.titulo}'.\nDeseja continuar?")
                    if not resposta:
                        print("Operação cancelada pelo utilizador.")
                        return  # não adiciona
            subtarefa = Tarefa(titulo_subtarefa)
            tarefa_principal.subtarefas.append(subtarefa)
            print(f"Subtarefa '{titulo_subtarefa}' adicionada à tarefa '{tarefa_principal.titulo}'.")
            self.salvar_dados()  # salva imediatamente
        except IndexError:
            print("Índice da tarefa principal inválido.")

    def listar_subtarefas(self, indice_tarefa_principal):
        try:
            tarefa_principal = self.tarefas[indice_tarefa_principal]
            if not tarefa_principal.subtarefas:
                print("Esta tarefa principal não tem subtarefas.")
                return
            print(f"Subtarefas da tarefa '{tarefa_principal.titulo}':")
            for i, sub in enumerate(tarefa_principal.subtarefas):
                status = "✓" if sub.concluida else " "
                print(f"  {i+1}. [{status}] {sub.titulo}")
        except IndexError:
            print("Índice da tarefa principal inválido.")

    def concluir_subtarefa(self, indice_tarefa_principal, indice_subtarefa):
        try:
            tarefa_principal = self.tarefas[indice_tarefa_principal]
            subtarefa = tarefa_principal.subtarefas[indice_subtarefa]
            subtarefa.concluida = True
            print(f"Subtarefa '{subtarefa.titulo}' concluída.")
            self.salvar_dados()  # salva imediatamente
            # Atualizar status da tarefa principal
            tarefa_principal.verificar_conclusao()
        except IndexError:
            print("Índice inválido para tarefa principal ou subtarefa.")

# metodos para comentários
    def adicionar_comentario(self, indice_tarefa, comentario):
        try:
            tarefa = self.tarefas[indice_tarefa]
            tarefa.comentarios.append(comentario.strip())
            print(f"Comentário adicionado à tarefa '{tarefa.titulo}'.")
            self.salvar_dados()  # salva imediatamente
        except IndexError:
            print("Índice da tarefa inválido.")

    def listar_comentarios(self, indice_tarefa):
        try:
            tarefa = self.tarefas[indice_tarefa]
            if not tarefa.comentarios:
                print("Esta tarefa não tem comentários.")
                return
            print(f"Comentários da tarefa '{tarefa.titulo}':")
            for i, c in enumerate(tarefa.comentarios):
                print(f"  {i+1}. {c}")
        except IndexError:
            print("Índice da tarefa inválido.")

    def remover_comentario(self, indice_tarefa, indice_comentario):
        try:
            tarefa = self.tarefas[indice_tarefa]
            comentario_removido = tarefa.comentarios.pop(indice_comentario)
            print(f"Comentário removido: '{comentario_removido}'")
            self.salvar_dados()  # salva imediatamente
        except IndexError:
            print("Índice da tarefa ou comentário inválido.")

    def salvar_dados(self):
        dados = {
            "tarefas": [t.to_dict() for t in self.tarefas],
            "historico": []
        }
        for item in self.historico:
            if item[0] == "remover":
                acao, tarefa, indice = item
                dados["historico"].append({
                    "acao": acao,
                    "tarefa": tarefa.to_dict(),
                    "indice": indice
                })
            else:
                acao, tarefa = item
                dados["historico"].append({
                    "acao": acao,
                    "tarefa": tarefa.to_dict()
                })
        with open(self.arquivo_json, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)

    def carregar_dados(self):
        try:
            with open(self.arquivo_json, "r", encoding="utf-8") as f:
                dados = json.load(f)
                self.tarefas = [Tarefa.from_dict(t) for t in dados.get("tarefas", [])]
                self.historico = []
                for h in dados.get("historico", []):
                    tarefa = Tarefa.from_dict(h["tarefa"])
                    if h["acao"] == "remover":
                        self.historico.append((h["acao"], tarefa, h["indice"]))
                    else:
                        self.historico.append((h["acao"], tarefa))
        except FileNotFoundError:
            self.tarefas = []
            self.historico = []

    #Exporta para Excel todas as tarefas e subtarefas, incluindo comentários, etiquetas e indicando tarefa principal
    def exportar_para_excel(self, arquivo_excel="ListaTarefas.xlsx"):
        dados = []
        for t in self.tarefas:
            dados.append({ # Tarefa principal
                "Tarefa Principal": t.titulo,
                "Título": t.titulo,
                "Prioridade": t.prioridade,
                "Prazo": t.prazo.strftime("%Y-%m-%d") if t.prazo else None,
                "Concluída": t.concluida,
                "Etiquetas": ", ".join(t.etiquetas),
                "Comentários": "\n".join(t.comentarios) if t.comentarios else "",
                "Tipo": "Tarefa Principal"
            })   
            for sub in t.subtarefas: # Subtarefas
                dados.append({
                    "Tarefa Principal": t.titulo,
                    "Título": sub.titulo,
                    "Prioridade": sub.prioridade,
                    "Prazo": sub.prazo.strftime("%Y-%m-%d") if sub.prazo else None,
                    "Concluída": sub.concluida,
                    "Etiquetas": ", ".join(sub.etiquetas),
                    "Comentários": "\n".join(sub.comentarios) if sub.comentarios else "",
                    "Tipo": "Subtarefa"
                })
        df = pd.DataFrame(dados)
        df.to_excel(arquivo_excel, index=False)
        print(f"Exportado para {arquivo_excel} com sucesso!")

def main():
    gestor = GestorTarefas()
    while True:
        print("\n--- Gestor de Tarefas ---")
        print("1. Adicionar nova tarefa")
        print("2. Listar tarefas (todas ou por etiqueta)")
        print("3. Concluir tarefa")
        print("4. Remover tarefa")
        print("5. Desfazer última ação")
        print("6. Iniciar Temporizador")
        print("7. Adicionar subtarefa a uma tarefa")
        print("8. Listar subtarefas de uma tarefa")
        print("9. Concluir subtarefa")
        print("10. Adicionar comentário a uma tarefa")
        print("11. Listar comentários de uma tarefa")
        print("12. Remover comentário de uma tarefa")
        print("0. Sair")
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            titulo = input("Título da tarefa: ")
            prioridade = input("Prioridade (Alta/Média/Baixa): ").strip().capitalize()
            if prioridade not in ['Alta', 'Média', 'Baixa']:
                prioridade = 'Média' #padrão
            etiquetas = [e.strip() for e in input("Etiquetas (separadas por vírgula), ex: trabalho, estudo, casa...: ").split(",") if e.strip()]
            prazo_str = input("Prazo (AAAA-MM-DD) ou vazio: ").strip()
            prazo = None
            if prazo_str:
                try:
                    prazo= datetime.strptime(prazo_str, "%Y-%m-%d")
                except ValueError:
                    print("Formato de data inválido. O prazo será ignorado.")
            recorrencia = input("Recorrência (diaria/semanal/não): ").lower().strip()
            recorrencia = recorrencia if recorrencia in ['diaria', 'semanal'] else None
            tarefa = Tarefa(titulo=titulo.strip(),
                            prioridade=prioridade.strip().capitalize(),
                            etiquetas=[e.strip() for e in etiquetas if e.strip()],
                            prazo=prazo,
                            recorrencia=recorrencia)
            gestor.adicionar_tarefa(tarefa)

        elif escolha == '2':
            filtro = input("Filtrar por etiqueta (deixe vazio para todas): ")
            gestor.listar_tarefas(filtro_etiqueta=filtro.strip() if filtro else None, mostrar_comentarios=True)

        elif escolha == '3':
            gestor.listar_tarefas()
            try:
                indice = int(input("Número da tarefa a concluir: ")) - 1
                gestor.concluir_tarefa(indice)
            except ValueError:
                print("Por favor, insira um número válido.")

        elif escolha == '4':
            gestor.listar_tarefas()
            try:
                indice = int(input("Número da tarefa a remover: ")) - 1
                gestor.remover_tarefa(indice)
            except ValueError:
                print("Por favor, insira um número válido.")

        elif escolha == '5':
            gestor.desfazer_ultima_acao()

        elif escolha == '6':
            minutos = input("Duração do Temporizador (minutos, padrão 25): ")
            minutos = int(minutos) if minutos.isdigit() else 25
            gestor.iniciar_temporizador(minutos)

        elif escolha == '7':
            gestor.listar_tarefas()
            try:
                indice = int(input("Número da tarefa principal para adicionar subtarefa: ")) - 1
                titulo_sub = input("Título da subtarefa: ").strip()
                gestor.adicionar_subtarefa(indice, titulo_sub)
            except ValueError:
                print("Por favor, insira um número válido.")

        elif escolha == '8':
            gestor.listar_tarefas()
            try:
                indice = int(input("Número da tarefa principal para listar subtarefas: ")) - 1
                gestor.listar_subtarefas(indice)
            except ValueError:
                print("Por favor, insira um número válido.")

        elif escolha == '9':
            gestor.listar_tarefas()
            try:
                indice_tarefa = int(input("Número da tarefa principal da subtarefa: ")) - 1
                gestor.listar_subtarefas(indice_tarefa)
                indice_sub = int(input("Número da subtarefa a concluir: ")) - 1
                gestor.concluir_subtarefa(indice_tarefa, indice_sub)
            except ValueError:
                print("Por favor, insira um número válido.")

        elif escolha == '10':
            gestor.listar_tarefas()
            try:
                indice = int(input("Número da tarefa para adicionar comentário: ")) - 1
                comentario = input("Digite o comentário: ")
                gestor.adicionar_comentario(indice, comentario)
            except ValueError:
                print("Por favor, insira um número válido.")    

        elif escolha == '11':
            gestor.listar_tarefas()
            try:
                indice = int(input("Número da tarefa para ver comentários: ")) - 1
                gestor.listar_comentarios(indice)
            except ValueError:
                print("Por favor, insira um número válido.")   

        elif escolha == '12':
            gestor.listar_tarefas()
            try:
                indice = int(input("Número da tarefa para remover comentário: ")) - 1
                gestor.listar_comentarios(indice)
                indice_com = int(input("Número do comentário a remover: ")) - 1
                gestor.remover_comentario(indice, indice_com)
            except ValueError:
                print("Por favor, insira um número válido.")         

        elif escolha == '0':
            print("Programa encerrado. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")

#INTERFACE TKINTER
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Tarefas")
        self.root.geometry("1000x500")
        self.gestor = GestorTarefas()
        self.dark_mode = False
        self.frame_main = tk.Frame(root)
        self.frame_main.pack(fill="both", expand=False)
        self.criar_widgets()
        self.configurar_estilo()

    def configurar_estilo(self):
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self.aplicar_tema_claro()

    def aplicar_tema_claro(self):
        self.style.configure("Treeview", background="white", foreground="black", fieldbackground="white")
        self.root.configure(bg="white")
        self.dark_mode = False
        self._aplicar_cores_widgets("white", "black")

    def aplicar_tema_escuro(self):
        self.style.configure("Treeview", background="#2e2e2e", foreground="white", fieldbackground="#2e2e2e")
        self.root.configure(bg="#2e2e2e")
        self.dark_mode = True
        self._aplicar_cores_widgets("#2e2e2e", "white")

    def _aplicar_cores_widgets(self, bg, fg):
        self.frame_comentarios.configure(bg=bg)
        self.label_comentarios.configure(bg=bg, fg=fg)
        self.text_comentarios.configure(bg=bg, fg=fg, insertbackground=fg)

    def alternar_tema(self):
        if self.dark_mode:
            self.aplicar_tema_claro()
        else:
            self.aplicar_tema_escuro()

    def criar_widgets(self):
        # Toolbar
        toolbar = tk.Frame(self.root, bg="gray")
        toolbar.pack(side="top", fill="x")
        btn_add = tk.Button(toolbar, text="Adicionar Tarefa", command=self.adicionar_tarefa)
        btn_add.pack(side="left", padx=5, pady=5)
        btn_concluir = tk.Button(toolbar, text="Concluir", command=self.concluir_tarefa)
        btn_concluir.pack(side="left", padx=5, pady=5)
        btn_remover = tk.Button(toolbar, text="Remover", command=self.remover_tarefa)
        btn_remover.pack(side="left", padx=5, pady=5)
        btn_comentario = tk.Button(toolbar, text="Adicionar Comentário", command=self.adicionar_comentario)
        btn_comentario.pack(side="left", padx=5, pady=5)
        btn_temporizador = tk.Button(toolbar, text="Temporizador", command=self.iniciar_temporizador)
        btn_temporizador.pack(side="left", padx=5, pady=5)
        btn_subtarefa = tk.Button(toolbar, text="Subtarefa", command=self.gerir_subtarefas)
        btn_subtarefa.pack(side="left", padx=5, pady=5)
        btn_tema = tk.Button(toolbar, text="🌗 Tema", command=self.alternar_tema)
        btn_tema.pack(side="right", padx=5, pady=5)
        btn_desfazer = tk.Button(toolbar, text="Desfazer", command=self.desfazer)
        btn_desfazer.pack(side="right", padx=5, pady=5)
        btn_exportar = tk.Button(toolbar, text="Exportar Excel", command=self.exportar_excel)
        btn_exportar.pack(side="left", padx=5, pady=5)
        # Lista de tarefas
        colunas = ("Título", "Prioridade", "Prazo", "Concluída", "Etiquetas")
        self.tree = ttk.Treeview(self.root, columns=colunas, show="headings")
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(fill="both", expand=True)
        #Scrollbar
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        # Comentários
        self.frame_comentarios = tk.Frame(self.root, bg="white")
        self.frame_comentarios.pack(side="bottom", fill="x")
        self.label_comentarios = tk.Label(self.frame_comentarios, text="Comentários:", bg="white")
        self.label_comentarios.pack(anchor="w")
        self.text_comentarios = tk.Text(self.frame_comentarios, height=4)
        self.text_comentarios.pack(fill="x")
        # Evento de seleção
        self.tree.bind("<<TreeviewSelect>>", self.mostrar_comentarios)
        # Tarefas de exemplo no próprio documento 'BaseDados.json'

    def atualizar_lista(self):
        self.tree.delete(*self.tree.get_children())
        for i, tarefa in enumerate(self.gestor.tarefas):
            prazo_str = tarefa.prazo.strftime("%Y-%m-%d") if tarefa.prazo else "-"
            parent_iid = str(i)
            self.tree.insert("", "end", iid=parent_iid, values=(
            tarefa.titulo,
            tarefa.prioridade,
            prazo_str,
            "✓" if tarefa.concluida else " ",
            ", ".join(tarefa.etiquetas)
        ))
        # Inserir subtarefas como filhos
        for j, sub in enumerate(tarefa.subtarefas):
            sub_prazo = sub.prazo.strftime("%Y-%m-%d") if sub.prazo else "-"
            sub_id = f"{i}-{j}"
            self.tree.insert(parent_iid, "end", iid=sub_id, values=(
                f"↳ {sub.titulo}",
                sub.prioridade,
                sub_prazo,
                "✓" if sub.concluida else " ",
                ", ".join(sub.etiquetas)
            ))
    
    def adicionar_tarefa(self):
        titulo = simpledialog.askstring("Nova Tarefa", "Digite o título da tarefa:")
        if not titulo:
            return
        prioridade = simpledialog.askstring("Prioridade", "Defina a prioridade (Alta, Média, Baixa):")
        etiquetas = simpledialog.askstring("Etiquetas", "Digite etiquetas separadas por vírgula:") or ""
        prazo_str = simpledialog.askstring("Prazo", "Digite o prazo (AAAA-MM-DD):")
        recorrencia = simpledialog.askstring("Recorrência", "Digite a recorrência (diária, semanal):")
        # transformar etiquetas em lista
        etiquetas = [e.strip() for e in etiquetas.split(",")] if etiquetas else []
        # converter prazo para datetime
        prazo = None
        if prazo_str:
            try:
                prazo = datetime.strptime(prazo_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Erro", "Formato de data inválido. Use AAAA-MM-DD.")
        # criar tarefa com todos os campos
        nova_tarefa = Tarefa(
            titulo=titulo,
            prioridade=prioridade,
            etiquetas=etiquetas,
            prazo=prazo,
            recorrencia=recorrencia
        )
        self.gestor.adicionar_tarefa(nova_tarefa)
        self.atualizar_lista()

    def editar_tarefa(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione a tarefa principal ou subtarefa.")
            return
        indice = int(selecionado[0])
        if indice >= 100: # É uma subtarefa
            indice_tarefa = indice // 100
            indice_subtarefa = indice % 100
            tarefa = self.gestor.tarefas[indice_tarefa]
            sub = tarefa.subtarefas[indice_subtarefa]
            op = simpledialog.askstring("Subtarefa", "Escolha ação: concluir/editar")
            if not op:
                return
            if op.lower() == "concluir":
                sub.concluida = True
                tarefa.verificar_conclusao()
                messagebox.showinfo("Subtarefa", f"Subtarefa '{sub.titulo}' concluída.")
            elif op.lower() == "editar":
                novo_titulo = simpledialog.askstring("Editar Subtarefa", "Novo título:", initialvalue=sub.titulo)
                nova_prioridade = simpledialog.askstring("Editar Subtarefa", "Nova prioridade (Alta/Média/Baixa):", initialvalue=sub.prioridade)
                nova_prioridade = nova_prioridade.capitalize() if nova_prioridade and nova_prioridade.capitalize() in ["Alta","Média","Baixa"] else sub.prioridade
                novas_etiquetas = simpledialog.askstring("Editar Subtarefa", "Novas etiquetas (separadas por vírgula):", initialvalue=", ".join(sub.etiquetas))
                novas_etiquetas = [e.strip() for e in novas_etiquetas.split(",")] if novas_etiquetas else sub.etiquetas
                novo_prazo_str = simpledialog.askstring("Editar Subtarefa", "Novo prazo (AAAA-MM-DD):", initialvalue=sub.prazo.strftime("%Y-%m-%d") if sub.prazo else "")
                novo_prazo = sub.prazo
                if novo_prazo_str:
                    try:
                        novo_prazo = datetime.strptime(novo_prazo_str, "%Y-%m-%d")
                    except ValueError:
                        messagebox.showwarning("Erro", "Formato de data inválido. O prazo será mantido.")
                nova_recorrencia = simpledialog.askstring("Editar Subtarefa", "Nova recorrência (diária/semanal/mensal/anual):", initialvalue=sub.recorrencia or "")
                sub.titulo = novo_titulo
                sub.prioridade = nova_prioridade
                sub.etiquetas = novas_etiquetas
                sub.prazo = novo_prazo
                sub.recorrencia = nova_recorrencia
                messagebox.showinfo("Subtarefa", f"Subtarefa '{sub.titulo}' editada com sucesso.")
        else: # É tarefa principal
            tarefa = self.gestor.tarefas[indice]
            op = simpledialog.askstring("Subtarefas", "Escolha ação: adicionar/listar/concluir")
            if not op:
                return
            if op.lower() == "editar":
                novo_titulo = simpledialog.askstring("Editar Tarefa", "Novo título:", initialvalue=tarefa.titulo)
                nova_prioridade = simpledialog.askstring("Editar Tarefa", "Nova prioridade (Alta/Média/Baixa):", initialvalue=tarefa.prioridade)
                nova_prioridade = nova_prioridade.capitalize() if nova_prioridade and nova_prioridade.capitalize() in ["Alta","Média","Baixa"] else tarefa.prioridade
                novas_etiquetas = simpledialog.askstring("Editar Tarefa", "Novas etiquetas (separadas por vírgula):", initialvalue=", ".join(tarefa.etiquetas))
                novas_etiquetas = [e.strip() for e in novas_etiquetas.split(",")] if novas_etiquetas else tarefa.etiquetas
                novo_prazo_str = simpledialog.askstring("Editar Tarefa", "Novo prazo (AAAA-MM-DD):", initialvalue=tarefa.prazo.strftime("%Y-%m-%d") if tarefa.prazo else "")
                novo_prazo = tarefa.prazo
                if novo_prazo_str:
                    try:
                        novo_prazo = datetime.strptime(novo_prazo_str, "%Y-%m-%d")
                    except ValueError:
                        messagebox.showwarning("Erro", "Formato de data inválido. O prazo será mantido.")
                nova_recorrencia = simpledialog.askstring("Editar Tarefa", "Nova recorrência (diária/semanal/mensal/anual):", initialvalue=tarefa.recorrencia or "")
                tarefa.titulo = novo_titulo
                tarefa.prioridade = nova_prioridade
                tarefa.etiquetas = novas_etiquetas
                tarefa.prazo = novo_prazo
                tarefa.recorrencia = nova_recorrencia
                messagebox.showinfo("Tarefa", f"Tarefa '{tarefa.titulo}' editada com sucesso.") 
        self.atualizar_lista()

    def remover_tarefa(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para remover.")
            return
        indice = int(selecionado[0])
        if indice >= 100:  # é subtarefa
            messagebox.showwarning("Aviso", "Não é possível remover uma subtarefa diretamente daqui.")
            return
        tarefa = self.gestor.tarefas[indice]
        self.gestor.remover_tarefa(indice)
        messagebox.showinfo("Removida", f"Tarefa '{tarefa.titulo}' removida.")
        self.atualizar_lista()

    def concluir_tarefa(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para concluir.")
            return
        indice = int(selecionado[0])
        if indice >= 100:
            messagebox.showwarning("Aviso", "Selecione a tarefa principal, não uma subtarefa.")
            return
        sucesso = self.gestor.concluir_tarefa(indice)
        if not sucesso:
            messagebox.showwarning("Aviso", "Ainda há subtarefas pendentes.")
        self.atualizar_lista()
    
    def iniciar_temporizador(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para Temporizador.")
            return
        indice = int(selecionado[0])
        tarefa = self.gestor.tarefas[indice]
        minutos = simpledialog.askinteger("Temporizador", "Duração do Temporizador (minutos):", initialvalue=25, minvalue=1)
        if not minutos:
            return
        self.temporizador_segundos = minutos * 60
        self.label_temporizador = tk.Label(self.root, text=f"Temporizador: {minutos}:00", font=("Arial", 12), bg="yellow")
        self.label_temporizador.pack(side="bottom", fill="x")
        self._contagem_regressiva_temporizador(tarefa)

    def _contagem_regressiva_temporizador(self, tarefa):
        minutos, segundos = divmod(self.temporizador_segundos, 60)
        self.label_temporizador.config(text=f"Temporizador: {minutos:02d}:{segundos:02d}")
        if self.temporizador_segundos > 0:
            self.temporizador_segundos -= 1
            self.root.after(1000, lambda: self._contagem_regressiva_temporizador(tarefa))
        else:
            messagebox.showinfo("Temporizador", f"Temporizador concluído para a tarefa '{tarefa.titulo}'!")
            self.label_temporizador.destroy()

    def gerir_subtarefas(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione a tarefa principal.")
            return
        indice = int(selecionado[0])
        if indice >= 100:
            messagebox.showwarning("Aviso", "Selecione a tarefa principal, não uma subtarefa.")
            return
        tarefa = self.gestor.tarefas[indice]
        op = simpledialog.askstring("Subtarefas", "Escolha ação: adicionar/listar/concluir")
        if not op:
            return
        if op.lower() == "adicionar":
            titulo = simpledialog.askstring("Nova Subtarefa", "Título da subtarefa:")
            if titulo: # vai buscar o método do gestor que já tem verificação de duplicados e salva
                self.gestor.adicionar_subtarefa(indice, titulo)
                self.atualizar_lista()
        elif op.lower() == "listar":
            if not tarefa.subtarefas:
                messagebox.showinfo("Subtarefas", "Nenhuma subtarefa.")
            else:
                msg = "\n".join([f"[{'✓' if s.concluida else ' '}] {s.titulo}" for s in tarefa.subtarefas])
                messagebox.showinfo("Subtarefas", msg)
        elif op.lower() == "concluir":
            if not tarefa.subtarefas:
                messagebox.showinfo("Subtarefas", "Nenhuma subtarefa.")
                return
            lista = "\n".join([f"{i+1}. {s.titulo}" for i, s in enumerate(tarefa.subtarefas)])
            escolha = simpledialog.askinteger("Concluir Subtarefa", f"Escolha número:\n{lista}")
            if escolha and 1 <= escolha <= len(tarefa.subtarefas):
                tarefa.subtarefas[escolha-1].concluida = True
                tarefa.verificar_conclusao()
                messagebox.showinfo("Subtarefa", f"Subtarefa '{tarefa.subtarefas[escolha-1].titulo}' concluída.")
        self.atualizar_lista()

    def mostrar_comentarios(self, event=None):
        selecionado = self.tree.selection()
        if not selecionado:
            return
        indice = int(selecionado[0])
        if indice >= 100:  # é subtarefa
            indice_tarefa = indice // 100
            indice_subtarefa = indice % 100
            tarefa = self.gestor.tarefas[indice_tarefa].subtarefas[indice_subtarefa]
        else:  # é tarefa principal
            tarefa = self.gestor.tarefas[indice]
        self.text_comentarios.delete("1.0", "end")
        for c in tarefa.comentarios:
            self.text_comentarios.insert("end", f"- {c}\n")
        
    def adicionar_comentario(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para adicionar comentário.")
            return
        indice = int(selecionado[0])
        if indice >= 100:
            messagebox.showwarning("Aviso", "Selecione a tarefa principal, não uma subtarefa.")
            return
        comentario = simpledialog.askstring("Novo Comentário", "Digite o comentário:")
        if comentario:
            self.gestor.adicionar_comentario(indice, comentario)
            self.mostrar_comentarios()

    def desfazer(self):
        resultado = self.gestor.desfazer_ultima_acao()
        if resultado:
            acao, tarefa = resultado
            messagebox.showinfo("Desfeito", f"Ação '{acao}' desfeita na tarefa '{tarefa.titulo}'.")
        else:
            messagebox.showinfo("Desfeito", "Nada para desfazer.")
        self.atualizar_lista()

    def exportar_excel(self):
        arquivo_excel = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Arquivos Excel", "*.xlsx")],
            title="Salvar tarefas como Excel"
        )
        if not arquivo_excel:  # Usuário cancelou
            return
        try:
            self.gestor.exportar_para_excel(arquivo_excel)
            messagebox.showinfo("Exportação", f"Tarefas exportadas com sucesso para:\n{arquivo_excel}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.gestor.salvar_dados(), root.destroy()))
    root.mainloop()
