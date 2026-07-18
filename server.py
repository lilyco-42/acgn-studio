import io
import json
from urllib.parse import quote

import httpx
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

from core.database import engine
from core.models import Character
from core.paths import BASE_DIR
from core.prts.x_search import HEADERS
from core.search import search_character

app = FastAPI()

DOWNLOAD_DIR = BASE_DIR / "downloads"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/search")
def search(q: str = ""):
    with Session(engine) as session:
        if q:
            result = search_character(session, q)
        else:
            result = session.exec(select(Character)).all()
        return [_character_to_dict(c) for c in result]


@app.get("/api/characters")
def list_characters():
    with Session(engine) as session:
        result = session.exec(select(Character)).all()
        return [_character_to_dict(c) for c in result]


@app.get("/api/characters/{character_id}")
def get_character(character_id: int):
    with Session(engine) as session:
        character = session.get(Character, character_id)
        if not character:
            return {"error": "not found"}
        return _character_to_dict(character)


@app.get("/api/download")
def download_file(url: str = Query(...), filename: str = Query(...)):
    resp = httpx.get(url, headers=HEADERS, timeout=60, follow_redirects=True)
    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}"}

    encoded_name = quote(filename)
    content_disposition = f"attachment; filename*=UTF-8''{encoded_name}"

    return StreamingResponse(
        io.BytesIO(resp.content),
        media_type="application/octet-stream",
        headers={"Content-Disposition": content_disposition},
    )


@app.get("/api/download/batch")
def download_batch(urls: str = Query(...), character: str = Query(...)):
    url_list = json.loads(urls)
    char_dir = DOWNLOAD_DIR / character
    char_dir.mkdir(parents=True, exist_ok=True)

    saved = []
    for item in url_list:
        url = item["url"]
        name = item["filename"]
        filepath = char_dir / name
        if filepath.exists():
            saved.append(str(filepath))
            continue
        resp = httpx.get(url, headers=HEADERS, timeout=60, follow_redirects=True)
        if resp.status_code == 200:
            filepath.write_bytes(resp.content)
            saved.append(str(filepath))

    return {"dir": str(char_dir), "files": saved}


def _character_to_dict(c: Character) -> dict:
    return {
        "id": c.id,
        "name": c.name,
        "char_id": c.char_id,
        "rarity": c.rarity,
        "profession": c.profession,
        "faction": c.faction,
        "avatar_url": c.avatar_url,
        "illustration_urls": json.loads(c.illustration_urls),
        "voice_lines": json.loads(c.voice_lines),
        "voice_urls": json.loads(c.voice_urls),
    }


app.mount(
    "/", StaticFiles(directory=str(BASE_DIR / "frontend"), html=True), name="frontend"
)
