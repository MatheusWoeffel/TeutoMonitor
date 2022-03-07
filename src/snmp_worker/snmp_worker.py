import time
import datetime
from sqlalchemy.orm import Session
from sqlalchemy.sql import between
from sqlalchemy import create_engine
from models.base import Base
from models.measurements import Measurement
from models.agents import Agent
from snmp.session import SNMPSession
from snmp_worker.process_alerts import process_alerts

MEASUREMENT_INTERVAL = 2


def get_all_agents(session):
    return session.query(Agent).all()


def get_new_agents(session):
    td = datetime.timedelta(seconds=MEASUREMENT_INTERVAL+1)
    now = datetime.datetime.utcnow()
    tmin = now - td
    return session.query(Agent).filter(between(Agent.created_at, tmin, now)).all()


def get_in_out_octets(snmp_session, numInterfaces):
    queries = ['ifInOctets', 'ifOutOctets']
    numQueries = len(queries)

    countBulk = snmp_session.session().get_bulk(
        queries, 0, numInterfaces)
    valifInOctets = {}
    valifOutOctets = {}

    for i in range(numInterfaces):
        ifInOctets = countBulk[i*numQueries]
        ifOutOctets = countBulk[i*numQueries + 1]

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
    Base.metadata.create_all(engine)

    agents = get_all_agents(db)

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

        new_agents = get_new_agents(db)
        if len(new_agents) > 0:
            for new_agent in new_agents:
                if new_agent.host_ip not in agent_sessions:
                    snmp_session = snmp_session_for_agent(new_agent)
                    agent_sessions[new_agent.host_ip] = {"agent": new_agent,
                                                         "session": snmp_session,
                                                         "instance_name": snmp_session.get_instance_name(),
                                                         "interfaces_count": snmp_session.get_interfaces_count()}

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

        process_alerts(db)
        time.sleep(MEASUREMENT_INTERVAL)
