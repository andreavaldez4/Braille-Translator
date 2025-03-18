import numpy as np
import pandas as pd
from stl import mesh
from diccionario_de_braille import conv
import sys

# --- FUNCIONES MESH ---------------------------------------------------------------------------------------------------------------------------------------------------
# Funcion para generar los vertices y las caras a partir de un mesh
def mesh_info(n_mesh):
    vertices = n_mesh.vectors.reshape(-1, 3)
    vertices = np.unique(vertices, axis=0)

    caras = []
    for face in n_mesh.vectors:
        p1 = np.where(np.all(vertices == face[0], axis=1))[0][0]
        p2 = np.where(np.all(vertices == face[1], axis=1))[0][0]
        p3 = np.where(np.all(vertices == face[2], axis=1))[0][0]
        caras.append([p1, p2, p3])
    return vertices, caras


# Funcion para generar un mesh
def mesh_generador(vertices, caras):
    mesh_figura = mesh.Mesh(np.zeros(len(caras), dtype=mesh.Mesh.dtype))
    for i, cara in enumerate(caras):
        for j in range(3):
            mesh_figura.vectors[i][j] = vertices[cara[j]]
    return mesh_figura


# Funcion para centrar los vertices
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


# Funcion para combinar meshes
def combinar_meshes(lista_mesh):
    data = [m.data for m in lista_mesh]
    combined = mesh.Mesh(np.concatenate(data))
    return combined


# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------


# --- FUNCIONES LETRAS ------------------------------------------------------------------------------------------------------------------------------------------------
# Funcion para cargar los vertices y las caras del excel
def letra_info(letra, excel):
    df_vertices = pd.read_excel(excel, sheet_name=letra + '_vert', engine='openpyxl')
    df_caras = pd.read_excel(excel, sheet_name=letra + '_caras', engine='openpyxl')

    vertices = np.array(df_vertices)
    caras = np.array(df_caras)

    return vertices, caras


# Genera un mesh de la palabra completa
def mesh_palabra(mensaje, vertices_lista):
    lista_meshes = []
    for j in range(len(mensaje)):
        mesh_letra = mesh_generador(vertices_lista[j], caras_lista[j])
        lista_meshes.append(mesh_letra)

    mesh_combinado = combinar_meshes(lista_meshes)
    return mesh_combinado


# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------


# --- FUNCIONES BRAILLE -----------------------------------------------------------------------------------------------------------------------------------------------
# Usuario ingresa el texto
def es_valido(texto_original):
    for char in texto_original:
        if char not in conv:
            return False
    return True


# Funcion para obtener texto y dimensiones
def evaluar_texto_insertado():
    cant_lineas = int(input("Ingrese la cantidad de líneas de braille que desea imprimir: "))
    input_usuario = []
    for i in range(cant_lineas):
        texto_original = str(input(f"Ingrese el texto de la fila #{i + 1}: "))
        while not es_valido(texto_original):
            print("Texto inválido")
            texto_original = str(input(f"Ingrese el texto de la fila #{i + 1}: "))
        input_usuario.append(texto_original.strip())
    if not input_usuario:
        sys.exit("\n No hay texto insertado, corre de nuevo el programa para proceder.\n")

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

    lista_del_texto = input_usuario

    linea_mas_larga = max(lista_del_texto, key=len)  # a partir de la línea más larga, se determina el largo del rectángulo
    total_espacios = linea_mas_larga.count(" ")
    total_caracteres = len(linea_mas_larga.replace(" ", ""))
    total_mayusculas = sum(1 for letra in linea_mas_larga if letra.isupper())
    largo_total = ((total_caracteres * ancho_celda) + (total_espacios * 2.8) + total_mayusculas * ancho_celda) / 5
    alto_total = ((alto_celda * cant_lineas) + (entre_filas * (cant_lineas - 1))) / 10

    margen = 0.5
    largo_total_con_margen = largo_total + (2 * margen)
    alto_total_con_margen = alto_total + (2 * margen)
    profundidad = 0.3

    # Conversión a milímetros y redondeo
    dim_x = round((largo_total_con_margen) * 10, 2)
    dim_y = round((alto_total_con_margen) * 10, 2)
    dim_z = round(profundidad * 10, 2)
    volumen = round(dim_x * dim_y * dim_z, 2)

    # Dimensiones redondeadas para el nombre del archivo
    dim_x_nombre = round(dim_x)
    dim_y_nombre = round(dim_y)
    dim_z_nombre = round(dim_z)

    # Generación del nombre del archivo con dimensiones redondeadas
    texto_base = '_'.join(texto.replace(' ', '_') for texto in lista_del_texto)
    nombre_con_dim = f"{texto_base}_x{dim_x_nombre}mm_y{dim_y_nombre}mm_z{dim_z_nombre}mm.stl"
    nombre_default = f"braille_completo_x{dim_x_nombre}mm_y{dim_y_nombre}mm_z{dim_z_nombre}mm.stl"

    opt = int(input("¿Deseas nombrar el archivo con todo el texto (1), o con nombre por default (2)? "))
    if opt == 1:
        nombre_doc = nombre_con_dim
        print(f"El archivo se guardará como: {nombre_doc}")
    if opt == 2:
        nombre_doc = nombre_default
        print(f"El archivo se guardará como: {nombre_doc}")

    print("\nDimensiones del modelo:")
    print(f"Vector X (largo):     {dim_x} mm")
    print(f"Vector Y (alto):      {dim_y} mm")
    print(f"Vector Z (profundo):  {dim_z} mm")
    print(f"Volumen aproximado:   {volumen} mm³")
    print("\nDimensiones del rectángulo base:")
    print(f"Largo del rectángulo: {round((largo_total + 1) * 10, 2)} mm")
    print(f"Alto del rectángulo:  {round((alto_total + 1) * 10, 2)} mm")

    return lista_del_texto, largo_total, alto_total, nombre_doc


