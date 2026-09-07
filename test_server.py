import pytest
from server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login_sem_credenciais(client):
    # SIMULA UM TESTE COM CREDENCIAIS VAZIAS
    response = client.post('api/login', json={})

    # RESULTADO ESPERADO
    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing credentials"}

def teste_login_usuario_invalido(client):
    # SIMULA TESTE COM USUÁRIO/SENHA INVÁLIDO
    payload = {
        "username": "zxiocj032je42ne",
        "password": "20913jdkajczkjc"
    }
    response = client.post('api/login', json=payload)

    # RESULTADO ESPERADO
    assert response.status_code == 401
    assert "Senha ou usuário inválido" in response.get_json()["error"]

def teste_login_sem_token(client):
    # SIMULA UM USUARIO TENTANDO LER AS NOTAS SEM TER FEITO LOGIN
    response = client.get('api/notes')

    # RESULTADO ESPERADO
    assert response.status_code == 401