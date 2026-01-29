import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib
import math

class CalculadoraWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Calculadora Científica GTK4")
        self.set_default_size(400, 600)
        
        # CSS para estilização moderna
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
            .display {
                font-size: 36px;
                font-family: monospace;
                padding: 20px;
                background: #1e1e1e;
                color: #ffffff;
                border-radius: 8px;
                margin: 10px;
            }
            .display-scientific {
                font-size: 14px;
                font-family: monospace;
                padding: 5px 20px;
                background: #2d2d2d;
                color: #aaaaaa;
                border-radius: 4px;
                margin: 0 10px;
            }
            .btn-num {
                background: #333333;
                color: white;
                font-size: 20px;
                border-radius: 50%;
                margin: 4px;
                min-height: 60px;
                min-width: 60px;
            }
            .btn-op {
                background: #ff9500;
                color: white;
                font-size: 20px;
                border-radius: 50%;
                margin: 4px;
                min-height: 60px;
                min-width: 60px;
            }
            .btn-func {
                background: #a5a5a5;
                color: black;
                font-size: 16px;
                border-radius: 50%;
                margin: 4px;
                min-height: 60px;
                min-width: 60px;
            }
            .btn-scientific {
                background: #2c3e50;
                color: #ecf0f1;
                font-size: 16px;
                border-radius: 12px;
                margin: 4px;
                min-height: 50px;
                font-weight: bold;
            }
            button:hover {
                opacity: 0.8;
                transform: scale(0.98);
            }
            button:active {
                transform: scale(0.95);
            }
        """)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Container principal
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        vbox.set_margin_top(20)
        vbox.set_margin_bottom(20)
        vbox.set_margin_start(20)
        vbox.set_margin_end(20)
        self.set_child(vbox)

        # Display secundário (para operação atual)
        self.display_scientific = Gtk.Label()
        self.display_scientific.add_css_class("display-scientific")
        self.display_scientific.set_xalign(1.0)  # Alinhar direita
        self.display_scientific.set_text("")
        vbox.append(self.display_scientific)

        # Display principal
        self.display = Gtk.Entry()
        self.display.set_alignment(1.0)
        self.display.set_editable(False)
        self.display.add_css_class("display")
        self.display.set_text("0")
        vbox.append(self.display)

        # Grid principal
        grid = Gtk.Grid()
        grid.set_row_homogeneous(True)
        grid.set_column_homogeneous(True)
        grid.set_row_spacing(6)
        grid.set_column_spacing(6)
        vbox.append(grid)

        # Estado
        self.valor_atual = "0"
        self.valor_anterior = None
        self.operacao = None
        self.novo_numero = True
        self.historico = ""  # Para mostrar operação no display secundário

        # Layout expandido com funções científicas
        # Formato: (label, row, col, width, style_class, callback)
        botoes = [
            # Linha 0: Funções científicas avançadas
            ('x²', 0, 0, 1, 'btn-scientific', self.on_quadrado),
            ('√x', 0, 1, 1, 'btn-scientific', self.on_raiz),
            ('log', 0, 2, 1, 'btn-scientific', self.on_log),
            ('ln', 0, 3, 1, 'btn-scientific', self.on_ln),
            
            # Linha 1: Mais funções científicas
            ('x^y', 1, 0, 1, 'btn-scientific', lambda b: self.on_operator('^')),
            ('10ˣ', 1, 1, 1, 'btn-scientific', self.on_exp10),
            ('eˣ', 1, 2, 1, 'btn-scientific', self.on_exp),
            ('π', 1, 3, 1, 'btn-scientific', self.on_pi),
            
            # Linha 2: Funções básicas de limpeza
            ('C', 2, 0, 1, 'btn-func', self.on_clear),
            ('CE', 2, 1, 1, 'btn-func', self.on_clear_entry),
            ('⌫', 2, 2, 1, 'btn-func', self.on_backspace),
            ('÷', 2, 3, 1, 'btn-op', lambda b: self.on_operator('÷')),
            
            # Linha 3: Números 7-9 e multiplicação
            ('7', 3, 0, 1, 'btn-num', lambda b: self.on_numero('7')),
            ('8', 3, 1, 1, 'btn-num', lambda b: self.on_numero('8')),
            ('9', 3, 2, 1, 'btn-num', lambda b: self.on_numero('9')),
            ('×', 3, 3, 1, 'btn-op', lambda b: self.on_operator('×')),
            
            # Linha 4: Números 4-6 e subtração
            ('4', 4, 0, 1, 'btn-num', lambda b: self.on_numero('4')),
            ('5', 4, 1, 1, 'btn-num', lambda b: self.on_numero('5')),
            ('6', 4, 2, 1, 'btn-num', lambda b: self.on_numero('6')),
            ('-', 4, 3, 1, 'btn-op', lambda b: self.on_operator('-')),
            
            # Linha 5: Números 1-3 e adição
            ('1', 5, 0, 1, 'btn-num', lambda b: self.on_numero('1')),
            ('2', 5, 1, 1, 'btn-num', lambda b: self.on_numero('2')),
            ('3', 5, 2, 1, 'btn-num', lambda b: self.on_numero('3')),
            ('+', 5, 3, 1, 'btn-op', lambda b: self.on_operator('+')),
            
            # Linha 6: Zero, decimal, igual e +/- 
            ('±', 6, 0, 1, 'btn-func', self.on_negate),
            ('0', 6, 1, 1, 'btn-num', lambda b: self.on_numero('0')),
            ('.', 6, 2, 1, 'btn-num', self.on_decimal),
            ('=', 6, 3, 1, 'btn-op', self.on_igual),
        ]

        for label, row, col, width, style, callback in botoes:
            btn = Gtk.Button(label=label)
            btn.add_css_class(style)
            btn.set_hexpand(True)
            btn.set_vexpand(True)
            grid.attach(btn, col, row, width, 1)
            btn.connect('clicked', callback)

        # Atalhos de teclado
        key_controller = Gtk.EventControllerKey()
        key_controller.connect('key-pressed', self.on_key_pressed)
        self.add_controller(key_controller)

    def atualizar_display(self):
        self.display.set_text(self.valor_atual)
        if self.valor_anterior is not None and self.operacao:
            op_symbol = self.operacao if self.operacao != '^' else '^'
            self.display_scientific.set_text(f"{self._format_num(self.valor_anterior)} {op_symbol}")
        else:
            self.display_scientific.set_text("")

    def _format_num(self, num):
        """Formata número para display, removendo .0 desnecessários"""
        if isinstance(num, str):
            try:
                num = float(num)
            except:
                return num
        if num == int(num):
            return str(int(num))
        return str(num)

    def on_numero(self, num):
        if self.novo_numero:
            self.valor_atual = num
            self.novo_numero = False
        else:
            if self.valor_atual == "0":
                self.valor_atual = num
            else:
                self.valor_atual += num
        self.atualizar_display()

    def on_decimal(self, btn):
        if self.novo_numero:
            self.valor_atual = "0."
            self.novo_numero = False
        elif "." not in self.valor_atual:
            self.valor_atual += "."
        self.atualizar_display()

    def on_clear(self, btn):
        self.valor_atual = "0"
        self.valor_anterior = None
        self.operacao = None
        self.novo_numero = True
        self.atualizar_display()

    def on_clear_entry(self, btn):
        self.valor_atual = "0"
        self.novo_numero = True
        self.atualizar_display()

    def on_backspace(self, btn):
        if len(self.valor_atual) > 1:
            self.valor_atual = self.valor_atual[:-1]
        else:
            self.valor_atual = "0"
            self.novo_numero = True
        self.atualizar_display()

    def on_negate(self, btn):
        if self.valor_atual != "0":
            if self.valor_atual.startswith("-"):
                self.valor_atual = self.valor_atual[1:]
            else:
                self.valor_atual = "-" + self.valor_atual
            self.atualizar_display()

    def on_pi(self, btn):
        self.valor_atual = str(math.pi)
        self.novo_numero = True
        self.atualizar_display()

    # NOVAS FUNÇÕES CIENTÍFICAS
    def on_quadrado(self, btn):
        """x ao quadrado"""
        try:
            val = float(self.valor_atual)
            resultado = val ** 2
            self.valor_atual = self._formatar_resultado(resultado)
            self.novo_numero = True
            self.atualizar_display()
        except Exception as e:
            self._erro()

    def on_raiz(self, btn):
        """Raiz quadrada"""
        try:
            val = float(self.valor_atual)
            if val < 0:
                self.valor_atual = "Erro"
            else:
                resultado = math.sqrt(val)
                self.valor_atual = self._formatar_resultado(resultado)
            self.novo_numero = True
            self.atualizar_display()
        except:
            self._erro()

    def on_log(self, btn):
        """Logaritmo base 10"""
        try:
            val = float(self.valor_atual)
            if val <= 0:
                self.valor_atual = "Erro"
            else:
                resultado = math.log10(val)
                self.valor_atual = self._formatar_resultado(resultado)
            self.novo_numero = True
            self.atualizar_display()
        except:
            self._erro()

    def on_ln(self, btn):
        """Logaritmo natural (ln)"""
        try:
            val = float(self.valor_atual)
            if val <= 0:
                self.valor_atual = "Erro"
            else:
                resultado = math.log(val)
                self.valor_atual = self._formatar_resultado(resultado)
            self.novo_numero = True
            self.atualizar_display()
        except:
            self._erro()

    def on_exp(self, btn):
        """e^x (exponencial natural)"""
        try:
            val = float(self.valor_atual)
            resultado = math.exp(val)
            self.valor_atual = self._formatar_resultado(resultado)
            self.novo_numero = True
            self.atualizar_display()
        except:
            self._erro()

    def on_exp10(self, btn):
        """10^x"""
        try:
            val = float(self.valor_atual)
            resultado = 10 ** val
            self.valor_atual = self._formatar_resultado(resultado)
            self.novo_numero = True
            self.atualizar_display()
        except:
            self._erro()

    def _formatar_resultado(self, resultado):
        """Formata resultado evitando notação científica para números pequenos"""
        if isinstance(resultado, (int, float)):
            if abs(resultado) > 1e10 or (abs(resultado) < 1e-10 and resultado != 0):
                return "{:.6e}".format(resultado)
            elif resultado == int(resultado):
                return str(int(resultado))
            else:
                # Limitar casas decimais
                s = "{:.10f}".format(resultado).rstrip('0').rstrip('.')
                return s
        return str(resultado)

    def _erro(self):
        self.valor_atual = "Erro"
        self.novo_numero = True
        self.atualizar_display()

    def on_operator(self, op):
        if self.operacao is not None and not self.novo_numero:
            self.calcular_intermediario()
        
        self.valor_anterior = float(self.valor_atual)
        self.operacao = op
        self.novo_numero = True
        self.atualizar_display()

    def calcular_intermediario(self):
        """Calcula resultado parcial para operações encadeadas"""
        try:
            atual = float(self.valor_atual)
            if self.operacao == '^':
                resultado = self.valor_anterior ** atual
            else:
                return  # Apenas exponencial precisa de cálculo intermediário aqui
            
            self.valor_anterior = resultado
            self.valor_atual = self._formatar_resultado(resultado)
            self.atualizar_display()
        except:
            pass

    def on_igual(self, btn):
        if self.operacao is None or self.valor_anterior is None:
            return
        
        try:
            atual = float(self.valor_atual)
            resultado = 0
            
            if self.operacao == '+':
                resultado = self.valor_anterior + atual
            elif self.operacao == '-':
                resultado = self.valor_anterior - atual
            elif self.operacao == '×':
                resultado = self.valor_anterior * atual
            elif self.operacao == '÷':
                if atual == 0:
                    self._erro()
                    return
                resultado = self.valor_anterior / atual
            elif self.operacao == '^':
                resultado = self.valor_anterior ** atual
            
            self.valor_atual = self._formatar_resultado(resultado)
            self.operacao = None
            self.valor_anterior = None
            self.novo_numero = True
            self.atualizar_display()
            
        except Exception as e:
            self._erro()

    def on_key_pressed(self, controller, keyval, keycode, state):
        key = Gdk.keyval_name(keyval)
        
        # Números
        if key in '0123456789':
            self.on_numero(key)
            return True
        elif key == 'period' or key == 'comma':
            self.on_decimal(None)
            return True
        # Operadores
        elif key in ['plus', 'KP_Add']:
            self.on_operator('+')
            return True
        elif key in ['minus', 'KP_Subtract']:
            self.on_operator('-')
            return True
        elif key in ['asterisk', 'KP_Multiply']:
            self.on_operator('×')
            return True
        elif key in ['slash', 'KP_Divide']:
            self.on_operator('÷')
            return True
        elif key == 'asciicircum':  # ^ para exponencial
            self.on_operator('^')
            return True
        # Ações
        elif key in ['Return', 'KP_Enter', 'equal']:
            self.on_igual(None)
            return True
        elif key == 'Escape':
            self.on_clear(None)
            return True
        elif key == 'BackSpace':
            self.on_backspace(None)
            return True
        
        return False

class CalculadoraApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='com.exemplo.calculadora.cientifica')
    
    def do_activate(self):
        win = CalculadoraWindow(application=self)
        win.present()

def main():
    app = CalculadoraApp()
    app.run(None)

if __name__ == '__main__':
    main()