import sys
import lexico
class Parser():
    def __init__(self,Scanner):
        self.scanner = Scanner
        self.token_actual = self.scanner.siguiente_token()
        self.nivel_indentacion = 0  # Nivel de indentación actual
        self.indentacion_esperada = 0  # Nivel de indentación esperado
        self.ultima_fila = None
        self.linea_entera = None
    def comprobador(self, *tipos_esperados):
        if self.token_actual.tipo in tipos_esperados:
            self.token_actual = self.scanner.siguiente_token()
        else:
            # Obtener los valores esperados desde el diccionario de símbolos y envolverlos en comillas
            esperados_str = ", ".join(f'"{lexico.simbolos_invertidos.get(tipo, tipo)}"' for tipo in tipos_esperados)
            
            print(
                f"<{self.token_actual.fila},{self.token_actual.columna}> Error sintáctico: "
                f"se encontró \"{self.token_actual.valor}\" "
                f"se esperaba {esperados_str}."
            )
            sys.exit(1)    # Finaliza la ejecución en caso de error
    def verificar_indentacion(self, linea):
        espacios = 0
        
        while espacios < len(linea) and linea[espacios] == ' ':
            espacios += 1
        
        if espacios % 4 != 0:
            print(f">>> Error de indentación (línea: {self.token_actual.fila}, posición: {self.token_actual.columna}): "
                f"La indentación debe ser múltiplo de 4.")
            sys.exit(1)
        
        return espacios // 4
    def condicion(self):
        izquierda = self.token_actual.valor
        self.comprobador("id")

        operador = self.token_actual.valor
        if operador == "==":
            self.comprobador("tk_igualdad")  
        elif operador == "!=":
            self.comprobador("tk_diferencia")
        else:
            raise SyntaxError(f"Operador no válido en la condición: {operador}")
        derecha = self.token_actual.valor
        self.comprobador("id")

        condicion_str = f"{izquierda} {operador} {derecha}"
        return condicion_str
    def parametros(self):
        parametros = []
        while True:  # Bucle principal para analizar múltiples parámetros
            if self.token_actual.tipo == "tk_llave_izq":  # Si es un array de enteros
                self.comprobador("tk_llave_izq")
                while self.token_actual.tipo == "tk_entero":
                    parametros.append(self.token_actual.valor)
                    self.comprobador("tk_entero")
                    if self.token_actual.tipo == "tk_coma":
                        self.comprobador("tk_coma")
                    else:
                        break
                self.comprobador("tk_llave_der")  # Cierra el arreglo

                # Verifica si hay más parámetros después del arreglo
                if self.token_actual.tipo == "tk_coma":
                    self.comprobador("tk_coma")
                    continue  # Continúa analizando más parámetros
                elif self.token_actual.tipo == "tk_par_der":
                    self.comprobador("tk_par_der")
                    break  # Fin de los parámetros
                else:
                    print(
                        f"<{self.token_actual.fila},{self.token_actual.columna}> Error sintáctico: "
                        f"se encontró \"{self.token_actual.valor}\"; se esperaba ',' o ')'."
                    )

            else:  # Si no es un arreglo, analiza parámetros simples
                while self.token_actual.tipo == "id" or self.token_actual.tipo == "tk_entero":

                    nombre_parametro = self.token_actual.valor

                    if self.token_actual.tipo == "id":
                        self.comprobador("id")
                    elif self.token_actual.tipo == "tk_entero":
                        
                        self.comprobador("tk_entero")
                    
                    if self.token_actual.tipo == "tk_dos_puntos":
                        
                        self.comprobador("tk_dos_puntos")
                        
                        if self.token_actual.tipo == "int":
                            self.comprobador("int")
                        elif self.token_actual.tipo == "tk_llave_izq":
                            self.comprobador("tk_llave_izq")
                            self.comprobador("int")
                            self.comprobador("tk_llave_der")

                    parametros.append(nombre_parametro)

                    # Verifica si hay más parámetros
                    if self.token_actual.tipo == "tk_coma":
                        self.comprobador("tk_coma")
                        continue  # Continúa analizando más parámetros
                    elif self.token_actual.tipo == "tk_par_der":
                        self.comprobador("tk_par_der")
                        break  # Fin de los parámetros
                    else:
                        raise SyntaxError(
                            f"<{self.token_actual.fila},{self.token_actual.columna}> Error sintáctico: "
                            f"se encontró \"{self.token_actual.valor}\"; se esperaba ',' o ')'."
                        )
            break  # Sale del bucle principal después de procesar parámetros simples

        return parametros
    def argumentos_print(self):
        while True:
            # Analiza el primer argumento (cadena, variable, número, etc.)
            print(self.token_actual.valor)
            if self.token_actual.tipo == "tk_comillas":
                self.comprobador("tk_comillas")
                self.comprobador("tk_cadena")
                self.comprobador("tk_comillas")
            elif self.token_actual.tipo == "id":
                self.comprobador("id")
            elif self.token_actual.tipo == "tk_entero":
                self.comprobador("tk_entero")
            else:
                raise SyntaxError(
                    f"<{self.token_actual.fila},{self.token_actual.columna}> Error sintáctico: "
                    f"se encontró \"{self.token_actual.valor}\"; se esperaba una cadena, variable o número."
                )

            # Verifica si hay una concatenación con el operador '+'
            if self.token_actual.tipo == "tk_suma":
                self.comprobador("tk_suma")
                continue  # Continúa analizando más argumentos
            else:
                break            
    def expresion(self):
        if self.token_actual.tipo == "if": 
            self.comprobador("if")
            if self.token_actual.tipo == "id":
                self.comprobador("id")
                self.comprobador("tk_par_izq")
                self.parametros()
            else:
                self.condicion()
            self.comprobador("tk_dos_puntos")
            self.indentacion_esperada += 1  # Incrementa el nivel de indentación esperado para el bloque if
            self.expresion()  # Procesa el bloque interno del if
            self.indentacion_esperada -= 1  # Reduce el nivel de indentación esperado después del bloque if

            # Manejo del else
            if self.token_actual.tipo == "else":
                self.comprobador("else")
                self.comprobador("tk_dos_puntos")
                self.indentacion_esperada += 1  # Incrementa el nivel de indentación esperado para el bloque else
                self.expresion()  # Procesa el bloque interno del else
                self.indentacion_esperada -= 1  # Reduce el nivel de indentación esperado después del bloque else

        elif self.token_actual.tipo == "for":
            self.comprobador("for")
            self.comprobador("id")
            self.comprobador("in")
            self.comprobador("id")
            self.comprobador("tk_dos_puntos")
            self.indentacion_esperada += 1  # Incrementa el nivel de indentación esperado
            self.expresion()  # Procesa el bloque interno
            self.indentacion_esperada -= 1  # Reduce el nivel de indentación esperado

        elif self.token_actual.tipo == "while":
            self.comprobador("while")
            self.comprobador("tk_par_izq")
            self.condicion()
            self.comprobador("tk_par_der")
            self.comprobador("tk_dos_puntos")
            self.indentacion_esperada += 1  # Incrementa el nivel de indentación esperado
            self.expresion()  # Procesa el bloque interno
            self.indentacion_esperada -= 1  # Reduce el nivel de indentación esperado

        elif self.token_actual.tipo == "def":
            self.comprobador("def")
            self.comprobador("id")
            self.comprobador("tk_par_izq")
            self.parametros()
            self.comprobador("tk_dos_puntos")
            self.indentacion_esperada += 1  # Incrementa el nivel de indentación esperado para el bloque def
            self.expresion()  # Procesa el bloque interno del def
            self.indentacion_esperada -= 1  # Reduce el nivel de indentación esperado después del bloque def

        elif self.token_actual.tipo == "print":  # Manejo de la función print
            self.comprobador("print")
            self.comprobador("tk_par_izq")  # Verifica el paréntesis de apertura
            self.argumentos_print()  # Analiza los argumentos dentro del print
            self.comprobador("tk_par_der")  # Verifica el paréntesis de cierre
            
    def parser(self):
        while self.token_actual.tipo != "EOF":  # Mientras no lleguemos al final del archivo
            self.linea_entera = self.scanner.obtener_linea_actual()
            
            if self.token_actual.fila != self.ultima_fila:
                self.nivel_indentacion = self.verificar_indentacion(self.linea_entera)
                
                if self.nivel_indentacion != self.indentacion_esperada:
                    print(f">>> Error de indentación (línea: {self.token_actual.fila}, posición: {self.token_actual.columna}): "
                        f"Se esperaba nivel de indentación {self.indentacion_esperada}, pero se encontró {self.nivel_indentacion}.")
                    sys.exit(1)
                self.ultima_fila = self.token_actual.fila
            self.expresion()
        print("Todo está correcto")
