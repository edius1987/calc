<<<<<<< HEAD
# Calculadora Científica GTK4

**Projeto:** calc

**Descrição:**
Vou criar uma calculadora moderna com GTK4 usando UV como gerenciador de projetos. Para Ubuntu 24.04, você precisará primeiro instalar as dependências de sistema do GTK4.

## Instalação

### 1. Instalar dependências de sistema (Ubuntu 24.04)
```bash
sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-4.0 libgirepository1.0-dev gcc libcairo2-dev pkg-config
```

### 2. Instalar dependências de Pillow (processamento de imagens)
```bash
sudo apt install -y libjpeg-dev zlib1g-dev libpng-dev
```

### 3. Inicializar projeto com UV
```bash
uv init calc
```

### 4. Adicionar PyGObject (bindings GTK4)
```bash
uv add PyGObject
```

### 5. Adicionar bibliotecas Python ao projeto
```bash
uv add reportlab pillow
```

## Execução

### Usando UV
```bash
uv run main.py
```

### Ou ativar ambiente e rodar
```bash
source .venv/bin/activate
python main.py
```

## Licença
MIT License

---

**Autor:** Edius Ferreira
**Email:** edisuferreira@gmail.com
**GitHub:** https://github.com/edius1987
**Repositório do Projeto:** https://github.com/edius1987/calc.git
=======
# calc
Calculadora moderna com GTK4 usando UV como gerenciador de projetos.
>>>>>>> origin/main
