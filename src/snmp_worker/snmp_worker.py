import time
from easysnmp import Session as easysnmpSession
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from models.base import Base
from models.measurements import Measurement
from models.agents import Agent
from snmp.session import SNMPSession

MEASUREMENT_INTERVAL = 2


def get_all_agents(session):
    return session.query(Agent).all()


def get_in_out_octets(snmp_session, numInterfaces):
    countBulk = snmp_session.session().get_bulk(
        ['ifInOctets', 'ifOutOctets'], 0, numInterfaces)
    valifInOctets = {}
    valifOutOctets = {}

    for i in range(numInterfaces):
        ifInOctets = countBulk[i*numInterfaces]
        ifOutOctets = countBulk[i*numInterfaces + 1]

        valifInOctets[i] = int(ifInOctets.value)
        valifOutOctets[i] = int(ifOutOctets.value)

    return (valifInOctets, valifOutOctets)


def snmp_session_for_agent(agent):
    return SNMPSession(host_ip=agent.host_ip, snmp_version=agent.snmp_version,
                       security_username=agent.security_username,
                       privacy_password=agent.privacy_password,
                       privacy_protocol=agent.privacy_protocol,
                       auth_password=agent.auth_password,
                       auth_protocol=agent.auth_protocol)


def run_snmp_worker():
    engine = create_engine('sqlite:///db.sqlite3')
    db = Session(engine)
    db.query
    Base.metadata.create_all(engine)

    agents = get_all_agents(db)

    snmp_session = snmp_session_for_agent(agents[0])

    agent_sessions = {}
    for agent in agents:
        snmp_session = snmp_session_for_agent(agent)
        agent_sessions[agent.host_ip] = {"agent": agent,
                                         "session": snmp_session,
                                         "instance_name": snmp_session.get_instance_name(),
                                         "interfaces_count": snmp_session.get_interfaces_count()}

    round = 1
    while True:
        print("Round ", round)
        round += 1

        for ip, agent_session in agent_sessions.items():
            print("> Monitoring IP:", ip)
            beforeValifInOctets = {}
            beforeValifOutOctets = {}

            beforeValifInOctets, beforeValifOutOctets = get_in_out_octets(
                agent_session["session"], agent_session["interfaces_count"])

            newInOctetsEntry = Measurement(
                metric='ifInOctets', value=beforeValifInOctets[1],
                agent_id=agent_session["agent"].id)
            newOutOctetsEntry = Measurement(
                metric='ifOutOctets', value=beforeValifOutOctets[1],
                agent_id=agent_session["agent"].id)

            db.add(newInOctetsEntry)
            db.add(newOutOctetsEntry)
            db.commit()

        time.sleep(MEASUREMENT_INTERVAL)
