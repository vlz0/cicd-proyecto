"""
Aplicación Flask para gestionar notas.
"""

from flask import Flask, render_template, request, redirect, url_for
from .notes import add_note, list_notes, get_note, delete_note


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Página principal: lista notas y permite crear una nueva.
    """
    if request.method == "POST":
        titulo = (request.form.get("titulo") or "").strip()
        contenido = (request.form.get("contenido") or "").strip()
        if titulo and contenido:
            add_note(titulo, contenido)
        return redirect(url_for("index"))

    notas = list_notes()
    return render_template("index.html", notas=notas)


@app.route("/note/<int:note_id>")
def note_detail(note_id: int):
    """
    Muestra el detalle de una nota individual.
    """
    nota = get_note(note_id)
    if not nota:
        return "Nota no encontrada", 404
    return render_template("detail.html", nota=nota)


@app.post("/delete/<int:note_id>")
def delete(note_id: int):
    """
    Elimina una nota.
    """
    delete_note(note_id)
    return redirect(url_for("index"))


@app.route("/health")
def health():
    """
    Endpoint para pruebas de vida en CI/CD.
    """
    return "OK", 200


if __name__ == "__main__":  # pragma: no cover
    app.run(debug=False, port=5000, host="0.0.0.0")
