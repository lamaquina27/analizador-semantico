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
        if self.token_actual.tipo in ("id", "tk_entero"):
            izquierda = self.token_actual.valor
            self.comprobador(self.token_actual.tipo)
        else:
            print(f"<{self.token_actual.fila},{self.token_actual.columna}> Error sintáctico: se esperaba variable o número.")
            sys.exit(1)

        operador = self.token_actual.valor
        if operador == "==":
            self.comprobador("tk_igualdad")  
        elif operador == "!=":
            self.comprobador("tk_diferencia")
        elif operador == ">":
            self.comprobador("tk_mayorque")
        elif operador == "<":
            self.comprobador("tk_menorque")
        elif operador == ">=":
            self.comprobador("tk_mayorigual")
        elif operador == "<=":
            self.comprobador("tk_menorigual")
        else:
            print(f"<{self.token_actual.fila},{self.token_actual.columna}> Error sintáctico: operador no válido en la condición: {operador}")
            sys.exit(1)

        if self.token_actual.tipo in ("id", "tk_entero"):
            derecha = self.token_actual.valor
            self.comprobador(self.token_actual.tipo)
        else:
            print(f"<{self.token_actual.fila},{self.token_actual.columna}> Error sintáctico: se esperaba variable o número.")
            sys.exit(1)

    def parametros(self):
        parametros = []

        while True:
            if self.token_actual.tipo == "id":
                nombre = self.token_actual.valor
                self.comprobador("id")

                if self.token_actual.tipo == "tk_dos_puntos":
                    self.comprobador("tk_dos_puntos")
                    if self.token_actual.tipo == "int":
                        self.comprobador("int")
                    elif self.token_actual.tipo == "tk_llave_izq":
                        self.comprobador("tk_llave_izq")
                        self.comprobador("int")
                        self.comprobador("tk_llave_der")
                    else:
                        self.error_parametro()
                parametros.append(nombre)

            elif self.token_actual.tipo == "tk_llave_izq":
                self.comprobador("tk_llave_izq")
                while self.token_actual.tipo == "tk_entero":
                    parametros.append(self.token_actual.valor)
                    self.comprobador("tk_entero")
                    if self.token_actual.tipo == "tk_coma":
                        self.comprobador("tk_coma")
                    else:
                        break
                self.comprobador("tk_llave_der")

            else:
                break

            if self.token_actual.tipo == "tk_coma":
                self.comprobador("tk_coma")
            elif self.token_actual.tipo == "tk_par_der":
                self.comprobador("tk_par_der")
                break
            else:
                self.error_parametro()

        return parametros

    def error_parametro(self):
        print(f"<{self.token_actual.fila},{self.token_actual.columna}> Error sintáctico en parámetro.")
        sys.exit(1)

    def argumentos_print(self):
        while True:
            
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
        token_tipo = self.token_actual.tipo
        if token_tipo == "if":
            self.analizar_if()
        elif token_tipo == "for":
            self.analizar_for()
        elif token_tipo == "while":
            self.analizar_while()
        elif token_tipo == "def":
            self.analizar_def()
        elif token_tipo == "print":
            self.analizar_print()
        
        elif token_tipo == "id":
            if self.peek_token().tipo == "tk_par_izq":
                self.analizar_llamada_funcion()
            elif self.peek_token().tipo == "tk_asig":
                self.analizar_asignacion()
            
            else:
                print(f"<{self.token_actual.fila},{self.token_actual.columna}> Error sintáctico: '{self.token_actual.valor}' no es una instrucción válida.")
                sys.exit(1)
    def analizar_operacion(self):
        self.operacion()
    def operacion(self):
        self.termino()
        while self.token_actual.tipo in ("tk_suma", "tk_menos"):
            self.comprobador(self.token_actual.tipo)
            self.termino()
    def termino(self):
        self.factor()
        while self.token_actual.tipo in ("tk_multiplicacion", "tk_division"):
            self.comprobador(self.token_actual.tipo)
            self.factor()
    def factor(self):
        if self.token_actual.tipo == "tk_par_izq":
            self.comprobador("tk_par_izq")
            self.operacion()
            self.comprobador("tk_par_der")
        elif self.token_actual.tipo in ("tk_entero", "id"):
            self.comprobador(self.token_actual.tipo)
        else:
            print(f"<{self.token_actual.fila},{self.token_actual.columna}> Error: se esperaba número, variable o paréntesis.")
            sys.exit(1)

    def peek_token(self):
        if self.scanner.tokens:
            return self.scanner.tokens[0]
        return lexico.Token("EOF", "", -1, -1)

    def analizar_if(self):
        self.comprobador("if")
        self.condicion()
        self.comprobador("tk_dos_puntos")

        self.indentacion_esperada += 1

        # ✅ Avanzamos solo si cambia de línea (como ya haces en parser)
        self.token_actual = self.scanner.siguiente_token()

        self.verificar()
        self.indentacion_esperada -= 1

        # ✅ Si viene un else, se debe validar que esté al mismo nivel de indentación
        if self.token_actual.tipo == "else":
            if self.nivel_indentacion != self.indentacion_esperada:
                print(f">>> Error de indentación (línea: {self.token_actual.fila}): else mal indentado.")
                sys.exit(1)

            self.comprobador("else")
            self.comprobador("tk_dos_puntos")
            self.indentacion_esperada += 1
            self.token_actual = self.scanner.siguiente_token()
            self.verificar()
            self.indentacion_esperada -= 1


    def analizar_for(self):
        self.comprobador("for")
        self.comprobador("id")
        self.comprobador("in")
        self.comprobador("id")
        self.comprobador("tk_dos_puntos")
        self.indentacion_esperada += 1
        self.token_actual = self.scanner.siguiente_token()
        self.verificar()
        self.indentacion_esperada -= 1

    def analizar_while(self):
        self.comprobador("while")
        
        self.condicion()
        
        self.comprobador("tk_dos_puntos")
        self.indentacion_esperada += 1
        self.token_actual = self.scanner.siguiente_token()
        self.verificar()
        self.indentacion_esperada -= 1

    def analizar_def(self):
        self.comprobador("def")
        self.comprobador("id")
        self.comprobador("tk_par_izq")
        if self.token_actual.tipo != 'tk_par_der':
            self.parametros()
        else:
            self.comprobador("tk_par_der")
        self.comprobador("tk_dos_puntos")
        self.indentacion_esperada += 1
        self.token_actual = self.scanner.siguiente_token()
        self.verificar()
        self.indentacion_esperada -= 1
    def analizar_llamada_funcion(self):
        self.comprobador("id")
        self.comprobador("tk_par_izq")

        while self.token_actual.tipo not in ("tk_par_der", "EOF"):
            if self.token_actual.tipo in ("id", "tk_entero", "tk_cadena"):
                self.comprobador(self.token_actual.tipo)
            elif self.token_actual.tipo == "tk_llave_izq":
                self.comprobador("tk_llave_izq")
                while self.token_actual.tipo == "tk_entero":
                    self.comprobador("tk_entero")
                    if self.token_actual.tipo == "tk_coma":
                        self.comprobador("tk_coma")
                    else:
                        break
                self.comprobador("tk_llave_der")
            else:
                print(f"<{self.token_actual.fila},{self.token_actual.columna}> Error: argumento inválido.")
                sys.exit(1)

            if self.token_actual.tipo == "tk_coma":
                self.comprobador("tk_coma")
            else:
                break

        self.comprobador("tk_par_der")

    def analizar_print(self):
        self.comprobador("print")
        self.comprobador("tk_par_izq")
        self.argumentos_print()
        self.comprobador("tk_par_der")
    def analizar_asignacion(self):
        self.comprobador("id")
        self.comprobador("tk_asig")

        # Valor de la asignación: puede ser id, entero, cadena o llamada a función
        if self.token_actual.tipo in ("tk_entero", "id", "tk_comillas",'tk_par_izq'):
            if self.token_actual.tipo == "tk_comillas":
                self.comprobador("tk_comillas")
                self.comprobador("tk_cadena")
                self.comprobador("tk_comillas")
            else:
                
                self.analizar_operacion()
        elif self.token_actual.tipo == "id" and self.peek_token().tipo == "tk_par_izq":
            self.analizar_llamada_funcion()
        else:
            print(f"<{self.token_actual.fila},{self.token_actual.columna}> Error sintáctico: valor de asignación inválido.")
            sys.exit(1)

                
    

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
                self.token_actual = self.scanner.siguiente_token()
            else:
                return 
    def verificar(self):
        linea_valida_en_bloque = False  

        while self.token_actual.tipo != "EOF":
            if self.token_actual.fila != self.ultima_fila:
                self.linea_entera = self.scanner.obtener_linea_actual()
                self.nivel_indentacion = self.verificar_indentacion(self.linea_entera)

                # 🔥 Verifica que el else mal indentado no se cuele fuera de su bloque
                if self.token_actual.tipo == "else" and self.nivel_indentacion != self.indentacion_esperada:
                    print(f">>> Error de indentación (línea: {self.token_actual.fila}): else mal indentado.")
                    sys.exit(1)

                # 🚨 Si la indentación es menor, salimos del bloque
                if self.nivel_indentacion < self.indentacion_esperada:
                    break  

                self.ultima_fila = self.token_actual.fila  

            self.expresion()
            self.token_actual = self.scanner.siguiente_token()

            linea_valida_en_bloque = True

        if not linea_valida_en_bloque:
            print(f">>> Error de indentación (línea: {self.token_actual.fila}): "
                f"Ninguna línea dentro del bloque tiene la indentación esperada de {self.indentacion_esperada * 4} espacios.")
            sys.exit(1)
