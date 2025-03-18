import numpy as np
import pandas as pd
from stl import mesh
import sys
from diccionario_de_braille import conv

# --- FUNCIONES MESH ---------------------------------------------------------------------------------------------------------------------------------------------------
def mesh_generador(vertices, caras):
    mesh_figura = mesh.Mesh(np.zeros(len(caras), dtype=mesh.Mesh.dtype))
    for i, cara in enumerate(caras):
        for j in range(3):
            mesh_figura.vectors[i][j] = vertices[cara[j]]
    return mesh_figura


def centrar(vertices):
    vertices = np.array(vertices)
    min_x = np.min(vertices[:, 0])
    max_x = np.max(vertices[:, 0])
    min_y = np.min(vertices[:, 1])
    max_y = np.max(vertices[:, 1])
    centro_x = (min_x + max_x) / 2
    centro_y = (min_y + max_y) / 2
    vertices_centrados = np.array([(x - centro_x, y - centro_y, z) for x, y, z in vertices])
    return vertices_centrados


def combinar_meshes(lista_mesh):
    data = [m.data for m in lista_mesh]
    combined = mesh.Mesh(np.concatenate(data))
    return combined


# --- FUNCIONES LETRAS ------------------------------------------------------------------------------------------------------------------------------------------------
def letra_info(letra, excel):
    df_vertices = pd.read_excel(excel, sheet_name=letra + '_vert', engine='openpyxl')
    df_caras = pd.read_excel(excel, sheet_name=letra + '_caras', engine='openpyxl')
    vertices = np.array(df_vertices)
    caras = np.array(df_caras)
    return vertices, caras


def generar_rectangulo_redondeado(largo_total, alto_total, profundidad, radio=0.5, segmentos=16):
    vertices = []
    caras = []

    def generar_puntos_esquina(cx, cy, start_angle, custom_radio=None):
        if custom_radio is None:
            custom_radio = radio
        puntos = []
        for i in range(segmentos + 1):
            angulo = start_angle + (i * (np.pi / 2) / segmentos)
            x = cx + custom_radio * np.cos(angulo)
            y = cy + custom_radio * np.sin(angulo)
            puntos.append((x, y))
        return puntos

    # Usar un radio más pequeño para la esquina superior izquierda
    radio_sup_izq = 0.1  # Radio reducido para la esquina superior izquierda

    esq_inf_izq = generar_puntos_esquina(radio, radio, np.pi)
    esq_inf_der = generar_puntos_esquina(largo_total - radio, radio, 3 * np.pi / 2)
    esq_sup_der = generar_puntos_esquina(largo_total - radio, alto_total - radio, 0)
    esq_sup_izq = generar_puntos_esquina(radio_sup_izq, alto_total - radio_sup_izq, np.pi / 2, radio_sup_izq)

    puntos_perimetro = (
            esq_inf_izq[:-1] +
            esq_inf_der[:-1] +
            esq_sup_der[:-1] +
            esq_sup_izq[:-1]
    )

    num_vertices_base = len(puntos_perimetro)
    offset = len(vertices)

    vertices.extend([(x, y, 0) for x, y in puntos_perimetro])
    vertices.extend([(x, y, profundidad) for x, y in puntos_perimetro])

    centro_inferior = len(vertices)
    centro_superior = len(vertices) + 1
    vertices.append((largo_total / 2, alto_total / 2, 0))
    vertices.append((largo_total / 2, alto_total / 2, profundidad))

    for i in range(num_vertices_base):
        caras.append([offset + i,
                      offset + ((i + 1) % num_vertices_base),
                      centro_inferior])
        caras.append([offset + i + num_vertices_base,
                      offset + ((i + 1) % num_vertices_base) + num_vertices_base,
                      centro_superior])

        caras.append([offset + i,
                      offset + ((i + 1) % num_vertices_base),
                      offset + i + num_vertices_base])
        caras.append([offset + ((i + 1) % num_vertices_base),
                      offset + ((i + 1) % num_vertices_base) + num_vertices_base,
                      offset + i + num_vertices_base])

    vertices = centrar(vertices)
    return vertices, caras


# Parámetros dimensionales
separacion_letras = 2
espacio = 10
letra_size = 0.08
profundidad = 0.3
margen = 0.5


def es_valido(texto_original):
    for char in texto_original:
        if char not in conv:
            return False
    return True


