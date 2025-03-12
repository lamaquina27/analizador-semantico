# main.py

from lexico import Scanner
from sintaxis import Parser

def main():
    with open("ejemplo.py", "r") as archivo:
        texto = archivo.read()

    s = Scanner(texto)
    p = Parser(s)
    p.parser()
    
if __name__ == '__main__':
    main()
