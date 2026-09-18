# Projeto Notes Manager em Python
### Aplicação web desenvolvida em Python para autenticação e gerenciamento de anotações.
[Acessar Projeto](https://aleussandro.github.io/login_page_01/)

Aplicação web para gerenciamento de anotações, desenvolvida em Python, com autenticação de usuários, controle de acesso por JWT e operações CRUD integradas a banco de dados MySQL.

O projeto começou como uma página de login e foi posteriormente evoluído para uma aplicação de gerenciamento de anotações, incluindo autenticação, API, persistência de dados e testes automatizados

## Funcionalidades

### Autenticação
* Cadastro de novos usuários
* Armazenamento de senhas utilizando hash
* Login com validação de senha e usuário
* Geração de token JWT após autenticação
* Expiração do token após 1 hora
* Proteção de rotas que exigem autenticação

### Gerenciamento de anotações
* Criação de novas anotações
* Listagem de anotações do usuário autenticado
* Atualização de anotações
* Exclusão de anotações
* Controle de acesso para garantir que usuários alterem apenas as próprias anotações

## Tecnologias
* Python
* Flask
* Flask-CORS
* MySQL
* mysql-connector-python
* PyJWT
* python-dotenv
* gunicorn
* Werkzeug
* Pytest

## Banco de Dados
A aplicação utiliza um banco de dados compatível com MySQL.

O projeto foi migrado para o TiDB Cloud, utilizando conexão segura por SSL.

As credenciais e informações sensíveis de conexão são carregadas por meio de variáveis de ambiente, evitando deixar senhas diretamente expostas no código.

## Objetivo do Projeto
Este projeto foi desenvolvido como prática de desenvolvimento web utilizando Python, com foco em:
* Desenvolvimento de APIs
* Autenticação e autorização
* Manipulação de banco de dados
* Operações CRUD
* Integração entre cliente e servidor
* Testes automatizados
* Versionamento utilizando Git e GitHub

O projeto também representa a evolução de uma aplicação originalmente criada como uma página de login para uma aplicação web com gerenciamento de dados e autenticação.