def main():
    try:
        print("\n~~~ Generador de texto 3D ~~~")

        # Solicitar número de líneas
        while True:
            try:
                cant_lineas = int(input("Ingrese la cantidad de líneas de texto que desea convertir: "))
                if cant_lineas > 0:
                    break
                else:
                    print("Por favor, ingrese un número mayor a 0.")
            except ValueError:
                print("Entrada inválida. Ingrese un número entero.")

        # Recopilar texto línea por línea
        input_usuario = []
        for i in range(cant_lineas):
            texto_original = str(input(f"Ingrese el texto de la fila #{i + 1}: "))
            while not es_valido(texto_original):
                print("Texto inválido")
                texto_original = str(input(f"Ingrese el texto de la fila #{i + 1}: "))
            input_usuario.append(texto_original.strip())

        # Confirmación de texto
        print(f"El texto insertado es el siguiente: ")
        for x in range(cant_lineas):
            print(f"Texto en fila #{x + 1}: {input_usuario[x]}")

        confirmar = input("¿Deseas confirmar este texto? (y/n): ").lower()
        while confirmar != 'y':
            if confirmar == 'n':
                try:
                    mod = int(input(f"¿Qué línea deseas modificar? (1-{cant_lineas}): "))
                    if 1 <= mod <= cant_lineas:
                        nuevo_texto = str(input(f"Ingrese el nuevo texto de la fila #{mod}: "))
                        while not es_valido(nuevo_texto):
                            print("Texto inválido")
                            nuevo_texto = str(input(f"Ingrese el nuevo texto de la fila #{mod}: "))
                        input_usuario[mod - 1] = nuevo_texto.strip()
                    else:
                        print(f"Por favor, elige un número entre 1 y {cant_lineas}.")
                except ValueError:
                    print("Entrada inválida. Por favor, introduce un número.")

                print("\nEl texto actualizado es el siguiente:")
                for x in range(cant_lineas):
                    print(f"Texto en fila #{x + 1}: {input_usuario[x]}")
            else:
                print("Entrada inválida. Responde con 'y' o 'n'.")

            confirmar = input("¿Deseas confirmar este texto? (y/n): ").lower()

        # Archivos de Excel para letras
        excel_min = 'letras_minusculas_corbel.xlsx'
        excel_may = 'letras_mayusculas_corbel.xlsx'

        todos_meshes = []
        desplazamiento_vertical = 0
        entre_filas = 1

        # Procesamiento de cada línea
        for texto in input_usuario:
            # Guarda la información de cada letra en listas
            vertices_lista = []
            caras_lista = []
            for j in texto:
                if j == ' ':
                    continue
                elif j.isupper():
                    vertices, caras = letra_info(j, excel_may)
                else:
                    vertices, caras = letra_info(j, excel_min)
                vertices_lista.append(vertices)
                caras_lista.append(caras)

            # Ordena las letras en el eje x y añade espacios
            dx = 0
            count = 1
            for j in range(len(texto)):
                vertices_lista[j][:, 0] += dx
                if j == len(vertices_lista) - 1:
                    break
                x_max_1 = np.max(vertices_lista[j][:, 0])
                x_min_2 = np.min(vertices_lista[j + 1][:, 0])
                dx = x_max_1 - x_min_2 + separacion_letras
                if texto[j + count] == ' ':
                    dx += espacio
                    count += 1

            # Modifica el tamaño de la letra
            vertices_lista = [array * letra_size for array in vertices_lista]

            # Centrar el texto en el eje x
            x_max = np.max(np.concatenate([array[:, 0] for array in vertices_lista]))
            calibracion = abs(np.min(vertices_lista[0][:, 0]))
            mover = (x_max - calibracion) / 2
            vertices_lista = [np.column_stack((array[:, 0] - mover, array[:, 1], array[:, 2])) for array in
                              vertices_lista]

            # Centrar el texto en el eje y
            y_max_lista = [np.max(array[:, 1]) for array in vertices_lista]
            y_min_lista = [np.min(array[:, 1]) for array in vertices_lista]
            y_max = np.max(y_max_lista)
            y_min = np.min(y_min_lista)
            bajar = (y_max - y_min) / 2

            # Desplazar verticalmente y añadir profundidad
            vertices_lista = [np.column_stack((array[:, 0],
                                               array[:, 1] - bajar + desplazamiento_vertical,
                                               array[:, 2] + profundidad)) for array in vertices_lista]

            # Generar meshes de letras
            letras_mesh = []
            for i in range(len(vertices_lista)):
                letra_mesh = mesh_generador(vertices_lista[i], caras_lista[i])
                letras_mesh.append(letra_mesh)

            # Combinar letras de la línea
            linea_mesh = combinar_meshes(letras_mesh)

            # Calcular dimensiones de la base

            margin = 1  # Adjust this value as needed

            x_max_letra = np.max(list(np.max(array[:, 0]) for array in vertices_lista)) + margin
            x_min_letra = np.min(list(np.min(array[:, 0]) for array in vertices_lista)) - margin
            y_max_letra = np.max(list(np.max(array[:, 1]) for array in vertices_lista)) + margin
            y_min_letra = np.min(list(np.min(array[:, 1]) for array in vertices_lista)) - margin

            largo_total = x_max_letra - x_min_letra
            alto_total = y_max_letra - y_min_letra

            alto_total_constante = alto_total
            # Generar base para esta línea
            vertices_rect, caras_rect = generar_rectangulo_redondeado(largo_total, alto_total_constante, profundidad, radio=0.5, segmentos=16)
            base_mesh = mesh_generador(vertices_rect, caras_rect)

            # Combinar letras y base de la línea
            linea_completa_mesh = combinar_meshes([linea_mesh, base_mesh])
            todos_meshes.append(linea_completa_mesh)

            # Preparar desplazamiento para la siguiente línea
            desplazamiento_vertical -= (alto_total + entre_filas)

        # Combinar todas las líneas en un solo mesh
        texto_mesh = combinar_meshes(todos_meshes)

        # Generar nombre de archivo
        texto_completo = '_'.join(input_usuario)
        nombre_doc = f"{texto_completo.replace(' ', '_')}_x{round(largo_total * 10)}mm_y{round(alto_total * 10)}mm_z{round(profundidad * 10)}mm.stl"

        # Guardar archivo
        texto_mesh.save(nombre_doc)
        print(f"\nArchivo STL '{nombre_doc}' ha sido generado correctamente.")

    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()