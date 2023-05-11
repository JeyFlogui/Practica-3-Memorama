import socket
import numpy as np

# Función para mostrar el tablero de parejas
def mostrar_tablero(tablero, descubiertas):
    for i in range(tablero.shape[0]):
        for j in range(tablero.shape[1]):
            if descubiertas[i, j] == 0:
                print(" * ", end="")
            else:
                print(" {} ".format(tablero[i, j]), end="")
        print()

PORT = 55041
buffer_size = 1024

print("Introduce la dirección IP del servidor")
HOST = input()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPClientSocket:
    TCPClientSocket.connect((HOST, PORT))
    print("Conectado al servidor")

    # Recibir tablero de parejas del servidor
    data = TCPClientSocket.recv(buffer_size)
    tablero = np.frombuffer(data, dtype=int).reshape((4, 4))

    # Mostrar tablero de parejas al usuario
    descubiertas = np.zeros(shape=(4, 4), dtype=int)
    mostrar_tablero(tablero, descubiertas)

    encontrado = 0
    while encontrado < (4 * 4) // 2:

        # Seleccionar dos fichas del tablero
        print("Introduce las coordenadas de dos fichas (fila1,columna1,fila2,columna2):")
        f1, c1, f2, c2 = map(int, input().split(","))

        # Enviar coordenadas de las fichas seleccionadas al servidor
        data = "{},{},{},{}".format(f1, c1, f2, c2).encode()
        TCPClientSocket.sendall(data)

        # Esperar respuesta del servidor
        data = TCPClientSocket.recv(buffer_size)
        if not data:
            break

        # Decodificar respuesta del servidor
        response = data.decode()
        if response.startswith("encontrado"):
            _, f1, c1, f2, c2 = response.split(",")
            f1, c1, f2, c2 = int(f1), int(c1), int(f2), int(c2)
            descubiertas[f1, c1] = tablero[f1, c1]
            descubiertas[f2, c2] = tablero[f2, c2]
            encontrado += 2
        elif response.startswith("equivocado"):
            print("Las fichas no coinciden")
        elif response.startswith("ganado"):
            print("¡Muy bien! Todas las fichas fueron encontradas")
            encontrado = (4 * 4) // 2
        elif response.startswith("perdido"):
            print("Se alcanzó el límite de intentos fallidos o el juego terminó.")
            encontrado = (4 * 4) // 2
        else:
            print("Respuesta no reconocida")

        # Mostrar estado del juego al usuario
        mostrar_tablero(tablero, descubiertas)

    # Recibir estado final del juego del servidor
    data = TCPClientSocket.recv(buffer_size)
    descubiertas = np.frombuffer(data, dtype=int).reshape((4, 4))
    mostrar_tablero(tablero, descubiertas)

    # Cerrar conexión con el servidor
    TCPClientSocket.close()