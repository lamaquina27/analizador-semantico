import sys

class Token:
    def __init__(self, tipo, valor, fila, columna):
        self.tipo = tipo
        self.valor = valor
        self.fila = fila
        self.columna = columna
        
    

class Scanner:
    def __init__(self, texto):
        self.tokens = []  
        self.texto = texto
        self.posicion = 0
        self.lineas_totales = self.texto.split("\n")
        self.linea_actual = 0
        self.tokenizar()
        
    def tokenizar(self):
        for num_fila, linea in enumerate(self.lineas_totales, start=1):
            indice = 0
            while indice < len(linea):
                if linea[indice].isspace():
                    indice += 1
                    continue
                if linea[indice] == "#":
                    break
                palabra = ""
                while indice < len(linea) and (linea[indice].isalnum() or linea[indice] == "_"):
                    palabra += linea[indice]
                    indice += 1
                if palabra.isdigit():
                    print(f"<tk_entero,\"{palabra}\", {num_fila}, {indice + 1}>")
                    self.tokens.append(Token("tk_entero", palabra, num_fila, indice + 1))
                elif palabra:
                    if palabra in palabras_reservadas_key:
                        print(f"<{palabra}, {num_fila}, {indice - len(palabra) + 1}>")
                        self.tokens.append(Token(palabras_reservadas[palabra], palabra, num_fila, indice - len(palabra) + 1))
                    elif palabra.lower() in palabras_reservadas_key:
                        print(f">>> Error léxico(linea:{num_fila},posicion:{indice - len(palabra) + 1})")
                        sys.exit(1)
                    else:
                        print(f"<id,{palabra}, {num_fila}, {indice - len(palabra) + 1}>")
                        self.tokens.append(Token("id", palabra, num_fila, indice - len(palabra) + 1))

                elif linea[indice] == '"':
                    inicio = indice
                    print(f"<tk_comillas,\"''\", {num_fila}, {inicio + 1}>")
                    self.tokens.append(Token("tk_comillas", '', num_fila, inicio + 1))
                    indice += 1
                    cadena = ""
                    while indice < len(linea) and linea[indice] != '"':
                        cadena += linea[indice]
                        
                        indice += 1
                    if indice < len(linea) and linea[indice] == '"':
                        print(f"<tk_cadena,\"{cadena}\", {num_fila}, {inicio + 2}>")
                        self.tokens.append(Token("tk_cadena", cadena, num_fila, inicio + 1))
                        
                        indice += 1  
                    
                    if indice <= len(linea) and linea[indice-1] == '"':
                        print(f"<tk_comillas,\"''\", {num_fila}, {indice}>")
                        self.tokens.append(Token("tk_comillas", '', num_fila, inicio + 2))
                        
                elif indice + 1 < len(linea) and linea[indice:indice + 2] in simbolos_keys:
                    simbolo = linea[indice:indice + 2]
                    print(f"<{simbolos[simbolo]}, {num_fila}, {indice + 1}>")
                    self.tokens.append(Token(simbolos[simbolo], simbolo, num_fila, indice + 1))
                    indice += 2  
                elif linea[indice] in simbolos_keys:
                    simbolo = linea[indice]
                    print(f"<{simbolos[simbolo]}, {num_fila}, {indice + 1}>")
                    self.tokens.append(Token(simbolos[simbolo], simbolo, num_fila, indice + 1))
                    indice += 1
                else:
                    print(f">>> Error léxico(linea:{num_fila},posicion:{indice+1})")
                    sys.exit(1)

    def siguiente_token(self):
        if self.tokens:
            return self.tokens.pop(0)
        else:
            return Token("EOF", "", -1, -1)

    def obtener_linea_actual(self):
        if self.linea_actual < len(self.lineas_totales):
            linea=self.lineas_totales[self.linea_actual]
            self.linea_actual += 1
            return linea
        return ""  # Retorna una cadena vacía si el índice es inválido

        

palabras_reservadas ={"else":"else","int":"int","str":"str","while":"while","in":"in","for":"for","None":"None","class" : "class","def":'def',"True":'true',"False":"false","bool":'bool',"__init__":'__init',"self":"self","print":"print","return":"return","object":"object","if":"if"}
palabras_reservadas_key = palabras_reservadas.keys()
simbolos={">=":"tk_mayorigual","<=":"tk_menorigual",">":"tk_mayorque","<":"tk_menorque","*":"tk_multiplicacion","-":"tk_menos","+":"tk_suma",",":"tk_coma","[":"tk_llave_izq","]":"tk_llave_der",":":"tk_dos_puntos","(":"tk_par_izq",")":"tk_par_der",".":"tk_punto","=":"tk_asig","->":"tk_ejecuta","==":"tk_igualdad","!=":"tk_diferencia"}
simbolos_keys=simbolos.keys()
simbolos_invertidos = {v: k for k, v in simbolos.items()}
