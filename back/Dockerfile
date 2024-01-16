# Dockerfile para aplicação Flask (Python 3.11.3)

# Utiliza o Alpine Linux como imagem base
FROM python:3.11.3-alpine

# Define o diretório de trabalho no container
WORKDIR /app

# Copia o arquivo de dependências para o diretório de trabalho
COPY requirements.txt .

# Instala os pacotes necessários especificados no requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia o conteúdo do diretório local src para o diretório de trabalho
COPY / .

# Expõe a porta 5000
EXPOSE 5000

# Comando para executar a aplicação
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
# CMD ["python", "app.py"]