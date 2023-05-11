import socket
import numpy as np
import random as rnd
import threading

# Función para generar un tablero de parejas
def tableroparejas(n):
    fichasunicas = (n*n)//2
    tablero = np.zeros(shape=(n,n),dtype=int)
    i = 1
    while i <= fichasunicas:
        f1 = int(rnd.random()*n)
        c1 = int(rnd.random()*n)
        while not(tablero[f1,c1] == 0):
            f1 = int(rnd.random()*n)
            c1 = int(rnd.random()*n)
        tablero[f1,c1] = i
        f2 = int(rnd.random()*n)
        c2 = int(rnd.random()*n)
        while not(tablero[f2,c2] == 0):
            f2 = int(rnd.random()*n)
            c2 = int(rnd.random()*n)
        tablero[f2,c2] = i
        i += 1
    return tablero

def juego_de_memorama(conn, addr):
    # Generar tablero de parejas
    tablero = tableroparejas(4)

    # Enviar tablero de parejas al cliente
    tablero_serializado = tablero.tostring()
    conn.sendall(tablero_serializado)

    # Inicializar matriz descubiertas
    descubiertas = np.zeros(shape=(4, 4), dtype=int)
    encontrado = 0
    intentos_fallidos = 0

    # Juego de memorama
    while encontrado < (4 * 4) // 2 and intentos_fallidos < 10:
        # Esperar a recibir datos del cliente (coordenadas de fichas seleccionadas)
        data = conn.recv(buffer_size)
        if not data:
            break

        # Decodificar coordenadas de fichas seleccionadas
        f1, c1, f2, c2 = map(int, data.decode().split(","))

        # Verificar si las fichas seleccionadas coinciden
        ficha1 = tablero[f1, c1]
        ficha2 = tablero[f2, c2]

        if ficha1 == ficha2:
            descubiertas[f1, c1] = ficha1
            descubiertas[f2, c2] = ficha2
            encontrado += 2
            print("ENCONTRÓ una pareja..!", ficha1, ficha2)

            # Enviar respuesta al cliente (pareja encontrada)
            response = "encontrado,{},{},{},{}".format(f1, c1, f2, c2).encode()
            conn.sendall(response)
        else:
            intentos_fallidos += 1
            print("Las fichas son diferentes:", ficha1, ficha2)

            # Enviar respuesta al cliente (pareja no encontrada)
            response = "equivocado".encode()
            conn.sendall(response)

        # Enviar estado actual del juego (descubierto o no) al cliente
        estado_juego_serializado = descubiertas.tostring()
        conn.sendall(estado_juego_serializado)

    # Verificar si se encontraron todas las parejas
    if encontrado == (4 * 4) // 2:
        print("¡Muy bien! Todas las fichas fueron encontradas")
        # Enviar respuesta al cliente (juego ganado)
        response = "ganado".encode()
        conn.sendall(response)
    else:
        print("Se alcanzó el límite de intentos fallidos o el juego terminó.")
        # Enviar respuesta al cliente (juego perdido)
        response = "perdido".encode()
        conn.sendall(response)

    # Cerrar conexión con el cliente
    conn.close()

def servirPorSiempre(socketTcp, listaconexiones):
    try:
        while True:
            client_conn, client_addr = socketTcp.accept()
            print("Conectado a", client_addr)
            listaconexiones.append(client_conn)
            thread_game = threading.Thread(target=juego_de_memorama, args=[client_conn, client_addr])
            thread_game.start()
            gestion_conexiones(listaconexiones)
    except Exception as e:
        print(e)

def gestion_conexiones(listaconexiones):
    for conn in listaconexiones:
        if conn.fileno() == -1:
            listaconexiones.remove(conn)
    print("hilos activos:", threading.active_count())
    print("enum", threading.enumerate())
    print("conexiones: ", len(listaconexiones))
    print(listaconexiones)

HOST = "x.x.x.x"  # Dirección de la interfaz de loopback estándar (localhost)
PORT = 55041  # Puerto que usa el cliente  (los puertos sin provilegios son > 1023)
buffer_size = 1024

listaConexiones = []

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
    TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    TCPServerSocket.bind((HOST, PORT))
    TCPServerSocket.listen()
    print("El servidor TCP está disponible y en espera de solicitudes")

    servirPorSiempre(TCPServerSocket, listaConexiones)