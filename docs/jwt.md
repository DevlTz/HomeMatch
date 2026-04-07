# Authentication & Security Documentation

Esta documentação detalha a implementação do sistema de segurança e autenticação do projeto **HomeMatch**.

## Visão Geral
A plataforma utiliza **JSON Web Tokens (JWT)** via `djangorestframework-simplejwt` para gerenciar sessões e permissões. O diferencial do nosso modelo é a autenticação baseada exclusivamente em **E-mail**, tendo o campo `username` sido removido para simplificar o fluxo do usuário.

---

## Modelo de Usuário Customizado
O modelo `User` herda de `AbstractUser`, mas utiliza um `UserManager` customizado para suportar o e-mail como identificador único.

* **Identificador de Login**: `email`.
* **Campos Obrigatórios**: `email`, `name`.
* **Tipos de Usuário (user_type)**: 
    * `A` (Advertiser/Anunciante).
    * `S` (Seeker/Buscador).

---

## Endpoints de Autenticação (JWT)

| Método | Endpoint | Acesso | Descrição |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/users/register/` | Público | Registra um novo usuário na plataforma. |
| `POST` | `/api/users/login/` | Público | Recebe as credenciais e retorna os tokens `access` e `refresh`. |
| `POST` | `/api/users/token/refresh/` | Público | Gera um novo `access` token utilizando um `refresh` válido. |
| `POST` | `/api/users/logout/` | Autenticado | Invalida o `refresh` token (blacklist), encerrando a sessão. |
| `GET` | `/api/users/me/` | Autenticado | Retorna os dados do perfil do usuário logado. |

---

## Proteção de Rotas: Imóveis (Properties)

As rotas do app `properties` seguem a política de permissão `IsAuthenticatedOrReadOnly`.

### 1. Leitura de Dados (Público)
Qualquer usuário pode realizar as seguintes operações sem necessidade de token:
* `GET /api/properties/`: Lista todos os imóveis cadastrados.
* `GET /api/properties/{id}/`: Visualiza detalhes de um imóvel específico.

### 2. Escrita de Dados (Autenticado)
Requer o envio do cabeçalho `Authorization: Bearer <access_token>`.

* **Criação (`POST /api/properties/`)**: Permitida apenas para usuários com `user_type = 'A'` (Advertiser).
* **Edição (`PATCH /api/properties/{id}/`)**: Restrita ao proprietário do imóvel (`owner_id`).
* **Remoção (`DELETE /api/properties/{id}/`)**: Restrita ao proprietário do imóvel (`owner_id`).

---

## Tratamento de Erros

O sistema utiliza códigos de erro padronizados do Django REST Framework:

* **401 Unauthorized**: Token ausente, expirado ou inválido.
* **403 Forbidden**: Usuário autenticado tenta realizar uma ação sem permissão (ex: Seeker tentando postar imóvel ou editar imóvel de terceiros).
* **400 Bad Request**: Erros de validação (ex: e-mail já cadastrado ou senha fora do padrão).

---

## Exemplo de Requisição (CURL)

Para acessar rotas protegidas no terminal, utilize:

```bash
docker compose exec web python manage.py createsuperuser # Pra criar seu usuario - Se ainda não criado
```

```bash
curl -X POST http://localhost:8000/api/users/login/      -H "Content-Type: application/json"      -d '{
        "email": "seu email cadastrado",
        "password": "sua senha cadastrada"
     }'
```
 * Só ai, você testa com seu token.

```bash
curl -X GET http://localhost:8000/api/users/me/ \
         -H "Authorization: Bearer <SEU_ACCESS_TOKEN>" \
         -H "Content-Type: application/json"
```


