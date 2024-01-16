## Documentação do Código

### Arquivo: app.py
Este é o arquivo principal do aplicativo Flask. Ele define a aplicação Flask, configura o CORS, conecta ao banco de dados MongoDB, define as rotas da API e configura o SocketIO para comunicação em tempo real.

#### Funções importantes:
- `authenticated_only(f)`: Decorador que verifica se um usuário está autenticado antes de permitir o acesso a uma rota específica.
- `start_timer(room)`: Inicia um temporizador para iniciar um jogo em uma determinada sala.
- `start_game(room)`: Inicia um jogo em uma determinada sala.
- `@socketio.on("join_game")`: Manipulador de eventos para quando um usuário tenta entrar em um jogo.
- `@socketio.on("list_rooms")`: Manipulador de eventos para listar todas as salas disponíveis.
- `@socketio.on("send_message")`: Manipulador de eventos para enviar uma mensagem em uma sala específica.
- `@socketio.on("connect")` e `@socketio.on("disconnect")`: Manipuladores de eventos para lidar com a conexão e desconexão de um cliente.
- `@socketio.on("add_point")` e `@socketio.on("subtract_point")`: Manipuladores de eventos para adicionar ou subtrair pontos de um usuário.

### Arquivo: user_controller.py
Este arquivo contém as funções de controle para gerenciar usuários.

#### Funções importantes:
- `register_user(mongo, data)`: Registra um novo usuário no banco de dados.
- `get_user(mongo, user_id)`: Obtém informações sobre um usuário específico.
- `login_user(mongo)`: Autentica um usuário e retorna um token JWT.

### Arquivo: user_model.py
Este arquivo define a classe User, que representa um usuário no sistema.

### Arquivo: user_routes.py
Este arquivo define as rotas da API para gerenciar usuários.

#### Rotas importantes:
- `/register`: Rota POST para registrar um novo usuário.
- `/user/<user_id>`: Rota GET para obter informações sobre um usuário específico.
- `/login`: Rota POST para autenticar um usuário.

Agora, vamos passar para a documentação dos endpoints da API.

## Endpoints da API

### Endpoint: /register
**Método:** POST

**Descrição:** Este endpoint é usado para registrar um novo usuário. Ele espera um corpo de solicitação JSON com os campos 'nome', 'email' e 'password'. Se o registro for bem-sucedido, ele retornará uma resposta com uma mensagem de sucesso e um status HTTP 201. Se o email já estiver em uso, ele retornará uma resposta com uma mensagem de erro e um status HTTP 400.

**Exemplo de solicitação:**
```json
{
   "nome": "Nome do Usuário",
   "email": "usuario@example.com",
   "password": "senha"
}
```

**Exemplo de resposta de sucesso:**
```json
{
   "message": "Usuário registrado com sucesso"
}
```

**Exemplo de resposta de erro:**
```json
{
   "error": "Email já existe"
}
```

### Endpoint: /user/<user_id>
**Método:** GET

**Descrição:** Este endpoint é usado para obter informações sobre um usuário específico. Ele requer o ID do usuário como parte do URL. Se o usuário for encontrado, ele retornará uma resposta com os detalhes do usuário e um status HTTP 200. Se o usuário não for encontrado, ele retornará uma resposta com uma mensagem de erro e um status HTTP 404.

**Exemplo de resposta de sucesso:**
```json
{
   "_id": "ID do Usuário",
   "email": "usuario@example.com",
   "nome": "Nome do Usuário"
}
```

**Exemplo de resposta de erro:**
```json
{
   "error": "Usuário não encontrado"
}
```

### Endpoint: /login
**Método:** POST

**Descrição:** Este endpoint é usado para autenticar um usuário. Ele espera um corpo de solicitação JSON com os campos 'email' e 'password'. Se a autenticação for bem-sucedida, ele retornará uma resposta com um token JWT e um status HTTP 200. Se a autenticação falhar, ele retornará uma resposta com uma mensagem de erro e um status HTTP 401.

**Exemplo de solicitação:**
```json
{
   "email": "usuario@example.com",
   "password": "senha"
}
```

**Exemplo de resposta de sucesso:**
```json
{
   "token": "Token JWT"
}
```

**Exemplo de resposta de erro:**
```json
{
   "error": "Credenciais inválidas"
}
```

## Rodar a aplicação com Docker Compose

Inicialmente renomeie o .env.example para .env dentro dele defina as variaveis de ambiente

Para levantar a aplicação completa com Docker Compose, você precisa seguir os seguintes passos:

1. Primeiro, certifique-se de que você tem o Docker e o Docker Compose instalados na sua máquina. Você pode verificar isso executando os seguintes comandos no terminal:

```bash
docker --version
docker-compose --version
```

Se ambos os comandos retornarem versões, então você tem o Docker e o Docker Compose instalados corretamente.

2. Navegue até o diretório onde o seu arquivo `docker-compose.yml` está localizado. Normalmente, este arquivo está na raiz do seu projeto. Você pode fazer isso com o comando `cd`, por exemplo:

```bash
cd /path/to/your/project
```

Substitua `/path/to/your/project` pelo caminho real para o diretório do seu projeto.

3. Agora você pode usar o comando `docker-compose up --build` para construir e iniciar todos os serviços definidos no seu arquivo `docker-compose.yml`. Este comando irá criar imagens Docker para cada serviço se elas ainda não existirem, e então iniciará os containers para esses serviços.

```bash
docker-compose up --build
```

Depois de executar este comando, você deve ver a saída do Docker Compose no terminal, mostrando o status de cada serviço à medida que eles são iniciados.

Lembre-se de que este comando irá iniciar todos os serviços definidos no seu arquivo `docker-compose.yml` em segundo plano. Se você quiser parar os serviços, você pode usar o comando `docker-compose down`.



Para navegar no front-end deste aplicativo, você pode seguir os seguintes passos:

1. Abra o navegador e digite a URL do aplicativo no campo de endereço. Por exemplo, se o aplicativo estiver sendo executado localmente, você pode digitar `http://localhost:5173/`.

2. Na página inicial, você verá links "Register" e "Login".

3. Clique no link "Register" para acessar a página de registro. Aqui, você pode preencher o formulário com suas informações pessoais e clicar no botão "Register" para criar uma nova conta.

4. Após o registro bem-sucedido, você será redirecionado para a página de login. Digite suas credenciais de login e clique no botão "Login" para acessar sua conta.

5. Após o login bem-sucedido, você será redirecionado para a página do dashboard.

6. Clique no link "Enter Game" na página.

7. Agora você pode acessar uma sala de jogo digitando seu nome e apertando Join Room.

8. Nessa sala você podera enviar mensagens para outros jogadores presentes, alem disso assim que dois player estiverem na sala inicia-se uma contagem de 10 segundos para o inicio do jogo, limitado até quatro jogadores.

9. No fim da partida sera enviado ao banco de dados as informaçoes da partida.