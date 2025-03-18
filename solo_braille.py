# version python 3.12

from stl import mesh
import numpy as np
import sys
from diccionario_de_braille import conv

# --- PARÁMETROS DIMENSIONALES (en mm) ---
diam_punto = 1.95
ancho_celda = 4
alto_celda = 6.5
entre_puntos = 1
entre_filas = 3.5
entre_letras = 3.9


# --- USUARIO INGRESA TEXTO ---
def es_valido(texto_original):
    for char in texto_original:
        if char not in conv:
            return False
    return True


def evaluar_texto_insertado():
    conversion_ancho = 10
    conversion_largo = 11
    cant_lineas = int(input("Ingrese la cantidad de líneas de braille que desea imprimir: "))
    if cant_lineas == 1:
        conversion_ancho = 9.2
    if cant_lineas == 2:
        conversion_ancho = 10.9
    if cant_lineas == 3:
        conversion_ancho = 10.6
    if cant_lineas == 4:
        conversion_ancho = 10.5
    if cant_lineas == 5:
        conversion_ancho = 10.4

    input_usuario = []
    for i in range(cant_lineas):
        texto_original = str(input(f"Ingrese el texto de la fila #{i + 1}: "))
        while not es_valido(texto_original):
            print("Texto inválido")
            texto_original = str(input(f"Ingrese el texto de la fila #{i + 1}: "))
            # repetir input
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

    # Cálculos de dimensiones vectoriales
    lista_del_texto = input_usuario
    linea_mas_larga = max(lista_del_texto, key=len)
    total_espacios = linea_mas_larga.count(" ")
    total_caracteres = len(linea_mas_larga.replace(" ", ""))
    total_mayusculas = sum(1 for letra in linea_mas_larga if letra.isupper())
    largo_total = (((total_caracteres * ancho_celda) + (total_espacios * ancho_celda) +
                    (total_mayusculas * ancho_celda) + (total_caracteres - 1) * entre_letras) - 1) / conversion_largo
    alto_total = ((alto_celda * cant_lineas) + (entre_filas * (cant_lineas - 1)) - 1) / conversion_ancho

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


# --- GENERA LOS PUNTOS DE BRAILLE ---
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


# --- GENERA EL RECTÁNGULO DONDE IRÁN LOS PUNTOS ---
def generar_rectangulo_redondeado(vertices, caras, largo_total, alto_total, profundidad, radio=0.5, segmentos=16):
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


# --- COMBINA MESH DE RECTÁNGULO Y BRAILLE ---
def combinar_meshes(mesh1, mesh2):
    combined = mesh.Mesh(np.concatenate([mesh1.data, mesh2.data]))
    return combined


def generar_braille_completo(lista_del_texto, largo_total, alto_total, profundidad=0.5,
                             nombre_archivo="braille_completo.stl"):
    margen = 0.5
    largo_total_con_margen = largo_total + (2 * margen)
    alto_total_con_margen = alto_total + (2 * margen)

    # Lista para almacenar todos los vértices y caras
    todos_vertices = []
    todas_caras = []
    offset_global = 0

    # --- Generar el rectángulo base ---
    vertices_rect = []
    caras_rect = []
    generar_rectangulo_redondeado(vertices_rect, caras_rect,
                                  largo_total_con_margen,
                                  alto_total_con_margen,
                                  profundidad, radio=0.5)

    # Añadir rectángulo base a las listas globales
    todos_vertices.extend(vertices_rect)
    todas_caras.extend(caras_rect)
    offset_global = len(vertices_rect)

    # --- Generar los puntos braille ---
    pos_y = alto_total_con_margen - margen
    for linea in lista_del_texto:
        pos_x = margen
        for letra in linea:
            if letra.isupper():
                braille = conv.get('CAP', [0, 0, 0, 0, 0, 0])
                for i in range(6):
                    if braille[i] == 1:
                        cx = pos_x + (i % 2) * (diam_punto / 10 + entre_puntos / 10)
                        cy = pos_y - (i // 2) * (diam_punto / 10 + entre_puntos / 10)
                        new_vertices, new_caras, new_offset = punto(0.10, diam_punto / 10, 12, cx, cy, profundidad,
                                                                    offset_global)
                        todos_vertices.extend(new_vertices)
                        todas_caras.extend(new_caras)
                        offset_global = new_offset
                pos_x += 0.67
                letra = letra.lower()

            braille = conv.get(letra, [0, 0, 0, 0, 0, 0])
            for i in range(6):
                if braille[i] == 1:
                    cx = pos_x + (i % 2) * (diam_punto / 10 + entre_puntos / 10)
                    cy = pos_y - (i // 2) * (diam_punto / 10 + entre_puntos / 10)
                    new_vertices, new_caras, new_offset = punto(0.10, diam_punto / 10, 12, cx, cy, profundidad,
                                                                offset_global)
                    todos_vertices.extend(new_vertices)
                    todas_caras.extend(new_caras)
                    offset_global = new_offset
            pos_x += 0.67
        pos_y -= 0.30

    # Crear el mesh final con todos los elementos
    if len(todas_caras) > 0:
        mesh_final = mesh.Mesh(np.zeros(len(todas_caras), dtype=mesh.Mesh.dtype))
        for i, cara in enumerate(todas_caras):
            for j in range(3):
                mesh_final.vectors[i][j] = todos_vertices[cara[j]]

        mesh_final.save(nombre_archivo)
        print(f"El archivo STL '{nombre_archivo}' ha sido generado correctamente.")
    else:
        print("No se generaron elementos. Asegúrese de que el texto sea válido.")


def main():
    try:
        print("\n~~~ Bienvenido al generador de braille en 3D ~~~")
        print("Este programa genera un archivo STL con texto en braille")
        lista_del_texto, largo_total, alto_total, nombre_doc = evaluar_texto_insertado()
        generar_braille_completo(
            lista_del_texto=lista_del_texto,
            largo_total=largo_total,
            alto_total=alto_total,
            profundidad=0.3,
            nombre_archivo=nombre_doc
        )
        print("\nProceso completado exitosamente!")
    except Exception as e:
        print(f"\nOcurrió un error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()