from sqlalchemy import Column, Integer, String, DateTime
import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Measurement(Base):
    __tablename__ = 'Measurement'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    metric = Column(String)
    value = Column(Integer)


def __repr__(self):
    return "<(Measurement id='%i', metric=%s, value=%s, time='%s')>" % (
        self.id, self.metric, self.value, self.time)
