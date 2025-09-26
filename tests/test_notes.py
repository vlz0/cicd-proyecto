import pytest
from app import notes


def setup_function():
    # Reiniciar el almacenamiento entre tests
    notes._NOTES.clear()
    notes._NEXT_ID = 1


def test_add_note():
    note = notes.add_note("Título", "Contenido")
    assert note["id"] == 1
    assert note["title"] == "Título"
    assert note["content"] == "Contenido"
    assert notes.list_notes() == [note]


def test_list_notes_order():
    n1 = notes.add_note("Primera", "Contenido 1")
    n2 = notes.add_note("Segunda", "Contenido 2")
    lista = notes.list_notes()
    assert lista[0] == n2  # más reciente primero
    assert lista[1] == n1


def test_get_note_found():
    note = notes.add_note("Test", "Nota prueba")
    found = notes.get_note(note["id"])
    assert found == note


def test_get_note_not_found():
    assert notes.get_note(12345) is None


def test_delete_note():
    note = notes.add_note("A borrar", "Contenido")
    notes.delete_note(note["id"])
    assert notes.get_note(note["id"]) is None
    assert notes.list_notes() == []
