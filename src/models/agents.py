from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
import datetime
from models.base import Base


class Agent(Base):
    __tablename__ = 'Agents'
    id = Column(Integer, primary_key=True)
    host_ip = Column(String, nullable=False)
    snmp_version = Column(Integer, nullable=False)
    security_username = Column(String)
    privacy_password = Column(String)
    privacy_protocol = Column(String)
    auth_password = Column(String)
    auth_protocol = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    measurements = relationship("Measurement")

    def __repr__(self):
        return "<(Agent id='%i', host_ip=%s, snmp_version=%s, security_username=%s, privacy_password=%s, privacy_protocol=%s, auth_password=%s, auth_protocol=%s, created_at=%s)>" % (
            self.id, self.host_ip, self.snmp_version, self.security_username, self.privacy_password, self.privacy_protocol, self.auth_password, self.auth_protocol, self.created_at)
