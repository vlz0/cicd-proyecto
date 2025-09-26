# test_app.py
import pytest
from app.app import app
from app import notes


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        # Resetear notas antes de cada test
        notes._NOTES.clear()
        notes._NEXT_ID = 1
        yield client


def test_index_get(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Gestor de Notas" in response.data


def test_index_post_crear_nota(client):
    response = client.post("/", data={"titulo": "Mi titulo", "contenido": "Mi contenido"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Mi titulo" in response.data
    assert b"Mi contenido" in response.data


def test_note_detail(client):
    nota = notes.add_note("Nota detalle", "Contenido detalle")
    response = client.get(f"/note/{nota['id']}")
    assert response.status_code == 200
    assert b"Nota detalle" in response.data
    assert b"Contenido detalle" in response.data


def test_note_detail_not_found(client):
    response = client.get("/note/999")
    assert response.status_code == 404
    assert b"Nota no encontrada" in response.data


def test_delete_note(client):
    nota = notes.add_note("Borrar", "Contenido")
    response = client.post(f"/delete/{nota['id']}", follow_redirects=True)
    assert response.status_code == 200
    assert b"Borrar" not in response.data


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert b"OK" in response.data
