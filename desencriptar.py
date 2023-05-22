import sys
import base64
import os
import random
from math import ceil
from decimal import Decimal

def decode_base64(lst):
    decoded_lst = []
    for tup in lst:
        decoded_tup = []
        for element in tup:
            decoded_element = base64.b64decode(element).decode('utf-8')
            decoded_tup.append(decoded_element)
        decoded_lst.append(decoded_tup)
    return decoded_lst

def reconstruct_secret(shares):

    sums = 0
    prod_arr = []
 
    for j, share_j in enumerate(shares):
        xj, yj = share_j
        prod = Decimal(1)
 
        for i, share_i in enumerate(shares):
            xi, _ = share_i
            if i != j:
                prod *= Decimal(Decimal(xi)/(xi-xj))
 
        prod *= yj
        sums += Decimal(prod)
 
    return int(round(Decimal(sums), 0))
 

def main():
        
    #Mensaje si no se introducen argumentos
    if len(sys.argv) == 1:
        print("Uso: python3 desencriptar.py numFich fich1 fich2 fich3 ...")
        print("Ayuda:  -h, --help       muestra este mensaje de ayuda y sale")
        sys.exit(1)

    #Mensaje de ayuda para explicar el comando
    if '-h' in sys.argv or '--help' in sys.argv:
        print("Uso: python3 desencriptar.py numFich fih1 fich2 fich3 ...")
        print("Desencripta un secreto reconstruyendo con un mínimo de partes del mismo")
        print()
        print("Argumentos:")
        print("  -h, --help       muestra este mensaje de ayuda y sale")
        print("  numFich          el numero mínimo de personas que se especificó para descifrar el secreto")
        print("  fich1            fichero dado en el programa encriptar.py con partes del secreto")
        print("  fich2            fichero dado en el programa encriptar.py con partes del secreto")
        return


    # Leer los argumentos
    numFich = sys.argv[1]

    if not numFich.isdigit():
        print("Error: el primer parametro tiene que ser un numero positivo.")
        sys.exit(1)
    
    numFich = int(numFich)

    #Comprobacion de si se han introducido mas ficheros de los indicados en el primer argumento
    if len(sys.argv) - 2 != numFich:
        print("No has introducido el numero correctos de ficheros de los especificados en el primer argumento")
        return

    #Guardamos todos los ficheros en una lista
    files = sys.argv[2:]

    # Comprobar si cada archivo existe
    for file in files:
        if not os.path.exists(file):
            print(f"{file} no existe")
            return
        
    #Contar el numero de lineas del primer fichero para poder comprar con los demas, lineas con texto, no vacias
    with open(files[0], "r") as f:
        lines = f.readlines()
        num_lines = len([line for line in lines if line.strip()])

    # Comprobar que todos los archivos tienen el mismo número de líneas
    for file in files[1:]:
        with open(file, "r") as f:
            lines = f.readlines()
            if len([line for line in lines if line.strip()]) != num_lines:
                print("Los archivos no vienen del mismo secreto, no coincide el numero de lineas y no se puede recuperar el secreto")
                sys.exit(1)

    #Lo metemos en un bloque try por si falla la reconstruccion
    try:

        #Guardamos los datos en base64 en una lista para poder tratar con ellos
        lista_ficheros = []
        for nombre_fichero in files:
            with open(nombre_fichero) as fichero:
                lineas = [line.strip() for line in fichero.readlines() if line.strip()]
                lista_ficheros.append(lineas)

        #Pasamos la lista de base64 a la tupla que es el tipo de dato con que trata el algoritmo
        lista_decimal = decode_base64(lista_ficheros)
        result = [[tuple(int(num) for num in tup[1:-1].split(', ')) for tup in sublista] for sublista in lista_decimal]

        #Hacemos la transpuesta para que cada persona pueda sacar la parte correspondiente del secreto para luego juntarlo
        transpuesta = list(zip(*result))

        # Crear una lista para cada elemento
        resultados = []
        for elemento in transpuesta:
            resultados.append(list(elemento))

        #Reconstruimos el secreto por partes en el caso de que tenga mas de 26 cifras i se tuvo que partir en trozos
        shares = []
        for sublista in resultados:
            resultado = reconstruct_secret(sublista)
            shares.append(resultado)  
            
        
        #Juntar los shares para recuperar el secreto
        numero_completo = int(''.join(str(num) for num in shares))
        bytes_num = numero_completo.to_bytes((numero_completo.bit_length() + 7) // 8, 'big')

        # Codificar la cadena de bytes en base64
        base64_bytes = base64.b64encode(bytes_num)

        #Imprimimos el secreto recuperado
        print("Secreto recuperado: " + base64_bytes.decode('utf-8'))       

    except Exception as e:
        print("Error en la recuperación del secreto, es posible que algún fichero se haya modificado o se hayan introducido dos ficheros iguales")

if __name__ == '__main__':
    main()