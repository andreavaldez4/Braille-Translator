# --- LIBRERÍAS QUE SE TIENEN QUE INSTALAR ---
#pip install numpy
#pip install numpy-stl (no instales solo stl)
#import pandas as pd
#from stl import mesh
#from conversiones import conv
#import sys

# |palabra| 4 letras | 5 letras | 6 letras | 7 letras | 8 letras | 9 letras | 10 letras |11 letras | 12 letras |
# |medida |   22mm   |   28 mm  |    34mm  |   40mm   |   46mm   |   52mm   |   58mm    |   64mm   |    70mm   |

# |palabra| 13 letras | 14 letras | 15 letras | 16 letras | 17 letras | 18 letras | 19 letras | 20 letras |
# |medida |   76mm    |   82 mm   |    88mm   |   94mm    |   100mm   |   106mm   |   112mm   |   118mm   |

# por cada mayúscula se le agrega ---> 6mm
# espacio entre palabras ---> 4mm
# espacio entre filas ---> 3.5mm

def main():
    print(" ~~~ Bienvenido al traductor de braille! ~~~ ")
    opt = int(input("Desea imprimir:\n 1) Braille\n 2) Texto\n 3) Braille y Texto\n Selección: "))

    # --- SOLAMENTE BRAILLE ---
    if opt == 1:
        print("\n ~~ Opción elegida: Braille ~~ ")
        import solo_braille
        solo_braille.main()

    # --- SOLAMENTE TEXTO ---
    if opt == 2:
        print("\n ~~ Opción elegida: Texto ~~ ")
        import solo_texto
        solo_texto.main()

    # --- BRAILLE Y TEXTO ---
    if opt == 3:
        print("\n ~~ Opción elegida: Texto y Braille ~~ ")
        import braille_y_letras
        braille_y_letras.main()


if __name__ == "__main__":
    main()

