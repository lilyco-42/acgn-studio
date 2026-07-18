import hashlib
import json
import re
import urllib.parse

import httpx
import mwparserfromhell

PRTS_API = "https://prts.wiki/api.php"
CHAR_LIST_JS = "https://static.prts.wiki/charinfo/charId20260604.js"
CHAR_VOICE_JS = "https://static.prts.wiki/charinfo/charVoice20260604.js"
MEDIA_CDN = "https://media.prts.wiki"
AUDIO_CDN = "https://torappu.prts.wiki/assets/audio"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://prts.wiki/",
}


def get_media_path(filename: str) -> str:
    filename = filename.replace(" ", "_")
    md5 = hashlib.md5(filename.encode("utf-8")).hexdigest()
    return f"{md5[0]}/{md5[0:2]}/{urllib.parse.quote(filename)}"


def get_illustration_urls(name: str, skin_count: int = 0) -> dict[str, str]:
    urls = {}
    urls["elite0"] = f"{MEDIA_CDN}/{get_media_path(f'立绘_{name}_1.png')}"
    urls["elite2"] = f"{MEDIA_CDN}/{get_media_path(f'立绘_{name}_2.png')}"
    for i in range(1, skin_count + 1):
        urls[f"skin{i}"] = f"{MEDIA_CDN}/{get_media_path(f'立绘_{name}_skin{i}.png')}"
    return urls


def get_voice_url(char_id: str, voice_key: str, lang: str = "cn") -> str:
    lang_dir = {"cn": "voice_cn", "jp": "voice", "en": "voice_en", "kr": "voice_kr"}
    directory = lang_dir.get(lang, "voice_cn")
    return f"{AUDIO_CDN}/{directory}/{char_id}/{voice_key}.mp3"


def fetch_character_list() -> list[dict[str, str]]:
    resp = httpx.get(CHAR_LIST_JS, headers=HEADERS, timeout=30)
    text = resp.text
    start = text.find("[")
    end = text.rfind("]") + 1
    if start < 0 or end <= start:
        return []
    return json.loads(text[start:end])


def fetch_character(name: str) -> dict:
    resp = httpx.get(
        PRTS_API,
        params={"action": "parse", "page": name, "prop": "wikitext", "format": "json"},
        headers=HEADERS,
        timeout=30,
    )
    data = resp.json()
    wikitext = data["parse"]["wikitext"]["*"]
    return parse_character_wikitext(wikitext, name)


def parse_character_wikitext(wikitext: str, name: str) -> dict:
    code = mwparserfromhell.parse(wikitext)
    char_data = {"name": name}

    for template in code.filter_templates():
        tpl_name = template.name.strip()
        if tpl_name.startswith("CharinfoV2"):
            for param in template.params:
                key = param.name.strip()
                val = param.value.strip()
                char_data[key] = val

    char_id = char_data.get("干员id", "")
    rarity = int(char_data.get("稀有度", "0"))
    faction = char_data.get("所属国家", "")
    profession = char_data.get("职业", "")
    skin_count = 0
    for k in char_data:
        if k.startswith("时装") and k.endswith("名称"):
            num = k[1:-2]
            try:
                skin_count = max(skin_count, int(num))
            except ValueError:
                pass

    illustration_urls = get_illustration_urls(name, skin_count)

    avatar_url = f"{MEDIA_CDN}/{get_media_path(f'头像_{name}.png')}"

    voice_lines = fetch_voice_lines(name, char_id)

    return {
        "name": name,
        "char_id": char_id,
        "rarity": rarity,
        "profession": profession,
        "faction": faction,
        "avatar_url": avatar_url,
        "illustration_urls": json.dumps(illustration_urls, ensure_ascii=False),
        "voice_lines": json.dumps(voice_lines.get("cn", []), ensure_ascii=False),
        "voice_urls": json.dumps(
            {k: get_voice_url(char_id, k) for k in voice_lines.get("cn_keys", [])},
            ensure_ascii=False,
        ),
    }


def fetch_voice_lines(name: str, char_id: str) -> dict:
    try:
        resp = httpx.get(
            PRTS_API,
            params={
                "action": "parse",
                "page": f"{name}/语音记录",
                "prop": "wikitext",
                "format": "json",
            },
            headers=HEADERS,
            timeout=30,
        )
        data = resp.json()
        wikitext = data["parse"]["wikitext"]["*"]
    except Exception:
        return {"cn": [], "cn_keys": []}

    lines = []
    cn_keys = []

    title_pattern = re.compile(r"\|标题(\d+)=(.+)")
    voice_pattern = re.compile(r"\|语音(\d+)=(.+)")

    titles = {}
    for m in title_pattern.finditer(wikitext):
        titles[m.group(1)] = m.group(2).strip()

    for m in voice_pattern.finditer(wikitext):
        idx = m.group(1)
        voice_file = m.group(2).strip()
        title = titles.get(idx, "")

        cn_keys.append(voice_file.replace(".wav", "").lower())

        text_match = re.search(
            r"\|台词" + idx + r"=.*?\{\{VoiceData/word\|中文\|(.+?)\}\}", wikitext
        )
        text = text_match.group(1) if text_match else ""

        lines.append({"title": title, "text": text, "file": voice_file})

    return {"cn": lines, "cn_keys": cn_keys}
