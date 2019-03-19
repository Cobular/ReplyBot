from sqlalchemy import Column, Integer, String, TIMESTAMP, create_engine, BIGINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from datetime import datetime
import os
import logging


DATABASE_URL = os.environ['DATABASE_URL']
engine = create_engine(DATABASE_URL, echo=False)

Base = declarative_base()


class Message(Base):
    __tablename__ = "messages"

    id = Column("id", Integer, primary_key=True)
    message_content = Column("message_content", String(2000), index=True, nullable=False)
    message_id = Column('message_id', BIGINT, nullable=False)
    message_sender = Column("message_sender", BIGINT, index=True, nullable=False)
    message_channel = Column("message_channel", BIGINT)
    message_server = Column("message_server", BIGINT)
    message_sent_time = Column("message_sent_time", TIMESTAMP, default=datetime.utcnow)

    def __repr__(self):
        return self.message_content

    @classmethod
    def prune_db(cls, num_to_get_to: int):
        session = make_session()
        count = 0
        servers = session.query(Message.message_server).distinct()
        for server in servers:
            total_num = session.query(Message).filter(Message.message_server == server.message_server).count()
            num_to_delete = total_num - num_to_get_to
            if num_to_delete > 0:
                ids_to_keep = session.query(Message.id).order_by(Message.message_sent_time.asc()).limit(num_to_delete).subquery()
                session.query(Message).filter(Message.id.in_(ids_to_keep)).delete(synchronize_session='fetch')
                count += num_to_delete

        session.commit()
        session.close()
        print("done")
        if count > 0:
            logging.log(20, str(count) + " messages deleted")


def create_db():
    Base.metadata.create_all(engine)


def make_session():
    """ Makes a database session needed to access the DB. Be sure to close the session afterwards!

    :return db_session: a Session for the database above
    """
    Base.metadata.bind = engine
    db_session = Session(bind=engine)
    return db_session
