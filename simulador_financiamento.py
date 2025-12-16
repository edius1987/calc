import flet as ft
import math

class FinanciamentoCalculator:
    """Classe para cálculos de financiamento com prestações fixas (Sistema Price)"""
    
    @staticmethod
    def calcular_prestacao(valor_financiado, taxa_mensal, n_meses):
        """Calcula o valor da prestação"""
        if taxa_mensal == 0:
            return valor_financiado / n_meses
        
        i = taxa_mensal / 100
        pmt = valor_financiado * (i * (1 + i)**n_meses) / ((1 + i)**n_meses - 1)
        return pmt
    
    @staticmethod
    def calcular_valor_financiado(prestacao, taxa_mensal, n_meses):
        """Calcula o valor financiado"""
        if taxa_mensal == 0:
            return prestacao * n_meses
        
        i = taxa_mensal / 100
        pv = prestacao * ((1 + i)**n_meses - 1) / (i * (1 + i)**n_meses)
        return pv
    
    @staticmethod
    def calcular_n_meses(valor_financiado, taxa_mensal, prestacao):
        """Calcula o número de meses"""
        if taxa_mensal == 0:
            return valor_financiado / prestacao
        
        i = taxa_mensal / 100
        
        # Verifica se a prestação é suficiente para pagar os juros
        if prestacao <= valor_financiado * i:
            raise ValueError("Prestação insuficiente para pagar os juros")
        
        n = math.log(prestacao / (prestacao - valor_financiado * i)) / math.log(1 + i)
        return n
    
    @staticmethod
    def calcular_taxa_juros(valor_financiado, n_meses, prestacao):
        """Calcula a taxa de juros mensal usando método de Newton-Raphson"""
        
        # Função para calcular o erro
        def funcao(i):
            if abs(i) < 1e-10:
                return prestacao * n_meses - valor_financiado
            return valor_financiado * i * (1 + i)**n_meses / ((1 + i)**n_meses - 1) - prestacao
        
        # Derivada da função
        def derivada(i):
            if abs(i) < 1e-10:
                return 0
            num = (1 + i)**n_meses * (1 + i * n_meses) - 1
            den = ((1 + i)**n_meses - 1)**2
            return valor_financiado * num / den
        
        # Método de Newton-Raphson
        taxa = 0.01  # Chute inicial de 1%
        for _ in range(100):
            f = funcao(taxa)
            if abs(f) < 1e-10:
                break
            df = derivada(taxa)
            if abs(df) < 1e-10:
                break
            taxa = taxa - f / df
            
            # Garante que a taxa seja positiva
            if taxa < 0:
                taxa = 0.0001
        
        return taxa * 100  # Retorna em percentual

