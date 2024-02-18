# Makefile para o projeto Metaverso Notepad

# Definição do alvo padrão
all: lint

# Formatação dos arquivos Python
autopep8:
	#find pasta -name "*.py" | xargs autopep8 --max-line-length 120 --in-place
	find . -name "app.py" | xargs autopep8 --max-line-length 120 --in-place

# Organização das importações nos arquivos Python
isort:
	isort -m 3 * --skip instance --skip venv

# Execução de todos os linters e formatações
lint: autopep8 isort
