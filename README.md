# 💰 Simulador de Financiamento - Sistema Price

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flet](https://img.shields.io/badge/Flet-0.24+-purple.svg)](https://flet.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Uma aplicação desktop/web moderna para simulação de financiamentos com prestações fixas (Sistema Price), baseada na Calculadora do Cidadão do Banco Central do Brasil.

## 📋 Sobre o Projeto

Este simulador replica todas as funcionalidades da [Calculadora do Cidadão do BCB](https://www3.bcb.gov.br/CALCIDADAO), permitindo calcular qualquer uma das 4 variáveis de um financiamento:

- 📅 Número de meses (prazo)
- 📊 Taxa de juros mensal
- 💵 Valor da prestação
- 💰 Valor financiado

## ✨ Funcionalidades

### Cálculos Financeiros
- ✅ **Cálculo do prazo**: Descubra em quantos meses você quitará o financiamento
- ✅ **Cálculo da taxa de juros**: Identifique a taxa real cobrada no financiamento
- ✅ **Cálculo da prestação**: Saiba quanto pagará por mês
- ✅ **Cálculo do valor financiado**: Descubra o valor presente do financiamento

### Interface e Recursos
- 🎨 Interface moderna e intuitiva com Flet
- 📈 Tabela de amortização completa (mês a mês)
- 📱 Responsivo (funciona em desktop, web e mobile)
- 💡 Exemplos práticos inclusos
- ⚠️ Validação de dados e tratamento de erros
- 🧮 Cálculos precisos usando fórmulas matemáticas corretas

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**: Linguagem de programação
- **Flet**: Framework para criar aplicações multi-plataforma
- **Matemática Financeira**: Implementação do Sistema Price (Francês)

## 📦 Instalação

### Pré-requisitos

- Python 3.8 ou superior instalado
- pip (gerenciador de pacotes do Python)

### Passo a passo

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/simulador-financiamento.git
cd simulador-financiamento
```

2. **Crie um ambiente virtual (opcional, mas recomendado)**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install flet
```

4. **Execute o programa**
```bash
python simulador_financiamento.py
```

## 🚀 Como Usar

1. **Preencha 3 campos** com os valores conhecidos
2. **Deixe 1 campo em branco** (será calculado automaticamente)
3. **Clique em "Calcular"**
4. **Visualize o resultado** e a tabela de amortização

### Exemplo Prático

**Calcular o valor da prestação:**
- Valor financiado: `1290`
- Número de meses: `4`
- Taxa de juros mensal: `1.99`
- Prestação: *(deixe em branco)*

**Resultado:** R$ 337,46 por mês

## 📊 Fórmulas Matemáticas

### Sistema Price (Tabela Price)

O Sistema Price, também conhecido como Sistema Francês de Amortização, utiliza prestações fixas ao longo do período.

**Cálculo da Prestação (PMT):**
```
PMT = PV × [i × (1 + i)^n] / [(1 + i)^n - 1]
```

**Cálculo do Valor Presente (PV):**
```
PV = PMT × [(1 + i)^n - 1] / [i × (1 + i)^n]
```

**Cálculo do Número de Períodos (n):**
```
n = log[PMT / (PMT - PV × i)] / log(1 + i)
```

**Cálculo da Taxa de Juros (i):**
- Método de Newton-Raphson (método numérico iterativo)

Onde:
- `PMT` = Valor da prestação
- `PV` = Valor presente (valor financiado)
- `i` = Taxa de juros por período (decimal)
- `n` = Número de períodos

### Tabela de Amortização

Para cada período:
- **Juros** = Saldo Devedor × Taxa de Juros
- **Amortização** = Prestação - Juros
- **Saldo Devedor** = Saldo Anterior - Amortização

## 📚 Exemplos de Uso

### Exemplo 1: Calcular o prazo
```
Dados:
- Valor financiado: R$ 2.000,00
- Taxa de juros: 1% ao mês
- Prestação: R$ 261,50

Resultado: ~9 meses
```

### Exemplo 2: Calcular a taxa de juros
```
Dados:
- Valor financiado: R$ 750,00
- Número de meses: 10
- Prestação: R$ 86,00

Resultado: ~3% ao mês
```

### Exemplo 3: Calcular a prestação
```
Dados:
- Valor financiado: R$ 1.290,00
- Número de meses: 4
- Taxa de juros: 1,99% ao mês

Resultado: R$ 337,46
```

### Exemplo 4: Calcular o valor financiado
```
Dados:
- Número de meses: 24
- Taxa de juros: 1,99% ao mês
- Prestação: R$ 935,00

Resultado: R$ 17.500,00
```

## 🎯 Casos de Uso

- 🏠 **Financiamento imobiliário**: Calcule as prestações da casa própria
- 🚗 **Financiamento de veículos**: Simule a compra do seu carro
- 🛒 **Compras parceladas**: Descubra a taxa real do carnê
- 💳 **Empréstimos pessoais**: Compare ofertas de diferentes bancos
- 📊 **Educação financeira**: Aprenda sobre juros compostos na prática

## ⚠️ Observações Importantes

- A primeira prestação **não** é no ato da contratação
- O valor financiado **não inclui** o valor da entrada
- Os cálculos consideram o regime de **juros compostos**
- Valores são arredondados para 2 casas decimais

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer um Fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abrir um Pull Request

### Ideias de melhorias

- [ ] Exportar tabela de amortização para Excel/PDF
- [ ] Adicionar gráficos de evolução do saldo devedor
- [ ] Incluir outros sistemas de amortização (SAC, SAM)
- [ ] Adicionar cálculo com entrada/sinal
- [ ] Implementar simulação de portabilidade
- [ ] Adicionar comparador de financiamentos

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👨‍💻 Autor

Desenvolvido com 💙 usando Python e Flet

## 🔗 Links Úteis

- [Documentação do Flet](https://flet.dev/docs/)
- [Calculadora do Cidadão - BCB](https://www3.bcb.gov.br/CALCIDADAO)
- [Sistema Price - Wikipédia](https://pt.wikipedia.org/wiki/Tabela_Price)

## 📞 Suporte

Se você tiver alguma dúvida ou sugestão, sinta-se à vontade para abrir uma [issue](https://github.com/seu-usuario/simulador-financiamento/issues).

---

⭐ Se este projeto foi útil para você, considere dar uma estrela no GitHub!

**Aviso Legal:** Esta ferramenta é fornecida apenas para fins educacionais e informativos. Sempre consulte um profissional financeiro antes de tomar decisões de investimento ou financiamento.