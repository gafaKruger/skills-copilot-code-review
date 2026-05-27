# API de Atividades da Mergington High School

Uma aplicação FastAPI super simples que permite aos alunos visualizar e se inscrever em atividades extracurriculares.

## Funcionalidades

- Visualizar todas as atividades extracurriculares disponíveis
- Inscrever-se em atividades
- Exibir anúncios ativos carregados do banco de dados
- Gerenciar anúncios (listar, criar, editar e excluir) para usuários autenticados

## Como começar

1. Instale as dependências:

   ```
   pip install fastapi uvicorn
   ```

2. Execute a aplicação:

   ```
   python app.py
   ```

3. Abra seu navegador e acesse:
   - Documentação da API: http://localhost:8000/docs
   - Documentação alternativa: http://localhost:8000/redoc

## Endpoints da API

| Método | Endpoint                                                          | Descrição                                                            |
| ------ | ----------------------------------------------------------------- | -------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Obtém todas as atividades com detalhes e número atual de participantes |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Inscreve-se em uma atividade                                         |
| GET    | `/announcements`                                                  | Lista anúncios ativos para exibição pública                          |
| GET    | `/announcements/manage?username=teacher`                          | Lista todos os anúncios (requer login)                              |
| POST   | `/announcements/manage?username=teacher`                          | Cria anúncio com `expires_at` obrigatório                            |
| PUT    | `/announcements/manage/{announcement_id}?username=teacher`        | Atualiza anúncio existente                                            |
| DELETE | `/announcements/manage/{announcement_id}?username=teacher`        | Exclui anúncio existente                                              |

## Modelo de Dados

A aplicação usa um modelo de dados simples com identificadores significativos:

1. **Atividades** - Usa o nome da atividade como identificador:
   - Descrição
   - Horário
   - Número máximo de participantes permitidos
   - Lista de e-mails dos alunos inscritos

2. **Alunos** - Usa o e-mail como identificador:
   - Nome
   - Série

Os dados são armazenados no MongoDB (atividades, usuários e anúncios).
