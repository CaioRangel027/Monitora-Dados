import time
import psutil
import socket
import mysql.connector
from datetime import datetime
import os

# Função Coleta o Hostname
def get_hostname():
    return socket.gethostname()

# Função para Coleta do Usuário Logado
def get_logged_user():
    return os.getlogin()

# Função para Coleta Endereço IPV4
def get_ipv4_address():
    hostname = get_hostname()
    return socket.gethostbyname(hostname)

# Função para Coletar Uso da CPU
def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

# Função para Coletar Uso da Memória
def get_memory_usage():
    memory = psutil.virtual_memory()
    return memory.percent

# Função para Coletar Espaço em Disco e Uso do Disco
def get_disk_usage():
    disk = psutil.disk_usage('/')
    return disk.total, disk.free, disk.used, disk.percent

# Função para Coletar o Tráfego de Rede (kb/s)
def get_network_traffic(prev_data, interval):
    net_io = psutil.net_io_counters()
    bytes_sent_per_sec = (net_io.bytes_sent - prev_data['bytes_sent']) / interval / 1024
    bytes_recv_per_sec = (net_io.bytes_recv - prev_data['bytes_recv']) / interval / 1024
    return bytes_sent_per_sec, bytes_recv_per_sec, net_io.bytes_sent, net_io.bytes_recv

# Função para Conectar ao Banco de Dados MySQL
def connect_db():
    return mysql.connector.connect(
        host = "172.29.152.150",
        user = "coletor",
        password = "coletor",
        database = "senai"
    )

# Função para Inserir os Dados no Banco
def insert_data(cursor, data):
    cursor.execute("""
        INSERT INTO monitoramento (
            timestamp, hostname, ipv4, logged_user, cpu_usage, memory_usage, disk_total, disk_usage, disk_free, disk_percent, kb_sent_per_sec, kb_recv_per_sec
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """,data)

# Intervalo de Coleta em Segundos
interval = 10

# Função para Coletar Dados Iniciais de Rede
net_io_initial = psutil.net_io_counters()
prev_data = {'bytes_sent': net_io_initial.bytes_sent, 'bytes_recv': net_io_initial.bytes_recv}

# Conectar ao Banco de Dados
db_connection = connect_db()
db_cursor = db_connection.cursor()

# Coletar e Inserir Dados no Banco de Dados a Cada 10 Segundos
try:
    while True:
        timestamp = datetime.now()
        hostname = get_hostname()
        logged_user = get_logged_user()  # Coleta o nome de usuário logado
        ipv4_address = get_ipv4_address()
        cpu_usage = get_cpu_usage()
        memory_usage = get_memory_usage()
        total_disk, used_disk, free_disk, percent_disk = get_disk_usage()
        kb_sent_per_sec, kb_recv_per_sec, bytes_sent, bytes_recv = get_network_traffic(prev_data, interval)

        data = (timestamp, hostname, ipv4_address, logged_user, cpu_usage, memory_usage, total_disk, used_disk, free_disk, percent_disk, kb_sent_per_sec, kb_recv_per_sec)
        insert_data(db_cursor, data)
        db_connection.commit()

        # Atualizar os dados anteriores para a próxima coleta
        prev_data['bytes_sent'] = bytes_sent
        prev_data['bytes_recv'] = bytes_recv

        time.sleep(interval)

except KeyboardInterrupt:
    print("Parando a Coleta de Dados.")
finally:
    db_cursor.close()
    db_connection.close()