from sqlalchemy import MetaData, Column, Integer, String, TIMESTAMP, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from datetime import datetime

engine = create_engine('sqlite:///app.db')

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class Message(Base):
    __tablename__ = "Messages"

    id = Column(Integer, primary_key=True)
    message_content = Column(String(2000), index=True, nullable=False)
    message_sender = Column(Integer, index=True, nullable=False)
    message_channel = Column(Integer)
    message_server = Column(Integer)
    message_sent_time = Column(TIMESTAMP, default=datetime.utcnow)

    def __repr__(self):
        return self.message_content


def create_db():
    Base.metadata.create_all(engine)


def make_session():
    """ Makes a database session needed to access the DB. Be sure to close the session afterwards!

    :return db_session: a Session for the database above
    """
    Base.metadata.bind = engine
    db_session = Session(bind=engine)
    return db_session
