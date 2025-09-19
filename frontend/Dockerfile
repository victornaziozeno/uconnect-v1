FROM node:20

# Diretório de trabalho
WORKDIR /app

# Copiar e instalar dependências
COPY package*.json ./
RUN npm install

# Copiar código do frontend
COPY . .

# Build do projeto
RUN npm run build

# Usar servidor leve (serve) para rodar a build
RUN npm install -g serve
CMD ["serve", "-s", "build", "-l", "3000"]
