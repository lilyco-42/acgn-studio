import io
import json
import threading
from urllib.parse import quote

import httpx
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, SQLModel, col, select

from core.database import engine
from core.models import Character
from core.paths import BASE_DIR
from core.prts import fetch_character, fetch_character_list
from core.prts.x_search import HEADERS, get_media_path, MEDIA_CDN
from core.search import search_character

app = FastAPI()

DOWNLOAD_DIR = BASE_DIR / "downloads"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_init_state = {"running": False, "done": False, "current": 0, "total": 0, "log": []}


def _init_list():
    """只拉干员列表，写入基础数据。"""
    SQLModel.metadata.create_all(engine)
    _init_state["running"] = True

    try:
        char_list = fetch_character_list()
        _init_state["total"] = len(char_list)
        _init_state["log"].append(f"获取到 {len(char_list)} 个干员")
    except Exception as e:
        _init_state["log"].append(f"获取干员列表失败: {e}")
        _init_state["running"] = False
        _init_state["done"] = True
        return

    with Session(engine) as session:
        for i, char_ref in enumerate(char_list):
            name = char_ref["name"]
            char_id = char_ref["id"]
            _init_state["current"] = i + 1

            exists = session.exec(
                select(Character).where(col(Character.name) == name)
            ).first()
            if exists:
                continue

            avatar_url = f"{MEDIA_CDN}/{get_media_path(f'头像_{name}.png')}"
            character = Character(
                name=name,
                char_id=char_id,
                avatar_url=avatar_url,
            )
            session.add(character)
            session.commit()

    _init_state["done"] = True
    _init_state["running"] = False


@app.on_event("startup")
def on_startup():
    threading.Thread(target=_init_list, daemon=True).start()


@app.get("/api/init-status")
def init_status():
    return _init_state


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


@app.get("/api/characters/{character_id}/detail")
def get_character_detail(character_id: int):
    """懒加载：如果详情为空则抓取并回写。"""
    with Session(engine) as session:
        character = session.get(Character, character_id)
        if not character:
            return {"error": "not found"}

        if not character.rarity:
            try:
                data = fetch_character(character.name)
                character.char_id = data["char_id"]
                character.rarity = data["rarity"]
                character.profession = data["profession"]
                character.faction = data["faction"]
                character.illustration_urls = data["illustration_urls"]
                character.voice_lines = data["voice_lines"]
                character.voice_urls = data["voice_urls"]
                session.add(character)
                session.commit()
                session.refresh(character)
            except Exception as e:
                return {"error": str(e)}

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
        "illustration_urls": json.loads(c.illustration_urls)
        if c.illustration_urls
        else {},
        "voice_lines": json.loads(c.voice_lines) if c.voice_lines else [],
        "voice_urls": json.loads(c.voice_urls) if c.voice_urls else {},
    }


@app.get("/api/open-folder")
def open_folder(path: str = Query(...)):
    import os

    os.startfile(path)
    return {"ok": True}


app.mount(
    "/", StaticFiles(directory=str(BASE_DIR / "frontend"), html=True), name="frontend"
)