# Generador de puntos individuales de braille
def punto(altura, diametro, segmentos, dx, dy, dz, offset):
    radio = diametro / 2
    m = np.arctanh(radio / altura)
    a = altura / np.cosh(m)

    # ecuaciones parametrizadas
    u = np.linspace(0, 2 * np.pi, segmentos)
    v = np.linspace(0, np.pi / 2, segmentos)
    u, v = np.meshgrid(u, v)

    x = a * np.sinh(m) * np.sin(v) * np.cos(u) + dx
    y = a * np.sinh(m) * np.sin(v) * np.sin(u) + dy
    z = a * np.cosh(m) * np.cos(v) + dz

    # generar los vertices de la figura
    vertices = list(zip(x.ravel(), y.ravel(), z.ravel()))

    # generar las caras de la figura
    caras = []
    for i in range(segmentos - 1):
        for j in range(segmentos - 1):
            p1 = i * segmentos + j
            p2 = p1 + segmentos
            p3 = p1 + 1
            p4 = p2 + 1

            caras.append([p1 + offset, p2 + offset, p3 + offset])
            caras.append([p2 + offset, p4 + offset, p3 + offset])

    # actualizar el offset
    new_offset = offset + len(vertices)

    return vertices, caras, new_offset


# Funcion para posicionar los puntos para crear las letras en braille
def generar_braille(lista_del_texto, profundidad):
    vertices_braille = []
    caras_braille = []
    offset = 0

    pos_y = 0
    for linea in lista_del_texto:
        pos_x = 0
        for letra in linea:
            if letra.isupper():
                braille = conv.get('CAP', [0, 0, 0, 0, 0, 0])
                for i in range(6):
                    if braille[i] == 1:
                        cx = pos_x + (i % 2) * (diam_punto / 10 + entre_puntos / 10)
                        cy = pos_y - (i // 2) * (diam_punto / 10 + entre_puntos / 10)
                        # comenzar desde profundidad y agregar la altura del punto
                        new_vertices, new_caras, offset = punto(0.10, diam_punto / 10, 12, cx, cy, profundidad, offset)
                        vertices_braille.extend(new_vertices)
                        caras_braille.extend(new_caras)
                pos_x += 0.8
                letra = letra.lower()

            braille = conv.get(letra, [0, 0, 0, 0, 0, 0])
            for i in range(6):
                if braille[i] == 1:
                    cx = pos_x + (i % 2) * (diam_punto / 10 + entre_puntos / 10)
                    cy = pos_y - (i // 2) * (diam_punto / 10 + entre_puntos / 10)
                    # comenzar desde profundidad y agregar la altura del punto
                    new_vertices, new_caras, offset = punto(0.10, diam_punto / 10, 12, cx, cy, profundidad, offset)
                    vertices_braille.extend(new_vertices)
                    caras_braille.extend(new_caras)
            pos_x += 0.8
        pos_y -= 1.05

    vertices_braille = centrar(vertices_braille)
    return vertices_braille, caras_braille


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------


# --- FUNCION BASE ----------------------------------------------------------------------------------------------------------------------------------------------------
# Funcion para crear la base de las letras

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


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------


# --- PARAMETROS DIMENSIONALES EN MILIMETROS --------------------------------------------------------------------------------------------------------------------------

#  Puntos de braille
diam_punto = 1.95
ancho_celda = 4
alto_celda = 6.5
entre_puntos = 1
entre_filas = 3.5
altura_texto = 0.15
espacio_texto_braille = 1.0

# Dimensiones de las letras
espacio = 10
separacion_letras = 2
distancia_a_braille = 0.4
letra_size = 0.08

# Dimensiones de la base
profundidad = 0.5
margen = 0.2
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------


def main():
    try:
        print("\n~~~ Bienvenido al generador de braille y texto 3D ~~~")
        print("Este programa genera un archivo STL con texto en braille y letras.")

        # Solicitar texto al usuario
        texto, largo_total, alto_total, nombre_doc = evaluar_texto_insertado()

        # Generar vertices y caras del braille
        vertices_braille, caras_braille = generar_braille(texto, profundidad)

        # --- GENERACION DE LAS LETRAS -----------------------------------------------------------------------------------------------------------------------------------------
        excel_min = 'letras_minusculas_corbel.xlsx'
        excel_may = 'letras_mayusculas_corbel.xlsx'

        # Guarda la informacion de cada letra en listas
        vertices_lista = []
        caras_lista = []
        for j in texto[0]:
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
        for j in range(len(texto[0])):
            vertices_lista[j][:, 0] += dx
            if j == len(vertices_lista) - 1:
                break
            x_max_1 = np.max(vertices_lista[j][:, 0])
            x_min_2 = np.min(vertices_lista[j + 1][:, 0])
            dx = x_max_1 - x_min_2 + separacion_letras
            if texto[0][j + count] == ' ':
                dx += espacio
                count += 1

        # Modifica el tamaño de la letra
        vertices_lista = [array * letra_size for array in vertices_lista]

        # Centrar el texto en el eje x
        x_max = np.max(np.concatenate([array[:, 0] for array in vertices_lista]))
        calibracion = abs(np.min(vertices_lista[0][:, 0]))
        mover = (x_max - calibracion) / 2
        vertices_lista = [np.column_stack((array[:, 0] - mover, array[:, 1], array[:, 2])) for array in vertices_lista]

        # Posiciona el texto debajo del braille
        y_min_braille = abs(np.min(vertices_braille[:, 1]))
        y_max_lista = [np.max(array[:, 1]) for array in vertices_lista]
        y_max = np.max(y_max_lista)

        bajar_letras = distancia_a_braille + y_min_braille + y_max
        vertices_lista = [np.column_stack((array[:, 0], array[:, 1] - bajar_letras, array[:, 2])) for array in vertices_lista]

        # Eleva las letras sobre la base (eje z)
        vertices_lista = [np.column_stack((array[:, 0], array[:, 1], array[:, 2] + profundidad)) for array in vertices_lista]

        # --- GENERACION DE LA BASE --------------------------------------------------------------------------------------------------------------------------------------------
        # Limites en x
        x_max_letra = np.max(list(np.max(array[:, 0]) for array in vertices_lista))
        x_min_letra = np.min(list(np.min(array[:, 0]) for array in vertices_lista))

        x_max_braille = np.max(vertices_braille[:, 0])
        x_min_braille = np.min(vertices_braille[:, 0])

        x_max_total = np.max([x_max_letra, x_max_braille])
        x_min_total = np.min([x_min_letra, x_min_braille])

        # Limites en y
        y_max_total = np.max(vertices_braille[:, 1])
        y_min_total = np.min(list(np.min(array[:, 1]) for array in vertices_lista))

        # Vertices y caras de la base
        margen = 0.5
        largo_total = (x_max_total - x_min_total) + 2 * margen
        alto_total = (y_max_total - y_min_total) + 2 * margen
        vertices_rect, caras_rect = generar_rectangulo_redondeado(largo_total, alto_total, profundidad)

        # Centrar la base en el origen
        desplazar = alto_total / 2 - y_max_total - margen
        vertices_rect[:, 1] -= desplazar

        # --- BRAILLE Y LETRAS -------------------------------------------------------------------------------------------------------------------------------------------------
        # Generar meshes por separado
        base_mesh = mesh_generador(vertices_rect, caras_rect)
        braille_mesh = mesh_generador(vertices_braille, caras_braille)

        letras_mesh = []
        for i in range(len(vertices_lista)):
            letra_mesh = mesh_generador(vertices_lista[i], caras_lista[i])
            letras_mesh.append(letra_mesh)
        palabra_mesh = combinar_meshes(letras_mesh)

        # Crea el mesh final
        texto_braille_mesh = combinar_meshes([braille_mesh, palabra_mesh, base_mesh])
        texto_braille_mesh.save(nombre_doc)

        print(f"\nArchivo STL '{nombre_doc}' ha sido generado correctamente.")

    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()