def main(page: ft.Page):
    page.title = "Calculadora de Financiamento - Sistema Price"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = "adaptive"
    
    # Campos de entrada
    campo_n_meses = ft.TextField(
        label="Nº de meses",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=300,
        suffix_text="meses"
    )
    
    campo_taxa = ft.TextField(
        label="Taxa de juros mensal",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=300,
        suffix_text="%"
    )
    
    campo_prestacao = ft.TextField(
        label="Valor da prestação",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=300,
        prefix_text="R$ "
    )
    
    campo_valor_financiado = ft.TextField(
        label="Valor financiado",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=300,
        prefix_text="R$ "
    )
    
    resultado_texto = ft.Text(
        size=18,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.GREEN_700
    )
    
    erro_texto = ft.Text(
        size=14,
        color=ft.Colors.RED_700
    )
    
    tabela_amortizacao = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Mês", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Prestação", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Juros", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Amortização", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Saldo Devedor", weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=10,
        horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_200),
    )
    
    container_tabela = ft.Container(
        content=ft.Column([
            ft.Text("Tabela de Amortização", size=20, weight=ft.FontWeight.BOLD),
            tabela_amortizacao
        ]),
        visible=False,
        padding=20,
        border=ft.border.all(1, ft.Colors.BLUE_200),
        border_radius=10,
        bgcolor=ft.Colors.BLUE_50
    )
    
    def gerar_tabela_amortizacao(vf, taxa, n):
        """Gera a tabela de amortização"""
        tabela_amortizacao.rows.clear()
        calc = FinanciamentoCalculator()
        prestacao = calc.calcular_prestacao(vf, taxa, n)
        i = taxa / 100
        saldo = vf
        
        for mes in range(1, int(n) + 1):
            juros = saldo * i
            amortizacao = prestacao - juros
            saldo -= amortizacao
            
            # Ajuste para o último mês (evitar saldo negativo por arredondamento)
            if mes == int(n):
                saldo = 0
            
            tabela_amortizacao.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(mes))),
                        ft.DataCell(ft.Text(f"R$ {prestacao:,.2f}")),
                        ft.DataCell(ft.Text(f"R$ {juros:,.2f}")),
                        ft.DataCell(ft.Text(f"R$ {amortizacao:,.2f}")),
                        ft.DataCell(ft.Text(f"R$ {max(0, saldo):,.2f}")),
                    ]
                )
            )
        
        container_tabela.visible = True
    
    def calcular(e):
        erro_texto.value = ""
        resultado_texto.value = ""
        container_tabela.visible = False
        
        try:
            calc = FinanciamentoCalculator()
            
            # Conta quantos campos estão preenchidos
            campos_preenchidos = 0
            if campo_n_meses.value: campos_preenchidos += 1
            if campo_taxa.value: campos_preenchidos += 1
            if campo_prestacao.value: campos_preenchidos += 1
            if campo_valor_financiado.value: campos_preenchidos += 1
            
            if campos_preenchidos != 3:
                erro_texto.value = "❌ Preencha exatamente 3 campos para calcular o 4º"
                page.update()
                return
            
            # Calcula o número de meses
            if not campo_n_meses.value:
                vf = float(campo_valor_financiado.value.replace(',', '.'))
                taxa = float(campo_taxa.value.replace(',', '.'))
                prest = float(campo_prestacao.value.replace(',', '.'))
                
                n = calc.calcular_n_meses(vf, taxa, prest)
                campo_n_meses.value = f"{n:.2f}"
                resultado_texto.value = f"✅ Número de meses: {n:.2f} meses"
                gerar_tabela_amortizacao(vf, taxa, n)
            
            # Calcula a taxa de juros
            elif not campo_taxa.value:
                vf = float(campo_valor_financiado.value.replace(',', '.'))
                n = float(campo_n_meses.value.replace(',', '.'))
                prest = float(campo_prestacao.value.replace(',', '.'))
                
                taxa = calc.calcular_taxa_juros(vf, n, prest)
                campo_taxa.value = f"{taxa:.4f}"
                resultado_texto.value = f"✅ Taxa de juros mensal: {taxa:.4f}%"
                gerar_tabela_amortizacao(vf, taxa, n)
            
            # Calcula a prestação
            elif not campo_prestacao.value:
                vf = float(campo_valor_financiado.value.replace(',', '.'))
                taxa = float(campo_taxa.value.replace(',', '.'))
                n = float(campo_n_meses.value.replace(',', '.'))
                
                prest = calc.calcular_prestacao(vf, taxa, n)
                campo_prestacao.value = f"{prest:.2f}"
                resultado_texto.value = f"✅ Valor da prestação: R$ {prest:,.2f}"
                gerar_tabela_amortizacao(vf, taxa, n)
            
            # Calcula o valor financiado
            elif not campo_valor_financiado.value:
                prest = float(campo_prestacao.value.replace(',', '.'))
                taxa = float(campo_taxa.value.replace(',', '.'))
                n = float(campo_n_meses.value.replace(',', '.'))
                
                vf = calc.calcular_valor_financiado(prest, taxa, n)
                campo_valor_financiado.value = f"{vf:.2f}"
                resultado_texto.value = f"✅ Valor financiado: R$ {vf:,.2f}"
                gerar_tabela_amortizacao(vf, taxa, n)
            
        except ValueError as ve:
            erro_texto.value = f"❌ Erro: {str(ve)}"
        except Exception as ex:
            erro_texto.value = f"❌ Erro no cálculo: {str(ex)}"
        
        page.update()
    
    def limpar(e):
        campo_n_meses.value = ""
        campo_taxa.value = ""
        campo_prestacao.value = ""
        campo_valor_financiado.value = ""
        resultado_texto.value = ""
        erro_texto.value = ""
        container_tabela.visible = False
        page.update()
    
    # Exemplos
    exemplos = ft.Container(
        content=ft.Column([
            ft.Text("Exemplos de Cálculo", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            ft.ExpansionTile(
                title=ft.Text("1. Calcular número de meses"),
                subtitle=ft.Text("Dívida de R$ 2000, juros 1% a.m., prestações de R$ 261,50"),
                controls=[
                    ft.Text("• Valor financiado: R$ 2000,00", size=14),
                    ft.Text("• Taxa de juros: 1%", size=14),
                    ft.Text("• Prestação: R$ 261,50", size=14),
                    ft.Text("• Resultado: ~9 meses", weight=ft.FontWeight.BOLD),
                ],
            ),
            
            ft.ExpansionTile(
                title=ft.Text("2. Calcular taxa de juros"),
                subtitle=ft.Text("Bem de R$ 750, 10 parcelas de R$ 86"),
                controls=[
                    ft.Text("• Valor financiado: R$ 750,00", size=14),
                    ft.Text("• Número de meses: 10", size=14),
                    ft.Text("• Prestação: R$ 86,00", size=14),
                    ft.Text("• Resultado: ~3% a.m.", weight=ft.FontWeight.BOLD),
                ],
            ),
            
            ft.ExpansionTile(
                title=ft.Text("3. Calcular valor da prestação"),
                subtitle=ft.Text("Bem de R$ 1290, 4 parcelas, juros 1,99% a.m."),
                controls=[
                    ft.Text("• Valor financiado: R$ 1290,00", size=14),
                    ft.Text("• Número de meses: 4", size=14),
                    ft.Text("• Taxa de juros: 1,99%", size=14),
                    ft.Text("• Resultado: ~R$ 337,46", weight=ft.FontWeight.BOLD),
                ],
            ),
            
            ft.ExpansionTile(
                title=ft.Text("4. Calcular valor financiado"),
                subtitle=ft.Text("24 parcelas de R$ 935, juros 1,99% a.m."),
                controls=[
                    ft.Text("• Número de meses: 24", size=14),
                    ft.Text("• Taxa de juros: 1,99%", size=14),
                    ft.Text("• Prestação: R$ 935,00", size=14),
                    ft.Text("• Resultado: ~R$ 17.500", weight=ft.FontWeight.BOLD),
                ],
            ),
        ]),
        padding=20,
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=10,
        bgcolor=ft.Colors.GREY_50
    )
    
    # Layout da página
    page.add(
        ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        "💰 Calculadora de Financiamento",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_700
                    ),
                    ft.Text(
                        "Sistema Price - Prestações Fixas",
                        size=16,
                        color=ft.Colors.GREY_700
                    ),
                ]),
                padding=20,
                bgcolor=ft.Colors.BLUE_50,
                border_radius=10
            ),
            
            ft.Divider(height=20, color="transparent"),
            
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Simule o financiamento com prestações fixas",
                        size=18,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Text(
                        "Preencha 3 campos e deixe 1 em branco para calcular",
                        size=14,
                        color=ft.Colors.GREY_700,
                        italic=True
                    ),
                    ft.Divider(),
                    campo_n_meses,
                    campo_taxa,
                    campo_prestacao,
                    campo_valor_financiado,
                    
                    ft.Row([
                        ft.ElevatedButton(
                            "Calcular",
                            on_click=calcular,
                            icon=ft.Icons.CALCULATE,
                            bgcolor=ft.Colors.BLUE_700,
                            color=ft.Colors.WHITE,
                            width=150,
                            height=50
                        ),
                        ft.OutlinedButton(
                            "Limpar",
                            on_click=limpar,
                            icon=ft.Icons.CLEAR,
                            width=150,
                            height=50
                        ),
                    ], spacing=10),
                    
                    resultado_texto,
                    erro_texto,
                ]),
                padding=20,
                border=ft.border.all(2, ft.Colors.BLUE_700),
                border_radius=10
            ),
            
            ft.Divider(height=20, color="transparent"),
            
            container_tabela,
            
            ft.Divider(height=20, color="transparent"),
            
            exemplos,
            
            ft.Divider(height=20, color="transparent"),
            
            ft.Container(
                content=ft.Text(
                    "📝 Nota: A 1ª prestação não é no ato. O valor financiado não inclui entrada.",
                    size=12,
                    color=ft.Colors.GREY_600,
                    italic=True,
                    text_align=ft.TextAlign.CENTER
                ),
                padding=10
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO
        )
    )

ft.app(target=main)