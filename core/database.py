from sqlmodel import create_engine

from .paths import BASE_DIR

engine = create_engine(f"sqlite:///{BASE_DIR / 'data' / 'app.db'}")
