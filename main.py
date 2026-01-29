import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib, Gio, GdkPixbuf, cairo
import math
from datetime import datetime
import csv
import io
from pathlib import Path

# Para PDF e PNG precisaremos instalar: uv add reportlab pillow

class HistoricoItem:
    def __init__(self, expressao, resultado, timestamp=None):
        self.expressao = expressao
        self.resultado = resultado
        self.timestamp = timestamp or datetime.now()

class ExportadorHistorico:
    """Classe responsável por exportar o histórico em vários formatos"""
    
    @staticmethod
    def exportar_txt(historico, filepath):
        """Exporta para TXT"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("HISTÓRICO DA CALCULADORA\n")
            f.write("=" * 50 + "\n")
            f.write(f"Exportado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            
            for i, item in enumerate(historico, 1):
                f.write(f"{i}. [{item.timestamp.strftime('%H:%M:%S')}] ")
                f.write(f"{item.expressao} = {item.resultado}\n")
        
        return True
    
    @staticmethod
    def exportar_csv(historico, filepath):
        """Exporta para CSV"""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['#', 'Data/Hora', 'Expressão', 'Resultado'])
            
            for i, item in enumerate(historico, 1):
                writer.writerow([
                    i,
                    item.timestamp.strftime('%d/%m/%Y %H:%M:%S'),
                    item.expressao,
                    item.resultado
                ])
        
        return True
    
    @staticmethod
    def exportar_pdf(historico, filepath):
        """Exporta para PDF usando ReportLab"""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            
            # Título
            title = Paragraph("<b>Histórico da Calculadora</b>", styles['Heading1'])
            elements.append(title)
            
            # Data
            date_para = Paragraph(
                f"Exportado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 
                styles['Normal']
            )
            elements.append(date_para)
            elements.append(Spacer(1, 20))
            
            # Tabela
            data = [['#', 'Hora', 'Expressão', 'Resultado']]
            for i, item in enumerate(historico, 1):
                data.append([
                    str(i),
                    item.timestamp.strftime('%H:%M:%S'),
                    item.expressao,
                    item.resultado
                ])
            
            table = Table(data, colWidths=[30, 60, 200, 100])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Courier'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            
            elements.append(table)
            doc.build(elements)
            return True
            
        except ImportError:
            raise Exception("Biblioteca reportlab não instalada. Execute: uv add reportlab")
    
    @staticmethod
    def exportar_png(historico, filepath):
        """Exporta para PNG como imagem renderizada"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Dimensões
            width = 600
            line_height = 30
            header_height = 80
            padding = 20
            
            height = header_height + (len(historico) * line_height) + (padding * 2)
            height = max(height, 400)  # Altura mínima
            
            # Criar imagem
            img = Image.new('RGB', (width, height), color='#1e1e1e')
            draw = ImageDraw.Draw(img)
            
            # Fontes (usando fonte padrão se não encontrar)
            try:
                font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
                font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
                font_item = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
            except:
                font_title = ImageFont.load_default()
                font_header = ImageFont.load_default()
                font_item = ImageFont.load_default()
            
            # Título
            draw.text((padding, 20), "Histórico da Calculadora", fill='#ff9500', font=font_title)
            draw.text((padding, 50), f"Exportado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                     fill='#aaaaaa', font=font_header)
            
            # Linhas
            y = header_height
            for i, item in enumerate(historico, 1):
                text = f"{i}. [{item.timestamp.strftime('%H:%M:%S')}] {item.expressao} = {item.resultado}"
                draw.text((padding, y), text, fill='#ffffff', font=font_item)
                y += line_height
            
            img.save(filepath, 'PNG')
            return True
            
        except ImportError:
            raise Exception("Biblioteca Pillow não instalada. Execute: uv add pillow")

class HistoricoRow(Gtk.Box):
    """Widget customizado para cada item do histórico"""
    def __init__(self, item, parent_window):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.item = item
        self.parent_window = parent_window
        
        self.set_margin_top(6)
        self.set_margin_bottom(6)
        self.set_margin_start(12)
        self.set_margin_end(12)
        
        # Label da expressão
        self.label_expr = Gtk.Label()
        self.label_expr.set_text(item.expressao)
        self.label_expr.set_xalign(1.0)
        self.label_expr.add_css_class("historico-expr")
        
        # Label do resultado
        self.label_res = Gtk.Label()
        self.label_res.set_text(f"= {item.resultado}")
        self.label_res.set_xalign(1.0)
        self.label_res.add_css_class("historico-res")
        
        # Label do timestamp
        self.label_time = Gtk.Label()
        self.label_time.set_text(item.timestamp.strftime("%H:%M:%S"))
        self.label_time.set_xalign(1.0)
        self.label_time.add_css_class("historico-time")
        
        self.append(self.label_expr)
        self.append(self.label_res)
        self.append(self.label_time)
        
        # Gesture para detectar clique
        gesture = Gtk.GestureClick()
        gesture.connect("pressed", self.on_clicked)
        self.add_controller(gesture)
        
        self.add_css_class("historico-row")
    
    def on_clicked(self, gesture, n_press, x, y):
        self.parent_window.carregar_valor(self.item.resultado)

class CalculadoraWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Calculadora Científica")
        self.set_default_size(900, 700)
        
        self.historico_lista = []  # Lista de HistoricoItem
        
        self._setup_css()
        self._setup_header_bar()
        self._setup_content()
        self._setup_aceleradores()
        
    def _setup_css(self):
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
            .historico-time {
                font-size: 11px;
                color: #666;
                font-family: monospace;
            }
            .historico-vazio {
                color: #666;
                font-style: italic;
                padding: 20px;
            }
            button:hover {
                opacity: 0.9;
            }
            .header-btn {
                margin: 0 4px;
                padding: 8px 16px;
                background: #2c3e50;
                color: white;
                border-radius: 6px;
            }
            .menu-item {
                padding: 8px 16px;
            }
        """)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _setup_header_bar(self):
        """Configura a barra de cabeçalho com menu"""
        header = Gtk.HeaderBar()
        self.set_titlebar(header)
        
        # Menu button
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.add_css_class("header-btn")
        
        # Criar menu
        menu = Gio.Menu.new()
        
        # Submenu Histórico
        menu_historico = Gio.Menu.new()
        menu_historico.append("Visualizar Histórico", "win.toggle-historico")
        menu_historico.append("Limpar Histórico", "win.limpar-historico")
        menu_historico.append_section("Exportar", self._criar_menu_exportar())
        
        menu.append_submenu("📜 Histórico", menu_historico)
        menu.append("Sobre", "win.sobre")
        
        menu_button.set_menu_model(menu)
        header.pack_end(menu_button)
        
        # Toggle histórico button (atalho rápido)
        hist_btn = Gtk.Button(label="📜 Histórico")
        hist_btn.add_css_class("header-btn")
        hist_btn.connect("clicked", self.on_toggle_historico)
        header.pack_start(hist_btn)
        
        # Ações
        self._setup_acoes()

    def _criar_menu_exportar(self):
        """Cria submenu de exportação"""
        menu_export = Gio.Menu.new()
        menu_export.append("📄 Exportar como TXT", "win.export-txt")
        menu_export.append("📊 Exportar como CSV", "win.export-csv")
        menu_export.append("📑 Exportar como PDF", "win.export-pdf")
        menu_export.append("🖼️  Exportar como PNG", "win.export-png")
        return menu_export

    def _setup_acoes(self):
        """Configura ações da janela"""
        # Toggle histórico
        acao_toggle = Gio.SimpleAction.new("toggle-historico", None)
        acao_toggle.connect("activate", self.on_toggle_historico)
        self.add_action(acao_toggle)
        
        # Limpar histórico
        acao_limpar = Gio.SimpleAction.new("limpar-historico", None)
        acao_limpar.connect("activate", self.on_limpar_historico_action)
        self.add_action(acao_limpar)
        
        # Exportações
        acao_exp_txt = Gio.SimpleAction.new("export-txt", None)
        acao_exp_txt.connect("activate", lambda a, p: self.on_exportar("txt"))
        self.add_action(acao_exp_txt)
        
        acao_exp_csv = Gio.SimpleAction.new("export-csv", None)
        acao_exp_csv.connect("activate", lambda a, p: self.on_exportar("csv"))
        self.add_action(acao_exp_csv)
        
        acao_exp_pdf = Gio.SimpleAction.new("export-pdf", None)
        acao_exp_pdf.connect("activate", lambda a, p: self.on_exportar("pdf"))
        self.add_action(acao_exp_pdf)
        
        acao_exp_png = Gio.SimpleAction.new("export-png", None)
        acao_exp_png.connect("activate", lambda a, p: self.on_exportar("png"))
        self.add_action(acao_exp_png)
        
        # Sobre
        acao_sobre = Gio.SimpleAction.new("sobre", None)
        acao_sobre.connect("activate", self.on_sobre)
        self.add_action(acao_sobre)

    def _setup_content(self):
        """Configura o conteúdo principal"""
        self.paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.set_child(self.paned)
        
        # Calculadora
        self.calc_box = self._criar_calculadora()
        self.paned.set_start_child(self.calc_box)
        self.paned.set_position(500)
        
        # Histórico (inicialmente visível)
        self.historico_box = self._criar_historico_panel()
        self.paned.set_end_child(self.historico_box)
        self.historico_visivel = True

    def _criar_calculadora(self):
        """Cria a calculadora"""
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        vbox.set_margin_top(20)
        vbox.set_margin_bottom(20)
        vbox.set_margin_start(20)
        vbox.set_margin_end(20)
        
        self.display_scientific = Gtk.Label()
        self.display_scientific.add_css_class("display-scientific")
        self.display_scientific.set_xalign(1.0)
        self.display_scientific.set_text("")
        vbox.append(self.display_scientific)
        
        self.display = Gtk.Entry()
        self.display.set_alignment(1.0)
        self.display.set_editable(False)
        self.display.add_css_class("display")
        self.display.set_text("0")
        vbox.append(self.display)
        
        grid = Gtk.Grid()
        grid.set_row_homogeneous(True)
        grid.set_column_homogeneous(True)
        grid.set_row_spacing(6)
        grid.set_column_spacing(6)
        vbox.append(grid)
        
        self.valor_atual = "0"
        self.valor_anterior = None
        self.operacao = None
        self.novo_numero = True
        
        botoes = [
            ('x²', 0, 0, 1, 'btn-scientific', self.on_quadrado),
            ('√x', 0, 1, 1, 'btn-scientific', self.on_raiz),
            ('log', 0, 2, 1, 'btn-scientific', self.on_log),
            ('ln', 0, 3, 1, 'btn-scientific', self.on_ln),
            
            ('x^y', 1, 0, 1, 'btn-scientific', lambda b: self.on_operator('^')),
            ('10ˣ', 1, 1, 1, 'btn-scientific', self.on_exp10),
            ('eˣ', 1, 2, 1, 'btn-scientific', self.on_exp),
            ('π', 1, 3, 1, 'btn-scientific', self.on_pi),
            
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
        """Cria o painel de histórico"""
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vbox.add_css_class("historico-container")
        vbox.set_size_request(300, -1)
        
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
        
        header_box.append(title)
        vbox.append(header_box)
        
        # Lista
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        self.historico_listbox = Gtk.ListBox()
        self.historico_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        
        self.placeholder = Gtk.Label()
        self.placeholder.set_text("Nenhuma operação realizada")
        self.placeholder.add_css_class("historico-vazio")
        self.historico_listbox.set_placeholder(self.placeholder)
        
        scroll.set_child(self.historico_listbox)
        vbox.append(scroll)
        
        return vbox

    def _setup_aceleradores(self):
        """Configura atalhos de teclado"""
        key_controller = Gtk.EventControllerKey()
        key_controller.connect('key-pressed', self.on_key_pressed)
        self.add_controller(key_controller)

    # ===== AÇÕES DO MENU =====
    
    def on_toggle_historico(self, action=None, param=None):
        """Mostra/esconde o painel de histórico e redimensiona a janela"""
        if self.historico_visivel:
            self.paned.set_end_child(None)
            self.historico_visivel = False
            # Reduz a largura da janela
            self.set_default_size(550, 700)
            self.set_size_request(550, 700)
        else:
            self.paned.set_end_child(self.historico_box)
            self.historico_visivel = True
            # Aumenta a largura da janela para mostrar o histórico
            self.set_default_size(900, 700)
            self.set_size_request(900, 700)

    def on_limpar_historico_action(self, action, param):
        """Limpa o histórico via menu"""
        self.limpar_historico()

    def on_exportar(self, formato):
        """Abre diálogo de exportação"""
        if not self.historico_lista:
            self._mostrar_erro("Histórico vazio", "Não há operações para exportar.")
            return
        
        dialog = Gtk.FileDialog()
        dialog.set_title(f"Exportar como {formato.upper()}")
        
        # Filtros
        filters = Gio.ListStore.new(Gtk.FileFilter)
        
        if formato == "txt":
            filter_txt = Gtk.FileFilter()
            filter_txt.set_name("Arquivo de texto")
            filter_txt.add_pattern("*.txt")
            filters.append(filter_txt)
            dialog.set_default_filter(filter_txt)
            nome_padrao = f"historico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
        elif formato == "csv":
            filter_csv = Gtk.FileFilter()
            filter_csv.set_name("CSV")
            filter_csv.add_pattern("*.csv")
            filters.append(filter_csv)
            dialog.set_default_filter(filter_csv)
            nome_padrao = f"historico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
        elif formato == "pdf":
            filter_pdf = Gtk.FileFilter()
            filter_pdf.set_name("PDF")
            filter_pdf.add_pattern("*.pdf")
            filters.append(filter_pdf)
            dialog.set_default_filter(filter_pdf)
            nome_padrao = f"historico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
        elif formato == "png":
            filter_png = Gtk.FileFilter()
            filter_png.set_name("PNG")
            filter_png.add_pattern("*.png")
            filters.append(filter_png)
            dialog.set_default_filter(filter_png)
            nome_padrao = f"historico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        dialog.set_filters(filters)
        dialog.set_initial_name(nome_padrao)
        
        dialog.save(self, None, self._on_exportar_resposta, formato)

    def _on_exportar_resposta(self, dialog, result, formato):
        """Callback do diálogo de exportação"""
        try:
            file = dialog.save_finish(result)
            if file:
                filepath = file.get_path()
                
                exportador = ExportadorHistorico()
                
                if formato == "txt":
                    exportador.exportar_txt(self.historico_lista, filepath)
                elif formato == "csv":
                    exportador.exportar_csv(self.historico_lista, filepath)
                elif formato == "pdf":
                    exportador.exportar_pdf(self.historico_lista, filepath)
                elif formato == "png":
                    exportador.exportar_png(self.historico_lista, filepath)
                
                self._mostrar_sucesso(f"Exportado com sucesso!", f"Arquivo salvo em:\n{filepath}")
                
        except Exception as e:
            self._mostrar_erro("Erro na exportação", str(e))

    def on_sobre(self, action, param):
        """Diálogo sobre"""
        dialog = Gtk.AlertDialog()
        dialog.set_message("🧮 Calculadora Científica GTK4")
        dialog.set_detail(
            "Uma calculadora científica moderna desenvolvida com Python e GTK4.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📋 Projeto: Calculadora Científica\n"
            "👤 Autor: Edius Ferreira\n"
            "📧 Email: edisuferreira@gmail.com\n"
            "🔗 GitHub: https://github.com/edius1987\n"
            "📦 Repositório: https://github.com/edius1987/calc.git\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "⌨️ Atalhos de Teclado:\n"
            "• Ctrl+H: Mostrar/Esconder histórico\n"
            "• Esc: Limpar tudo\n"
            "• Enter: Calcular resultado\n"
            "• Backspace: Apagar último dígito\n\n"
            "🛠️ Tecnologias: Python, GTK4, UV"
        )
        dialog.set_buttons(["OK"])
        dialog.set_modal(True)
        dialog.show(self)

    def _mostrar_erro(self, titulo, mensagem):
        """Mostra diálogo de erro"""
        dialog = Gtk.AlertDialog()
        dialog.set_message(f"❌ {titulo}")
        dialog.set_detail(mensagem)
        dialog.set_buttons(["OK"])
        dialog.set_modal(True)
        dialog.show(self)

    def _mostrar_sucesso(self, titulo, mensagem):
        """Mostra diálogo de sucesso"""
        dialog = Gtk.AlertDialog()
        dialog.set_message(f"✅ {titulo}")
        dialog.set_detail(mensagem)
        dialog.set_buttons(["OK"])
        dialog.set_modal(True)
        dialog.show(self)

    # ===== MÉTODOS DO HISTÓRICO =====

    def adicionar_ao_historico(self, expressao, resultado):
        """Adiciona operação ao histórico"""
        item = HistoricoItem(expressao, resultado)
        self.historico_lista.insert(0, item)
        
        row_widget = HistoricoRow(item, self)
        self.historico_listbox.prepend(row_widget)
        
        # Animação
        row_widget.set_opacity(0)
        GLib.timeout_add(50, lambda: row_widget.set_opacity(1) or False)

    def limpar_historico(self):
        """Limpa o histórico"""
        self.historico_lista.clear()
        while True:
            row = self.historico_listbox.get_first_child()
            if row is None:
                break
            self.historico_listbox.remove(row)

    def carregar_valor(self, valor):
        """Carrega valor do histórico"""
        self.valor_atual = str(valor)
        self.novo_numero = True
        self.atualizar_display()

    # ===== OPERAÇÕES DA CALCULADORA =====

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
        if self.operacao is None or self.valor_anterior is None:
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
        
        # Ctrl+H para toggle histórico
        if key == 'h' and state & Gdk.ModifierType.CONTROL_MASK:
            self.on_toggle_historico()
            return True
        
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