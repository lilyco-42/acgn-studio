from sqlmodel import Session, col, select

from .models import Character


def search_character(session: Session, keyword: str):

    statement = select(Character).where(col(Character.name).contains(keyword))

    return session.exec(statement).all()
