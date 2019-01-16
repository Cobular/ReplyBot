from sqlalchemy import MetaData, Column, Integer, String, TIMESTAMP, create_engine, BIGINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from datetime import datetime
import os
import logging


DATABASE_URL = os.environ['DATABASE_URL']
engine = create_engine(DATABASE_URL)

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class Message(Base):
    __tablename__ = "Messages"

    id = Column(Integer, primary_key=True)
    message_content = Column(String(2000), index=True, nullable=False)
    message_sender = Column(BIGINT, index=True, nullable=False)
    message_channel = Column(BIGINT)
    message_server = Column(BIGINT)
    message_sent_time = Column(TIMESTAMP, default=datetime.utcnow)

    def __repr__(self):
        return self.message_content

    @classmethod
    def prune_db(cls, num: int):
        session = make_session()
        count = 0
        while session.query(Message).count() > num:
            obj = session.query(Message).order_by(Message.message_sent_time.asc()).first()
            session.delete(obj)
            count += 1
        session.commit()
        session.close()
        if count > 0:
            logging.log("INFO", str(count) + " messages deleted")


def create_db():
    Base.metadata.create_all(engine)


def make_session():
    """ Makes a database session needed to access the DB. Be sure to close the session afterwards!

    :return db_session: a Session for the database above
    """
    Base.metadata.bind = engine
    db_session = Session(bind=engine)
    return db_session
