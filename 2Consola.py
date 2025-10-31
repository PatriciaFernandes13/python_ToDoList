import time
from datetime import datetime, timedelta
import json
import pandas as pd
from tkinter.filedialog import asksaveasfilename

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
    def __init__(self, arquivo_json="tarefas.json"):
        
        self.tarefas = []
        self.historico = [] # armaneza ações para o desfazer
        self.arquivo_json = arquivo_json
        self.carregar_dados()

    def adicionar_tarefa(self, tarefa):
        for t in self.tarefas: #Verifica duplicados (título igual)
            if t.titulo.lower() == tarefa.titulo.lower():
                resposta = input(f"Tarefa Duplicada. Já existe uma tarefa chamada '{tarefa.titulo}'.\n Se deseja continuar prima '1'?")
                if resposta != '1':
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
                    return

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
        except IndexError:
            print("Índice inválido.")

    def remover_tarefa(self, indice):
        try:
            tarefa = self.tarefas.pop(indice)
            self.historico.append(('remover', tarefa))
            print(f"Tarefa '{tarefa.titulo}' removida.")
            self.salvar_dados()  # salva imediatamente
        except IndexError:
            print("Índice inválido.")

    def desfazer_ultima_acao(self):
        if not self.historico:
            print("Nada para desfazer.")
            return
        acao, tarefa = self.historico.pop()
        if acao == 'adicionar':
            self.tarefas.remove(tarefa)
            print("Ação desfeita: tarefa adicionada removida.")
        elif acao[0] == 'remover':
            _, tarefa, indice = acao
            self.tarefas.insert(indice, tarefa)
            print(f"Ação desfeita: tarefa '{tarefa.titulo}' restaurada na posição original.")
        elif acao == 'concluir':
            tarefa.concluida = False
            print(f"Ação desfeita: tarefa '{tarefa.titulo}' marcada como não concluída.")
        self.salvar_dados()  # salva imediatamente

    def iniciar_temporizador(self, minutos=25):
        print(f"A iniciar Temporizador de {minutos} minutos. Foca na tarefa!")
        try:
            for i in range(minutos * 60):
                time.sleep(1)
                if i % 60 == 0:
                    print(f"Tempo passado: {i//60} minutos")
            print("Temporizador terminado! Hora de fazer uma pausa.")
        except KeyboardInterrupt:
            print("\nTemporizador interrompido.")

# metodos para subtarefas
    def adicionar_subtarefa(self, indice_tarefa_principal, titulo_subtarefa):
        try:
            tarefa_principal = self.tarefas[indice_tarefa_principal]
            for sub in tarefa_principal.subtarefas:
                if sub.titulo.lower() == titulo_subtarefa.lower():
                    resposta = input(f"Já existe uma subtarefa chamada '{titulo_subtarefa}' nesta tarefa. Se deseja continuar prima 1: ").strip().lower()
                    if resposta != '1':
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
        data = {
            "tarefas": [t.to_dict() for t in self.tarefas],
            "historico": [
                {"acao": acao, "tarefa": t.to_dict()} for acao, t in self.historico
            ]
        }
        with open(self.arquivo_json, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def carregar_dados(self):
        try:
            with open(self.arquivo_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.tarefas = [Tarefa.from_dict(t) for t in data.get("tarefas", [])]
                self.historico = [
                    (h["acao"], Tarefa.from_dict(h["tarefa"])) for h in data.get("historico", [])
                ]
        except FileNotFoundError:
            self.tarefas = []
            self.historico = []

    #Exporta para Excel todas as tarefas e subtarefas, incluindo comentários, etiquetas e indicando tarefa principal
    def exportar_para_excel(self, arquivo_excel="ListaTarefas.xlsx"):
        if not arquivo_excel.endswith(".xlsx"): #guarda extenção xlsx
            arquivo_excel += ".xlsx"
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
        print("13. Exportar lista de tarefas para Excel")
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

        elif escolha == '13':
            arquivo_excel = input("Nome do arquivo Excel a exportar (padrão ListaTarefas.xlsx): ").strip()
            arquivo_excel = arquivo_excel if arquivo_excel else "ListaTarefas.xlsx"
            if not arquivo_excel.endswith(".xlsx"):
                arquivo_excel += ".xlsx"
            gestor.exportar_para_excel(arquivo_excel)      

        elif escolha == '0':
            print("Programa encerrado. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    gestor = GestorTarefas()
    try:
        main()
    finally:
        gestor.salvar_dados() # Garante que os dados são salvos ao sair
