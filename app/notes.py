"""
Módulo muy simple para gestionar notas en memoria.
Cada nota es un diccionario con: {"id": int, "title": str, "content": str}
"""

# Almacenamiento en memoria
_NOTES = []
_NEXT_ID = 1


def _get_next_id() -> int:
    """Devuelve un nuevo id incremental para la siguiente nota."""
    global _NEXT_ID
    nid = _NEXT_ID
    _NEXT_ID += 1
    return nid


def add_note(title: str, content: str) -> dict:
    """
    Crea una nota, limpia espacios y la guarda en memoria.
    Devuelve la nota creada.
    """
    note = {
        "id": _get_next_id(),
        "title": (title or "").strip(),
        "content": (content or "").strip(),
    }
    _NOTES.append(note)
    return note


def list_notes() -> list:
    """
    Devuelve todas las notas con la más reciente primero.
    Como siempre insertamos al final, basta con invertir la lista.
    """
    return list(reversed(_NOTES))


def get_note(note_id: int) -> dict | None:
    """Busca una nota por id. Si no existe, devuelve None."""
    for note in _NOTES:
        if note["id"] == note_id:
            return note
    return None


def delete_note(note_id: int) -> None:
    """
    Elimina la nota con el id indicado. Si no existe, no hace nada.
    (Se mantiene la firma que no devuelve valor.)
    """
    for i, note in enumerate(_NOTES):
        if note["id"] == note_id:
            del _NOTES[i]
            break
