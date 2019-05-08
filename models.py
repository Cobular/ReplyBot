import logging
import os
from datetime import datetime

from sqlalchemy import Column, Integer, String, TIMESTAMP, create_engine, BIGINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session

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
                ids_to_keep = session.query(Message.id).order_by(Message.message_sent_time.asc()).limit(
                    num_to_delete).subquery()
                session.query(Message).filter(Message.id.in_(ids_to_keep)).delete(synchronize_session='fetch')
                count += num_to_delete

        session.commit()
        session.close()
        print("done")
        if count > 0:
            logging.info(str(count) + " messages deleted in Messages")


class TempMessage(Base):
    __tablename__ = "tempmessages"

    id = Column("id", Integer, primary_key=True)
    message_id = Column('message_id', BIGINT, nullable=False)
    message_sender = Column("message_sender", BIGINT, index=True, nullable=False)
    message_channel = Column("message_channel", BIGINT)
    message_server = Column("message_server", BIGINT)
    message_sent_time = Column("message_sent_time", TIMESTAMP, default=datetime.utcnow)
    message_reactor_id = Column("message_reactor_id", BIGINT, nullable=False)

    @staticmethod
    def prune_db(num_to_get_to: int):
        session = make_session()
        count = 0
        users = session.query(TempMessage.message_reactor_id).distinct()
        for user in users:
            total_num = session.query(TempMessage).filter(
                TempMessage.message_reactor_id == user.message_reactor_id).count()
            num_to_delete = total_num - num_to_get_to
            if num_to_delete > 0:
                ids_to_keep = session.query(TempMessage.id).order_by(TempMessage.message_sent_time.asc()).limit(
                    num_to_delete).subquery()
                session.query(TempMessage).filter(TempMessage.id.in_(ids_to_keep)).delete(synchronize_session='fetch')
                count += num_to_delete

        session.commit()
        session.close()
        if count > 0:
            logging.info(str(count) + " messages deleted in TempMessages")


def create_db():
    Base.metadata.create_all(engine)


def print_model_sql():
    created_table = CreateTable(Message.__table__)
    tableCompiled = created_table.compile(engine)
    print(str(tableCompiled) + ';')
    reated_table = CreateTable(TempMessage.__table__)
    tableCompiled = created_table.compile(engine)
    print(str(tableCompiled) + ';')


def make_session() -> Session:
    """ Makes a database session needed to access the DB. Be sure to close the session afterwards!

    :return db_session: a Session for the database above
    """
    Base.metadata.bind = engine
    db_session = Session(bind=engine)
    return db_session
