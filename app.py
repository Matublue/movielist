"""
Movie List Manager — Backend API

A small Flask API backed by SQLite. This replaces the in-browser
localStorage version with a real server + database, so the movie
list is available from any device, not just one browser.

Endpoints:
  GET    /api/movies              -> list all movies
  POST   /api/movies              -> add a movie   {title, genre, year}
  DELETE /api/movies/<id>         -> delete a movie by id
  GET    /api/movies/search?title=... -> search movies by title
  GET    /api/health              -> simple health check
"""

import os
import sqlite3
from flask import Flask, g, jsonify, request
from flask_cors import CORS

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "movies.db")

app = Flask(__name__)
CORS(app)  # allows the frontend (hosted on a different URL) to call this API


# ---------- Database helpers ----------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            genre TEXT NOT NULL,
            year TEXT NOT NULL
        )
        """
    )
    db.commit()
    db.close()


# ---------- Validation (mirrors the original add_movie() checks) ----------

def validate_movie(data):
    title = (data.get("title") or "").strip()
    genre = (data.get("genre") or "").strip()
    year = (data.get("year") or "").strip()

    errors = {}
    if not title:
        errors["title"] = "Title cannot be empty."
    if not genre:
        errors["genre"] = "Genre cannot be empty."
    if not year.isdigit():
        errors["year"] = "Please enter a valid numeric year (e.g., 2023)."

    return title, genre, year, errors


# ---------- Routes ----------

@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/movies")
def list_movies():
    db = get_db()
    rows = db.execute("SELECT id, title, genre, year FROM movies ORDER BY id").fetchall()
    return jsonify([dict(row) for row in rows])


@app.post("/api/movies")
def add_movie():
    data = request.get_json(silent=True) or {}
    title, genre, year, errors = validate_movie(data)
    if errors:
        return jsonify({"errors": errors}), 400

    db = get_db()
    cursor = db.execute(
        "INSERT INTO movies (title, genre, year) VALUES (?, ?, ?)",
        (title, genre, year),
    )
    db.commit()
    new_movie = {"id": cursor.lastrowid, "title": title, "genre": genre, "year": year}
    return jsonify(new_movie), 201


@app.delete("/api/movies/<int:movie_id>")
def delete_movie(movie_id):
    db = get_db()
    existing = db.execute("SELECT id FROM movies WHERE id = ?", (movie_id,)).fetchone()
    if existing is None:
        return jsonify({"error": "Movie not found."}), 404

    db.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    db.commit()
    return jsonify({"deleted": movie_id})


@app.get("/api/movies/search")
def search_movies():
    query = (request.args.get("title") or "").strip().lower()
    db = get_db()
    rows = db.execute("SELECT id, title, genre, year FROM movies ORDER BY id").fetchall()
    matches = [dict(row) for row in rows if row["title"].lower() == query]
    return jsonify(matches)


if __name__ == "__main__":
    init_db()
    # debug=True is fine for local development only — turn off in production
    app.run(host="0.0.0.0", port=5000, debug=True)
else:
    # also make sure the table exists when run under gunicorn (production)
    init_db()
