import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from orm import DataClasses as dc
from main import Discord
from tickets_manager.orm.data_cls import TypeAction

DATABASE_URL = os.getenv("DATABASE_URL")


def main_():
    engine = create_engine(DATABASE_URL)
    factory = sessionmaker(bind=engine)
    session = factory()

    b = dc.Actions(
        type=TypeAction.open_ticket.value,
        guid_ticket=None,
        author=None,
        data='{"status":"не окей это"}'
    )
    a = session.add(b)

    session.commit()
    # a = Discord.get_idInDB("idtx3CvPRU5BKc9uqcH5inWQnDChp3", session)
    #
    # a.actions


if __name__ == "__main__":
    main_()
