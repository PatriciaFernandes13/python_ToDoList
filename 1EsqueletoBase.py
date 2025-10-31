#FALTA
#Adicionar subtarefas (o que pode ser outra lista de objetos Tarefa dentro da tarefa principal).
#Adicionar comentários.
#Melhorar a interface.
#Salvar e carregar tarefas.
#Tornar os avisos mais visuais (ex: cores no terminal).


import time
from datetime import datetime, timedelta

class Tarefa:
    def __init__(self, titulo, prioridade='Média', etiquetas=None, prazo=None, recorrencia=None, comentarios=None, subtarefas=None):
        self.titulo = titulo
        self.prioridade = prioridade.capitalize()  # 'Alta', 'Média', 'Baixa'
        self.etiquetas = etiquetas if etiquetas else []
        self.prazo = prazo  # tipo datetime
        self.recorrencia = recorrencia.lower()  # 'diaria', 'semanal', None
        self.comentarios = comentarios if comentarios else []
        self.subtarefas = subtarefas if subtarefas else []
        self.concluida = False

    def __str__(self):
        status = "✓" if self.concluida else " "
        prazo_str = self.prazo.strftime("%Y-%m-%d") if self.prazo else "Sem data de concusão prevista."
        return f"[{status}] {self.titulo} (Prioridade: {self.prioridade}, Prazo: {prazo_str}, Etiquetas: {', '.join(self.etiquetas)})"

class GestorTarefas:
    def __init__(self):
        self.tarefas = []
        self.historico = [] #armaneza ações para o undo

    def adicionar_tarefa(self, tarefa):
        self.tarefas.append(tarefa)
        self.historico.append(('adicionar', tarefa))
        print("Tarefa adicionada com sucesso!")

    def listar_tarefas(self, filtro_etiqueta=None):
        tarefas_filtradas = self.tarefas
        if filtro_etiqueta:
            tarefas_filtradas = [t for t in self.tarefas if filtro_etiqueta in t.etiquetas]
        
        # Ordenar por prioridade: Alta > Média > Baixa
        prioridade_ordem = {'Alta': 1, 'Média': 2, 'Baixa': 3}
        tarefas_filtradas.sort(key=lambda x: prioridade_ordem.get(x.prioridade, 4))

        for i, t in enumerate(tarefas_filtradas):
            aviso = ""
            if t.prazo:
                dias_restantes = (t.prazo - datetime.now()).days
                if dias_restantes < 0:
                    aviso = " [ATRASADA!]"
                elif dias_restantes <= 3:
                    aviso = " [Prazo Próximo]"
            print(f"{i+1}. {t}{aviso}")

    def concluir_tarefa(self, indice):
        try:
            tarefa = self.tarefas[indice]
            tarefa.concluida = True
            self.historico.append(('Concluir', tarefa))
            # Se for recorrente, criar nova tarefa para próxima data
            if tarefa.recorrencia:
                nova_data = None
                if tarefa.recorrencia == 'diaria':
                    nova_data = tarefa.prazo + timedelta(days=1) if tarefa.prazo else None
                elif tarefa.recorrencia == 'semanal':
                    nova_data = tarefa.prazo + timedelta(weeks=1) if tarefa.prazo else None
                if nova_data:
                    nova_tarefa = Tarefa(titulo=tarefa.titulo, prioridade=tarefa.prioridade,
                                         etiquetas=tarefa.etiquetas, prazo=nova_data,
                                         recorrencia=tarefa.recorrencia, comentarios=tarefa.comentarios,
                                         subtarefas=[])
                    self.adicionar_tarefa(nova_tarefa)
            print("Tarefa marcada como concluída!")
        except IndexError:
            print("Índice inválido.")

    def remover_tarefa(self, indice):
        try:
            tarefa = self.tarefas.pop(indice)
            self.historico.append(('remover', tarefa))
            print(f"Tarefa {tarefa.titulo} removida.")
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
        elif acao == 'remover':
            self.tarefas.append(tarefa)
            print(f"Ação desfeita: tarefa {tarefa.titulo} removida adicionada de volta.")
        elif acao == 'concluir':
            tarefa.concluida = False
            print(f"Ação desfeita: tarefa {tarefa.titulo} marcada como não concluída.")

    def iniciar_pomodoro(self, minutos=25):
        print(f"A iniciar Pomodoro de {minutos} minutos. Foca na tarefa!")
        try:
            for i in range(minutos * 60):
                time.sleep(1)
                if i % 60 == 0:
                    print(f"Tempo passado: {i//60} minutos")
            print("Pomodoro terminado! Hora de fazer uma pausa.")
        except KeyboardInterrupt:
            print("\nPomodoro interrompido.")

def main():
    gestor = GestorTarefas()

    while True:
        print("\n--- Gestor de Tarefas ---")
        print("1. Adicionar nova tarefa")
        print("2. Listar tarefas (todas ou por etiqueta)")
        print("3. Concluir tarefa")
        print("4. Remover tarefa")
        print("5. Desfazer última ação")
        print("6. Iniciar Temporizador Pomodoro")
        print("0. Sair")
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            titulo = input("Título da tarefa: ")
            prioridade = input("Prioridade (Alta/Média/Baixa): ")
            if prioridade not in ['Alta', 'Média', 'Baixa']:
                prioridade = 'Média' #padrão
            etiquetas = input("Etiquetas (separadas por vírgula), ex: trabalho, estudo, casa...: ").split(",")
            prazo_str = input("Prazo (AAAA-MM-DD) ou vazio: ").strip()
            prazo = None
            if prazo_str:
                try:
                    prazo= datetime.strptime(prazo_str, "%Y-%m-%d")
                except ValueError:
                    print("Formato de data inválido. O prazo será ignorado.")
            recorrencia = input("Recorrência (diaria/semanal/não): ")
            recorrencia = recorrencia if recorrencia in ['diaria', 'semanal'] else None
            tarefa = Tarefa(titulo=titulo.strip(),
                            prioridade=prioridade.strip().capitalize(),
                            etiquetas=[e.strip() for e in etiquetas if e.strip()],
                            prazo=prazo,
                            recorrencia=recorrencia)
            gestor.adicionar_tarefa(tarefa)

        elif escolha == '2':
            filtro = input("Filtrar por etiqueta (deixe vazio para todas): ")
            gestor.listar_tarefas(filtro_etiqueta=filtro.strip() if filtro else None)

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
            minutos = input("Duração do Pomodoro (minutos, padrão 25): ")
            minutos = int(minutos) if minutos.isdigit() else 25
            gestor.iniciar_pomodoro(minutos)

        elif escolha == '0':
            print("Programa encerrado. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
