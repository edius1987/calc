import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib, Gio
import math
from datetime import datetime

class HistoricoRow(Gtk.Box):
    """Widget customizado para cada item do histórico"""
    def __init__(self, expressao, resultado, parent_window):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.expressao = expressao
        self.resultado = resultado
        self.parent_window = parent_window
        
        self.set_margin_top(6)
        self.set_margin_bottom(6)
        self.set_margin_start(12)
        self.set_margin_end(12)
        
        # Label da expressão
        self.label_expr = Gtk.Label()
        self.label_expr.set_text(expressao)
        self.label_expr.set_xalign(1.0)
        self.label_expr.add_css_class("historico-expr")
        
        # Label do resultado
        self.label_res = Gtk.Label()
        self.label_res.set_text(f"= {resultado}")
        self.label_res.set_xalign(1.0)
        self.label_res.add_css_class("historico-res")
        
        self.append(self.label_expr)
        self.append(self.label_res)
        
        # Gesture para detectar clique
        gesture = Gtk.GestureClick()
        gesture.connect("pressed", self.on_clicked)
        self.add_controller(gesture)
        
        # Hover effect
        self.add_css_class("historico-row")
    
    def on_clicked(self, gesture, n_press, x, y):
        if n_press == 1:  # Clique simples - carrega resultado
            self.parent_window.carregar_valor(self.resultado)
        elif n_press == 2:  # Duplo clique - carrega expressão completa
            self.parent_window.carregar_valor(self.resultado)

class CalculadoraWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Calculadora Científica com Histórico")
        self.set_default_size(800, 650)
        
        # CSS atualizado
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
                font-size: 18px;
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
            .btn-historico {
                background: #7f8c8d;
                color: white;
                font-size: 14px;
                border-radius: 8px;
                margin: 4px;
                padding: 8px;
            }
            .historico-container {
                background: #252525;
                border-left: 2px solid #333;
            }
            .historico-header {
                font-size: 16px;
                font-weight: bold;
                color: #ecf0f1;
                padding: 15px;
                background: #2c3e50;
            }
            .historico-row {
                background: #333;
                border-radius: 8px;
                margin: 4px 8px;
                padding: 8px;
            }
            .historico-row:hover {
                background: #444;
            }
            .historico-expr {
                font-size: 13px;
                color: #aaa;
                font-family: monospace;
            }
            .historico-res {
                font-size: 18px;
                color: #fff;
                font-family: monospace;
                font-weight: bold;
            }
            .historico-vazio {
                color: #666;
                font-style: italic;
                padding: 20px;
            }
            button:hover {
                opacity: 0.9;
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

        # Paned para dividir calculadora e histórico
        self.paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.set_child(self.paned)
        
        # Lado esquerdo: Calculadora
        self.calc_box = self._criar_calculadora()
        self.paned.set_start_child(self.calc_box)
        self.paned.set_position(480)  # Largura inicial da calculadora
        
        # Lado direito: Histórico
        self.historico_box = self._criar_historico_panel()
        self.paned.set_end_child(self.historico_box)
        
        # Dados do histórico
        self.historico_lista = []
        
        # Atalhos de teclado
        key_controller = Gtk.EventControllerKey()
        key_controller.connect('key-pressed', self.on_key_pressed)
        self.add_controller(key_controller)

    def _criar_calculadora(self):
        """Cria o lado esquerdo com a calculadora"""
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        vbox.set_margin_top(20)
        vbox.set_margin_bottom(20)
        vbox.set_margin_start(20)
        vbox.set_margin_end(20)
        vbox.set_size_request(400, -1)  # Largura mínima
        
        # Display secundário (operação atual)
        self.display_scientific = Gtk.Label()
        self.display_scientific.add_css_class("display-scientific")
        self.display_scientific.set_xalign(1.0)
        self.display_scientific.set_text("")
        vbox.append(self.display_scientific)
        
        # Display principal
        self.display = Gtk.Entry()
        self.display.set_alignment(1.0)
        self.display.set_editable(False)
        self.display.add_css_class("display")
        self.display.set_text("0")
        vbox.append(self.display)
        
        # Grid de botões
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
        
        # Layout dos botões
        botoes = [
            # Científicas
            ('x²', 0, 0, 1, 'btn-scientific', self.on_quadrado),
            ('√x', 0, 1, 1, 'btn-scientific', self.on_raiz),
            ('log', 0, 2, 1, 'btn-scientific', self.on_log),
            ('ln', 0, 3, 1, 'btn-scientific', self.on_ln),
            
            ('x^y', 1, 0, 1, 'btn-scientific', lambda b: self.on_operator('^')),
            ('10ˣ', 1, 1, 1, 'btn-scientific', self.on_exp10),
            ('eˣ', 1, 2, 1, 'btn-scientific', self.on_exp),
            ('π', 1, 3, 1, 'btn-scientific', self.on_pi),
            
            # Básicas
            ('C', 2, 0, 1, 'btn-func', self.on_clear),
            ('CE', 2, 1, 1, 'btn-func', self.on_clear_entry),
            ('⌫', 2, 2, 1, 'btn-func', self.on_backspace),
            ('÷', 2, 3, 1, 'btn-op', lambda b: self.on_operator('÷')),
            
            ('7', 3, 0, 1, 'btn-num', lambda b: self.on_numero('7')),
            ('8', 3, 1, 1, 'btn-num', lambda b: self.on_numero('8')),
            ('9', 3, 2, 1, 'btn-num', lambda b: self.on_numero('9')),
            ('×', 3, 3, 1, 'btn-op', lambda b: self.on_operator('×')),
            
            ('4', 4, 0, 1, 'btn-num', lambda b: self.on_numero('4')),
            ('5', 4, 1, 1, 'btn-num', lambda b: self.on_numero('5')),
            ('6', 4, 2, 1, 'btn-num', lambda b: self.on_numero('6')),
            ('-', 4, 3, 1, 'btn-op', lambda b: self.on_operator('-')),
            
            ('1', 5, 0, 1, 'btn-num', lambda b: self.on_numero('1')),
            ('2', 5, 1, 1, 'btn-num', lambda b: self.on_numero('2')),
            ('3', 5, 2, 1, 'btn-num', lambda b: self.on_numero('3')),
            ('+', 5, 3, 1, 'btn-op', lambda b: self.on_operator('+')),
            
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
        
        return vbox

    def _criar_historico_panel(self):
        """Cria o lado direito com o histórico"""
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vbox.add_css_class("historico-container")
        vbox.set_size_request(250, -1)
        
        # Header
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header_box.set_margin_start(12)
        header_box.set_margin_end(12)
        header_box.set_margin_top(12)
        header_box.set_margin_bottom(12)
        
        title = Gtk.Label()
        title.set_text("📜 Histórico")
        title.add_css_class("historico-header")
        title.set_hexpand(True)
        title.set_xalign(0.0)
        
        btn_limpar = Gtk.Button(label="Limpar")
        btn_limpar.add_css_class("btn-historico")
        btn_limpar.connect("clicked", self.on_limpar_historico)
        
        header_box.append(title)
        header_box.append(btn_limpar)
        vbox.append(header_box)
        
        # Lista scrollável
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        self.historico_listbox = Gtk.ListBox()
        self.historico_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.historico_listbox.add_css_class("historico-list")
        
        # Placeholder quando vazio
        self.placeholder = Gtk.Label()
        self.placeholder.set_text("Nenhuma operação realizada")
        self.placeholder.add_css_class("historico-vazio")
        self.historico_listbox.set_placeholder(self.placeholder)
        
        scroll.set_child(self.historico_listbox)
        vbox.append(scroll)
        
        # Label de status
        self.status_label = Gtk.Label()
        self.status_label.set_margin_top(8)
        self.status_label.set_margin_bottom(8)
        self.status_label.set_text("Clique no item para reutilizar")
        self.status_label.add_css_class("historico-expr")
        vbox.append(self.status_label)
        
        return vbox

    def adicionar_ao_historico(self, expressao, resultado):
        """Adiciona operação ao histórico"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        item = {
            'expressao': expressao,
            'resultado': resultado,
            'hora': timestamp
        }
        self.historico_lista.insert(0, item)  # Adiciona no início
        
        # Cria widget visual
        row_widget = HistoricoRow(expressao, resultado, self)
        self.historico_listbox.prepend(row_widget)  # Adiciona no topo da lista
        
        # Animação sutil
        row_widget.set_opacity(0)
        def fade_in():
            row_widget.set_opacity(1)
            return False
        GLib.timeout_add(50, fade_in)

    def on_limpar_historico(self, btn):
        """Limpa todo o histórico"""
        self.historico_lista.clear()
        while True:
            row = self.historico_listbox.get_first_child()
            if row is None:
                break
            self.historico_listbox.remove(row)

    def carregar_valor(self, valor):
        """Carrega um valor do histórico para o display"""
        self.valor_atual = str(valor)
        self.novo_numero = True
        self.atualizar_display()
        
        # Feedback visual no status
        self.status_label.set_text(f"Valor {valor} carregado!")
        GLib.timeout_add(2000, lambda: self.status_label.set_text("Clique no item para reutilizar") or False)

    def atualizar_display(self):
        self.display.set_text(self.valor_atual)
        if self.valor_anterior is not None and self.operacao:
            op_map = {'^': '^', '÷': '/', '×': '*'}
            op_str = op_map.get(self.operacao, self.operacao)
            self.display_scientific.set_text(f"{self._format_num(self.valor_anterior)} {op_str}")
        else:
            self.display_scientific.set_text("")

    def _format_num(self, num):
        if isinstance(num, str):
            try:
                num = float(num)
            except:
                return num
        if num == int(num):
            return str(int(num))
        return str(num)

    def _formatar_resultado(self, resultado):
        if isinstance(resultado, (int, float)):
            if abs(resultado) > 1e10 or (abs(resultado) < 1e-10 and resultado != 0):
                return "{:.6e}".format(resultado)
            elif resultado == int(resultado):
                return str(int(resultado))
            else:
                s = "{:.10f}".format(resultado).rstrip('0').rstrip('.')
                return s
        return str(resultado)

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

    def on_quadrado(self, btn):
        try:
            val = float(self.valor_atual)
            resultado = val ** 2
            res_str = self._formatar_resultado(resultado)
            self.adicionar_ao_historico(f"sqr({self._format_num(val)})", res_str)
            self.valor_atual = res_str
            self.novo_numero = True
            self.atualizar_display()
        except:
            self._erro()

    def on_raiz(self, btn):
        try:
            val = float(self.valor_atual)
            if val < 0:
                self.valor_atual = "Erro"
            else:
                resultado = math.sqrt(val)
                res_str = self._formatar_resultado(resultado)
                self.adicionar_ao_historico(f"√({self._format_num(val)})", res_str)
                self.valor_atual = res_str
            self.novo_numero = True
            self.atualizar_display()
        except:
            self._erro()

    def on_log(self, btn):
        try:
            val = float(self.valor_atual)
            if val <= 0:
                self.valor_atual = "Erro"
            else:
                resultado = math.log10(val)
                res_str = self._formatar_resultado(resultado)
                self.adicionar_ao_historico(f"log({self._format_num(val)})", res_str)
                self.valor_atual = res_str
            self.novo_numero = True
            self.atualizar_display()
        except:
            self._erro()

    def on_ln(self, btn):
        try:
            val = float(self.valor_atual)
            if val <= 0:
                self.valor_atual = "Erro"
            else:
                resultado = math.log(val)
                res_str = self._formatar_resultado(resultado)
                self.adicionar_ao_historico(f"ln({self._format_num(val)})", res_str)
                self.valor_atual = res_str
            self.novo_numero = True
            self.atualizar_display()
        except:
            self._erro()

    def on_exp(self, btn):
        try:
            val = float(self.valor_atual)
            resultado = math.exp(val)
            res_str = self._formatar_resultado(resultado)
            self.adicionar_ao_historico(f"e^({self._format_num(val)})", res_str)
            self.valor_atual = res_str
            self.novo_numero = True
            self.atualizar_display()
        except:
            self._erro()

    def on_exp10(self, btn):
        try:
            val = float(self.valor_atual)
            resultado = 10 ** val
            res_str = self._formatar_resultado(resultado)
            self.adicionar_ao_historico(f"10^({self._format_num(val)})", res_str)
            self.valor_atual = res_str
            self.novo_numero = True
            self.atualizar_display()
        except:
            self._erro()

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
        try:
            atual = float(self.valor_atual)
            if self.operacao == '^':
                resultado = self.valor_anterior ** atual
                self.valor_anterior = resultado
                self.valor_atual = self._formatar_resultado(resultado)
                self.atualizar_display()
        except:
            pass

    def on_igual(self, btn):
        if self.operacao is None:
            # Se não houver operação pendente, mas houver função unária aplicada
            return
            
        if self.valor_anterior is None:
            return
        
        try:
            atual = float(self.valor_atual)
            resultado = 0
            expr_str = ""
            
            if self.operacao == '+':
                resultado = self.valor_anterior + atual
                expr_str = f"{self._format_num(self.valor_anterior)} + {self._format_num(atual)}"
            elif self.operacao == '-':
                resultado = self.valor_anterior - atual
                expr_str = f"{self._format_num(self.valor_anterior)} - {self._format_num(atual)}"
            elif self.operacao == '×':
                resultado = self.valor_anterior * atual
                expr_str = f"{self._format_num(self.valor_anterior)} × {self._format_num(atual)}"
            elif self.operacao == '÷':
                if atual == 0:
                    self._erro()
                    return
                resultado = self.valor_anterior / atual
                expr_str = f"{self._format_num(self.valor_anterior)} ÷ {self._format_num(atual)}"
            elif self.operacao == '^':
                resultado = self.valor_anterior ** atual
                expr_str = f"{self._format_num(self.valor_anterior)} ^ {self._format_num(atual)}"
            
            res_str = self._formatar_resultado(resultado)
            
            # Adiciona ao histórico
            self.adicionar_ao_historico(expr_str, res_str)
            
            self.valor_atual = res_str
            self.operacao = None
            self.valor_anterior = None
            self.novo_numero = True
            self.atualizar_display()
            
        except Exception as e:
            self._erro()

    def on_key_pressed(self, controller, keyval, keycode, state):
        key = Gdk.keyval_name(keyval)
        
        if key in '0123456789':
            self.on_numero(key)
            return True
        elif key == 'period' or key == 'comma':
            self.on_decimal(None)
            return True
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
        elif key == 'asciicircum':
            self.on_operator('^')
            return True
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
        super().__init__(application_id='com.exemplo.calculadora.historico')
    
    def do_activate(self):
        win = CalculadoraWindow(application=self)
        win.present()

def main():
    app = CalculadoraApp()
    app.run(None)

if __name__ == '__main__':
    main()