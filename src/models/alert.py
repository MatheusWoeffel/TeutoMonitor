from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from models.base import Base


class Alert(Base):
    __tablename__ = 'Alert'
    id = Column(Integer, primary_key=True)
    metric = Column(String)
    increase_threshold = Column(Integer)

    def __repr__(self):
        return "<(Alert id='%i', metric=%s, increaseThreshold=%s)>" % (
            self.id, self.metric, self.increase_threshold)
