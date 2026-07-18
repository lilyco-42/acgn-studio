import json
import time
from pathlib import Path

import httpx

from core.prts.x_search import HEADERS, fetch_character, get_voice_url

OUTPUT_DIR = Path("training_data")


def export_character(name: str):
    print(f"抓取 {name} 的数据...")
    char_data = fetch_character(name)
    char_id = char_data["char_id"]
    voice_lines = json.loads(char_data["voice_lines"])

    char_dir = OUTPUT_DIR / name
    audio_dir = char_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    metadata = []
    for line in voice_lines:
        title = line["title"]
        text = line["text"]
        file_key = line["file"].replace(".wav", "").lower()

        if not text or not file_key:
            continue

        url = get_voice_url(char_id, file_key)
        filename = f"{file_key}.mp3"
        filepath = audio_dir / filename

        if not filepath.exists():
            print(f"  下载 {title}: {filename}")
            try:
                resp = httpx.get(
                    url, headers=HEADERS, timeout=30, follow_redirects=True
                )
                if resp.status_code == 200:
                    filepath.write_bytes(resp.content)
                else:
                    print(f"    HTTP {resp.status_code}, 跳过")
                    continue
            except Exception as e:
                print(f"    失败: {e}")
                continue
            time.sleep(0.3)
        else:
            print(f"  已存在 {filename}")

        metadata.append(
            {
                "path": f"audio/{filename}",
                "text": text,
                "language": "zh",
                "speaker": name,
                "title": title,
            }
        )

    meta_path = char_dir / "metadata.jsonl"
    with open(meta_path, "w", encoding="utf-8") as f:
        for item in metadata:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"\n完成: {name}")
    print(f"  音频文件: {audio_dir}")
    print(f"  元数据: {meta_path}")
    print(f"  总计: {len(metadata)} 条语音")
    return metadata


if __name__ == "__main__":
    export_character("凯尔希")
