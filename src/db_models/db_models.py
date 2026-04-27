# %%

from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import select, func

class Base(DeclarativeBase):
    pass

class Match(Base):
    __tablename__ = "match"

    match_id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    duration: Mapped[int]
    start_time: Mapped[int]
    radiant_team_id: Mapped[int] = mapped_column(nullable=True)
    radiant_name: Mapped[str] = mapped_column(nullable=True) 
    dire_team_id: Mapped[int] = mapped_column(nullable=True)
    dire_name: Mapped[str] = mapped_column(nullable=True)
    leagueid: Mapped[int] = mapped_column(nullable=True)
    league_name: Mapped[str] = mapped_column(nullable=True)
    series_id: Mapped[int] = mapped_column(nullable=True)
    series_type: Mapped[int] = mapped_column(nullable=True)
    radiant_score: Mapped[int]
    dire_score: Mapped[int]
    radiant_win: Mapped[bool]
    version: Mapped[int] = mapped_column(nullable=True)
    flag_details_collected: Mapped[bool] = mapped_column(default=False)
    flag_details_processed: Mapped[bool] = mapped_column(default=False)


class League(Base):
    __tablename__ = "league"

    leagueid: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    ticket: Mapped[str] = mapped_column(nullable=True)
    banner: Mapped[str] = mapped_column(nullable=True)
    tier: Mapped[str] = mapped_column(nullable=True)
    name: Mapped[str]


def get_oldest_match_id(engine):
    with Session(engine) as session:
        stmt = select(func.min(Match.match_id))
        match_id = session.scalar(statement=stmt)
    return match_id