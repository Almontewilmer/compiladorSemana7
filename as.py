import tkinter as tk
from tkinter import ttk, scrolledtext
from ply import lex, yacc

# ==========================
# Analizador Léxico
# ==========================
tokens = (
    'NUMBER', 'PLUS', 'MINUS', 'MULT', 'DIV', 'LPAREN', 'RPAREN', 'ID', 'EQUAL'
)

t_PLUS = r'\+'
t_MINUS = r'-'
t_MULT = r'\*'
t_DIV = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EQUAL = r'='
t_ignore = ' \t'


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    t.lexer.skip(1)


lexer = lex.lex()

# ==========================
# Analizador Sintáctico
# ==========================
symbol_table = {}


def p_statement_assign(p):
    'statement : ID EQUAL expression'
    symbol_table[p[1]] = p[3]
    p[0] = f"{p[1]} = {p[3]}"  # Guardamos la asignación en p[0]


def p_statement_expr(p):
    'statement : expression'
    p[0] = p[1]  # Asignamos el valor de la expresión a p[0]


def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression MULT expression
                  | expression DIV expression'''
    if p[2] == '+':
        p[0] = p[1] + p[3]
    elif p[2] == '-':
        p[0] = p[1] - p[3]
    elif p[2] == '*':
        p[0] = p[1] * p[3]
    elif p[2] == '/':
        p[0] = p[1] / p[3]


def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]


def p_expression_number(p):
    'expression : NUMBER'
    p[0] = p[1]


def p_expression_id(p):
    'expression : ID'
    if p[1] in symbol_table:
        p[0] = symbol_table[p[1]]
    else:
        p[0] = f"Error: Variable '{p[1]}' no definida."


def p_error(p):
    if p:
        p[0] = f"Error: Sintaxis inválida en '{p.value}'"
    else:
        p[0] = "Error de sintaxis en entrada."


parser = yacc.yacc()


# ==========================
# Interfaz Gráfica
# ==========================
class CompilerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Compilador Básico")

        # Área de entrada de código
        self.code_label = ttk.Label(root, text="Código Fuente:")
        self.code_label.grid(column=0, row=0, padx=10, pady=10, sticky='W')

        self.code_text = scrolledtext.ScrolledText(root, width=60, height=15)
        self.code_text.grid(column=0, row=1, padx=10, pady=10, columnspan=2)

        # Botón de Compilar
        self.compile_button = ttk.Button(root, text="Compilar", command=self.compile_code)
        self.compile_button.grid(column=0, row=2, padx=10, pady=10)

        # Salida: Tokens Léxicos
        self.lexical_label = ttk.Label(root, text="Tokens Léxicos:")
        self.lexical_label.grid(column=0, row=3, padx=10, pady=10, sticky='W')

        self.lexical_text = scrolledtext.ScrolledText(root, width=40, height=10, state='disabled')
        self.lexical_text.grid(column=0, row=4, padx=10, pady=10)

        # Salida: Tabla de Símbolos
        self.symbol_table_label = ttk.Label(root, text="Tabla de Símbolos:")
        self.symbol_table_label.grid(column=1, row=3, padx=10, pady=10, sticky='W')

        self.symbol_table_text = scrolledtext.ScrolledText(root, width=40, height=10, state='disabled')
        self.symbol_table_text.grid(column=1, row=4, padx=10, pady=10)

        # Salida: Análisis Sintáctico
        self.syntax_label = ttk.Label(root, text="Análisis Sintáctico:")
        self.syntax_label.grid(column=0, row=5, padx=10, pady=10, sticky='W')

        self.syntax_text = scrolledtext.ScrolledText(root, width=60, height=10, state='disabled')
        self.syntax_text.grid(column=0, row=6, padx=10, pady=10, columnspan=2)

    def compile_code(self):
        code = self.code_text.get("1.0", tk.END).strip()  # Obtener el código y eliminar espacios en blanco

        if not code:  # Si el campo de código está vacío
            self.syntax_text.config(state='normal')
            self.syntax_text.delete("1.0", tk.END)
            self.syntax_text.insert(tk.END, "Por favor, ingrese algún código.")
            self.syntax_text.config(state='disabled')
            return

        lexer.input(code)

        # Análisis Léxico
        tokens_output = ""
        for token in lexer:
            tokens_output += f"{token.type}({token.value}) en línea {token.lineno}\n"

        # Mostrar Tokens
        self.lexical_text.config(state='normal')
        self.lexical_text.delete("1.0", tk.END)
        self.lexical_text.insert(tk.END, tokens_output)
        self.lexical_text.config(state='disabled')

        # Análisis Sintáctico (todo el bloque de código)
        try:
            result = parser.parse(code)
            if isinstance(result, str) and "Error" in result:
                self.syntax_text.config(state='normal')
                self.syntax_text.delete("1.0", tk.END)
                self.syntax_text.insert(tk.END, result)  # Error de sintaxis
                self.syntax_text.config(state='disabled')
            else:
                self.syntax_text.config(state='normal')
                self.syntax_text.delete("1.0", tk.END)
                self.syntax_text.insert(tk.END, "Análisis sintáctico exitoso.")
                self.syntax_text.config(state='disabled')
        except Exception as e:
            self.syntax_text.config(state='normal')
            self.syntax_text.delete("1.0", tk.END)
            self.syntax_text.insert(tk.END, f"Error: {str(e)}")
            self.syntax_text.config(state='disabled')

        # Mostrar Tabla de Símbolos
        self.symbol_table_text.config(state='normal')
        self.symbol_table_text.delete("1.0", tk.END)
        for key, value in symbol_table.items():
            self.symbol_table_text.insert(tk.END, f"{key}: {value}\n")
        self.symbol_table_text.config(state='disabled')


# ==========================
# Ejecutar Aplicación
# ==========================
if __name__ == "__main__":
    root = tk.Tk()
    app = CompilerApp(root)
    root.mainloop()
