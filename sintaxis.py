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

        for char in linea:
            if char == ' ':
                espacios += 1
                
            elif char == '\t':  # Detectar tabulaciones incorrectas
                print(f">>> Error de indentación (línea: {self.token_actual.fila}): No se permiten tabulaciones, usa espacios.")
                sys.exit(1)
            else:
                break  # Detenerse en el primer carácter que no sea espacio

        # ✅ Validar que la indentación es múltiplo de 4
        if espacios % 4 != 0:
            print(f">>> Error de indentación (línea: {self.token_actual.fila}): La indentación debe ser múltiplo de 4.")
            sys.exit(1)

        # ✅ Validar que la indentación encontrada es la esperada
        nivel_indentado = espacios // 4
        

        return nivel_indentado

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
                        sys.exit(1)
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

            # ✅ Incrementamos la indentación esperada
            self.indentacion_esperada += 1  
            self.token_actual = self.scanner.siguiente_token()

            self.verificar()
            # ✅ Reducimos la indentación esperada **antes de evaluar `else`**
            self.indentacion_esperada -= 1  

            # ✅ Verificar `else` solo si está al mismo nivel que `if`
            if self.nivel_indentacion == self.indentacion_esperada and self.token_actual.tipo == "else":
                self.comprobador("else")
                self.comprobador("tk_dos_puntos")

                # ✅ Volvemos a incrementar la indentación para el bloque `else`
                self.indentacion_esperada += 1  

                self.token_actual = self.scanner.siguiente_token()
                self.verificar()
                self.indentacion_esperada -= 1  # Reducimos indentación después de `else`

        elif self.token_actual.tipo == "for":
            self.comprobador("for")
            self.comprobador("id")
            self.comprobador("in")
            self.comprobador("id")
            self.comprobador("tk_dos_puntos")
            self.indentacion_esperada += 1  # Incrementa el nivel de indentación esperado
            self.token_actual = self.scanner.siguiente_token()

            self.verificar()  # Procesa el bloque interno
            self.indentacion_esperada -= 1  # Reduce el nivel de indentación esperado

        elif self.token_actual.tipo == "while":
            self.comprobador("while")
            self.comprobador("tk_par_izq")
            self.condicion()
            self.comprobador("tk_par_der")
            self.comprobador("tk_dos_puntos")
            self.indentacion_esperada += 1  # Incrementa el nivel de indentación esperado
            self.token_actual = self.scanner.siguiente_token()

            self.verificar()  # Procesa el bloque interno
            self.indentacion_esperada -= 1  # Reduce el nivel de indentación esperado

        elif self.token_actual.tipo == "def":
            self.comprobador("def")
            self.comprobador("id")
            self.comprobador("tk_par_izq")
            self.parametros()
            self.comprobador("tk_dos_puntos")
            self.indentacion_esperada += 1 # Incrementa el nivel de indentación esperado para el bloque def
            while self.token_actual.tipo != "EOF":
                if self.token_actual.fila != self.ultima_fila:
                    self.linea_entera = self.scanner.obtener_linea_actual()
                    self.nivel_indentacion = self.verificar_indentacion(self.linea_entera)

                    if self.nivel_indentacion < self.indentacion_esperada:
                        break  

                    self.ultima_fila = self.token_actual.fila  

                self.expresion()
                self.token_actual = self.scanner.siguiente_token()
            self.indentacion_esperada -= 1  # Reduce el nivel de indentación esperado después del bloque def

        elif self.token_actual.tipo == "print":  # Manejo de la función print
            self.comprobador("print")
            self.comprobador("tk_par_izq")  # Verifica el paréntesis de apertura
            self.argumentos_print()  # Analiza los argumentos dentro del print
            self.comprobador("tk_par_der")  # Verifica el paréntesis de cierre
            
    

    def parser(self):
        while self.token_actual.tipo != "EOF":
            # 🔥 Asegurar que se obtiene la línea actual SOLO cuando cambia la fila
            if self.token_actual.fila != self.ultima_fila:
                self.linea_entera = self.scanner.obtener_linea_actual()
                self.nivel_indentacion = self.verificar_indentacion(self.linea_entera)

                
                if self.nivel_indentacion < self.indentacion_esperada:
                    print(f">>> Error de indentación (línea: {self.token_actual.fila}): "
                          f"Se esperaba al menos {self.indentacion_esperada * 4} espacios, pero se encontraron {self.nivel_indentacion * 4}.")
                    sys.exit(1)

                self.ultima_fila = self.token_actual.fila  

            # ✅ Asegurar que los bloques internos se procesan con la indentación correcta
            if self.nivel_indentacion >= self.indentacion_esperada:
                self.expresion()  
            else:
                return 
    def verificar(self):
        # 🚨 Agregamos un indicador para verificar si hay al menos una línea correcta
        linea_valida_en_bloque = False  

        while self.token_actual.tipo != "EOF":
            if self.token_actual.fila != self.ultima_fila:
                self.linea_entera = self.scanner.obtener_linea_actual()
                self.nivel_indentacion = self.verificar_indentacion(self.linea_entera)

                if self.nivel_indentacion == self.indentacion_esperada:
                    linea_valida_en_bloque = True  # ✅ Se encontró al menos una línea con la indentación correcta
                
                # 🚨 Si encontramos una línea con indentación incorrecta, rompemos el bucle
                if self.nivel_indentacion < self.indentacion_esperada:
                    break  

                self.ultima_fila = self.token_actual.fila  

            self.expresion()
            self.token_actual = self.scanner.siguiente_token()
        # 🔥 Avanzamos el token después de procesar `expresion()`
        if self.token_actual.tipo != "EOF":
            self.token_actual = self.scanner.siguiente_token()
        # 🚨 Validar si **ninguna** línea dentro del bloque `if` tenía la indentación correcta
        if not linea_valida_en_bloque:
            print(f">>> Error de indentación (línea: {self.token_actual.fila}): "
                f"Ninguna línea dentro del bloque tiene la indentación esperada de {self.indentacion_esperada * 4} espacios.")
            sys.exit(1)
