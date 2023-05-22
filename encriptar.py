import binascii
import sys
import base64
import random
import os
from math import ceil
from decimal import Decimal
 
FIELD_SIZE = 10**5
 
def polynom(x, coefficients):

    point = 0
    for coefficient_index, coefficient_value in enumerate(coefficients[::-1]):
        point += x ** coefficient_index * coefficient_value
    return point
 
 
def coeff(t, secret):

    coeff = [random.randrange(0, FIELD_SIZE) for _ in range(t - 1)]
    coeff.append(secret)
    return coeff
 
 
def generate_shares(n, m, secret):

    coefficients = coeff(m, secret)
    shares = []
 
    for i in range(1, n+1):
        x = random.randrange(1, FIELD_SIZE)
        shares.append((x, polynom(x, coefficients)))
 
    return shares


def main():

    #Ayuda si no se proporciona ningun argumento
    if len(sys.argv) == 1:
        print("Uso: python3 encriptar.py {-b,-f} base64/fichero numPersonas numMinimo")
        print("Ayuda:  -h, --help       muestra este mensaje de ayuda y sale")
        sys.exit(1)

    #Ayuda si no se sabe como funciona el comando
    if '-h' in sys.argv or '--help' in sys.argv:
        print("Uso: python encriptar.py [-h] {-b,-f} base64/fichero numPersonas numMinimo")
        print("Encripta un secreto en base64 o el contenido de un archivo binario para compartir en n personas")
        print()
        print("Argumentos:")
        print("  -h, --help       muestra este mensaje de ayuda y sale")
        print("  -b               indica que el input es un texto en bytes codificado en base64")
        print("  -f               indica que el input es un archivo")
        print("  base64/fichero   el texto en base64 o archivo binario a compartir")
        print("  numPersonas      el numero de personas a compartir el secreto")
        print("  numMinimo        el numero de personas que se tienen que reunir para poder recuperar el secreto")
        return

    # Verificar que se han proporcionado 4 argumentos
    if len(sys.argv) != 5:
        print("Uso: python3 encriptar.py {-b,-f} base64/fichero numPersonas numMinimo")
        return

    # Leer los argumentos
    mode, input_data, numPersonas, numMinimo = sys.argv[1:]

    if not numPersonas.isdigit() or not numMinimo.isdigit():
        print("Error: los dos últimos parámetros deben ser enteros.")
        sys.exit(1)

    # Convertir los argumentos a enteros
    numPersonas = int(numPersonas)
    numMinimo = int(numMinimo)

    # Validar el primer argumento
    if mode not in ['-b', '-f']:
        print("Error: el primer argumento debe ser -b o -f")
        return

    # Validar el cuarto argumento
    if not (3 <= numMinimo < numPersonas):
        print("Error: el cuarto argumento debe ser menor que el tercer argumento y mayor que 3")
        return
    
    #Comprobacion de que el texto especificado sea en base64
    if mode == "-b":
        try:
            decoded = base64.b64decode(input_data)
            if base64.b64encode(decoded) != input_data.encode():
                raise ValueError
        except (TypeError, ValueError):
            print("Error: El contenido del segundo argumento no está en base64")
            sys.exit(1)
    
    # Comprobar si el modo es -f
    if mode == "-f":
        try:
            # Obtener la información del archivo
            file_info = os.stat(input_data)
            # Obtener el tamaño real del contenido
            file_size = file_info.st_size - file_info.st_size % 4
            # Leer el contenido del archivo
            with open(input_data, "rb") as f:
                file_content = f.read(file_size)
            if len(file_content) > 32:
                print("Error: El archivo no puede ser mayor de 32 bytes en binario")
                sys.exit(1)
            # Convertir el contenido a base64
            input_data = base64.b64encode(file_content).decode()
        except FileNotFoundError:
            print("Error: El archivo especificado no existe")
            sys.exit(1)
        except binascii.Error:
            print("Error: El contenido del fichero no es correcto")
            sys.exit(1)


    #Se pasa el texto a entero para poder trabajar con el en el algortimo
    decoded_bytes = base64.b64decode(input_data)
    decoded_integer = int.from_bytes(decoded_bytes, byteorder='big')
    numero_de_cifras = len(str(decoded_integer))
    
    #En el caso de que el entero tenga mas de 26 cifras se parte en entero en trozos iguales para poder pasarlo al algoritmo
    texto_entero = str(decoded_integer)

    trozos_enteros = []
    if numero_de_cifras > 26: #Si el numero de cifras es mayor de 26 partirmos el entero en trozos de 26
        while len(texto_entero) > 0:
            if len(texto_entero) <= 26:
                trozos_enteros.append(texto_entero)
                texto_entero = ""
            else:
                trozos_enteros.append(texto_entero[-26:])
                texto_entero = texto_entero[:-26]
        trozos_enteros.reverse()
    
    numeros_enteros = []
    if numero_de_cifras > 26:
        for trozo in trozos_enteros:
            numeros_enteros.append(int(trozo))
    else:
        numeros_enteros.append(int(decoded_integer))

    lista_de_listas = [[] for _ in range(numPersonas)]

    #Generamos los shares correspondientes a cada persona para compartirlo después
    for num in numeros_enteros:
        shares = generate_shares(numPersonas, numMinimo, num)
        i = 0
        for share in shares:
            lista_de_listas[i].append(share)
            i += 1

    #Cuando tengamos los shares se meten en ficheros con los shares correspondientes a cada persona
    for i, sublista in enumerate(lista_de_listas):
        with open(f"archivo_{i}.txt", "w") as archivo:
            for tupla in sublista:
                tupla_codificada = base64.b64encode(str(tupla).encode('utf-8')).decode('utf-8')
                archivo.write(f"{tupla_codificada}\n")

    #Se informa de que se han creado los ficheros i acaba el programa
    print(f"Creados " + str(numPersonas) +  " ficheros correctamente, nombre de los ficheros con el secreto ( archivo_X.txt )")
    print("Para descifrar el secreto llamar al desencriptar.py")

if __name__ == '__main__':
    main()
