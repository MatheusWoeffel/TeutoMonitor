import time
from easysnmp import Session as easysnmpSession
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from models.base import Base
from models.measurements import Measurement


def run_snmp_worker():
    engine = create_engine('sqlite:///db.sqlite3')
    db = Session(engine)
    Base.metadata.create_all(engine)

    session = easysnmpSession(
        hostname='192.168.50.152', community='public', version=2)
    instanceName = session.get('sysName.0')
    print('Nome da instancia', instanceName.value)
    numInterfaces = int(session.get('ifNumber.0').value)
    print(numInterfaces)

    def getInOutOctets(numInterfaces):
        countBulk = session.get_bulk(
            ['ifInOctets', 'ifOutOctets'], 0, numInterfaces)
        valifInOctets = {}
        valifOutOctets = {}

        for i in range(numInterfaces):
            ifInOctets = countBulk[i*numInterfaces]
            ifOutOctets = countBulk[i*numInterfaces + 1]

            valifInOctets[i] = int(ifInOctets.value)
            valifOutOctets[i] = int(ifOutOctets.value)

        return (valifInOctets, valifOutOctets)

    round = 1
    while True:
        MEASUREMENT_INTERVAL = 2
        print("Round ", round)
        round += 1
        beforeValifInOctets = {}
        beforeValifOutOctets = {}
        beforeValifInOctets, beforeValifOutOctets = getInOutOctets(
            numInterfaces)
        newInOctetsEntry = Measurement(
            metric='ifInOctets', value=beforeValifInOctets[1])
        newOutOctetsEntry = Measurement(
            metric='ifOutOctets', value=beforeValifOutOctets[1])
        db.add(newInOctetsEntry)
        db.add(newOutOctetsEntry)
        db.commit()
        time.sleep(MEASUREMENT_INTERVAL)
