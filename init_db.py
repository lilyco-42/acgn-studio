import time

from sqlmodel import Session, SQLModel, col, select

from core.database import engine
from core.models import Character
from core.prts import fetch_character, fetch_character_list

SQLModel.metadata.create_all(engine)


def init_characters():
    char_list = fetch_character_list()
    print(f"获取到 {len(char_list)} 个干员")

    with Session(engine) as session:
        for i, char_ref in enumerate(char_list):
            name = char_ref["name"]
            exists = session.exec(
                select(Character).where(col(Character.name) == name)
            ).first()
            if exists:
                print(f"[{i + 1}/{len(char_list)}] {name} 已存在，跳过")
                continue

            try:
                data = fetch_character(name)
                character = Character(**data)
                session.add(character)
                session.commit()
                print(f"[{i + 1}/{len(char_list)}] {name} 写入成功")
            except Exception as e:
                print(f"[{i + 1}/{len(char_list)}] {name} 失败: {e}")

            time.sleep(1)


if __name__ == "__main__":
    init_characters()
