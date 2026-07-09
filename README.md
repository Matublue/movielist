# Movie List Manager — Backend + Database

A Flask API backed by SQLite. This replaces the browser-only version —
your movie list now lives on a server, so it's the same list no matter
which device or browser you open the site from.

## Files

- `app.py` — the API server (Flask + SQLite)
- `requirements.txt` — Python packages it needs
- `movies.db` — created automatically the first time you run it
- `movie_list.html` — the website, already wired up to call this API

## 1. Run it on your own computer first

```bash
# from inside the movie-backend folder
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

You should see `Running on http://127.0.0.1:5000`. Leave that terminal open —
that's your server running.

Now open `movie_list.html` in your browser (just double-click it, or drag it
into a browser tab). It's already set to talk to `http://127.0.0.1:5000/api`,
so it should load, and adding/deleting/searching movies will hit your local
server and save to `movies.db`.

## 2. Put the backend on the internet (so it's not just on your laptop)

Your laptop being the server only works while your laptop is on and the
`python app.py` terminal is open. To make it permanently available, deploy
it to a free hosting service. **Render** is the simplest for Flask apps:

1. Push this `movie-backend` folder to a GitHub repository (same process
   as before — new repo, upload files, commit)
2. Go to **https://render.com** and sign up (free, can use GitHub login)
3. Click **New +** → **Web Service**
4. Connect your GitHub repo
5. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
6. Click **Create Web Service**

Render will give you a live URL like `https://your-app.onrender.com`.

**Then update the frontend:** open `movie_list.html`, find this line near
the top of the `<script>` section:

```js
const API_BASE = 'http://127.0.0.1:5000/api';
```

change it to:

```js
const API_BASE = 'https://your-app.onrender.com/api';
```

Re-upload `movie_list.html` to your GitHub Pages / Netlify site, and your
live website will now talk to your live backend.

## Important limitation: the free database will reset

Render's **free tier** does not keep files (like `movies.db`) permanently —
the disk resets whenever the service restarts or redeploys (this can happen
after periods of inactivity on the free plan). Your app will keep working,
but the movie list can occasionally go back to empty.

This is normal for free hosting and totally fine for learning and demos.
When you're ready for the data to be permanently reliable, the fix is to
use a real hosted database instead of a local SQLite file — for example:

- **Render's free PostgreSQL database** (separate from the free web service,
  works well together)
- **Railway** or **Supabase**, which both offer free hosted Postgres

That's a bigger step (swapping SQLite for PostgreSQL in `app.py`) — ask me
when you're ready and I'll walk through it.

## API reference

| Method | Endpoint                        | Does what                          |
|--------|----------------------------------|-------------------------------------|
| GET    | `/api/movies`                   | List all movies                    |
| POST   | `/api/movies`                   | Add a movie (`title`, `genre`, `year`) |
| DELETE | `/api/movies/<id>`              | Delete a movie by its id           |
| GET    | `/api/movies/search?title=...`  | Search by exact title match        |
