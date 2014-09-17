from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, text, UniqueConstraint, Unicode
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

import settings

DeclarativeBase = declarative_base()


def db_connect():
    """Performs database connection using database settings from settings.py.

    Returns sqlalchemy engine instance.

    """
    return create_engine(URL(**settings.DATABASE))


def create_deals_table(engine):
    """"""
    DeclarativeBase.metadata.create_all(engine)


class Body(DeclarativeBase):
    """SqlAlchemy pages model"""
    __tablename__ = "body"
    __table_args__ = (
        UniqueConstraint('body_name', name='_body_name_uc'),
        {'mysql_engine': 'MyISAM'}
    )

    id = Column(Integer, primary_key=True)
    page_url = Column('page_url', String(200), nullable=True)
    page_title = Column('page_title', Unicode(200))

    make = Column('make', Unicode(75), nullable=True)
    model = Column('model', Unicode(75), nullable=True)
    generation = Column('generation', Unicode(75), nullable=True)
    start = Column('start', String(10), nullable=True)
    end = Column('end', String(10), nullable=True)
    body_name = Column('body_name', Unicode(75), nullable=True)
    body_image = Column('body_image', String(250), nullable=True)

    status = Column(String(10), unique=False, nullable=True)

    created_at = Column('created_at', TIMESTAMP,
                        server_default=text('CURRENT_TIMESTAMP'))
