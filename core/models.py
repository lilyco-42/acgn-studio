from sqlmodel import Field, SQLModel


class Character(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    char_id: str = Field(default="", index=True)
    rarity: int = Field(default=0)
    profession: str = Field(default="")
    faction: str = Field(default="")
    avatar_url: str = Field(default="")
    illustration_urls: str = Field(default="{}")
    voice_lines: str = Field(default="[]")
    voice_urls: str = Field(default="{}")
