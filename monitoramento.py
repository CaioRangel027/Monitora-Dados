# Importando Bibliotecas
import psutil
import csv
import time
from datetime import datetime

# Função para Coletar o Uso da CPU
def get_uso_cpu():
    return psutil.cpu_percent(interval=1)

# Coletar Uso de Memória
def get_uso_memoria():
    memoria = psutil.virtual_memory()
    return memoria.percent

# Coletar Uso de Disco
def get_uso_disco():
    disco = psutil.disk_usage("/")
    return disco.total, disco.free, disco.used, disco.percent

# Chamar as Funções e Iniciar a Coleta de Dados
uso_cpu = get_uso_cpu()
memoria = get_uso_memoria()
disco = get_uso_disco()

# Exibir os Resultados
print(f"Uso da CPU: {uso_cpu}%")
print(f"Uso da MEMÓRIA: {memoria}%")
print(f"Uso do DISCO: {disco}%")
print(f"Coleta de Dados Iniciada. Tecle CONTROL + C Para Cancelar.")

# Criar Cabeçalho de Arquivo Log CSV
log_file = 'log_monitoramento.log'

with open(log_file, 'w', newline = '')as file:
    gravar = csv.writer(file)
    gravar.writerow(['timestamp', 'uso_cpu', 'memoria', 'disco'])

# Coletar e Gravar Dados a Cada 10 Segundos
try:
    while True:
        with open (log_file, 'a', newline = '') as file:
            data = datetime.now().isoformat()
            gravar = csv.writer(file)
            gravar.writerow([data, uso_cpu, memoria, disco])
            time.sleep(10)

except KeyboardInterrupt:
    print(f"Parando a Coleta de Dados.")