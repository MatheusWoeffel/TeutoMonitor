from multiprocessing import Process
from snmp_worker import snmp_worker


def f(name):
    print('hello', name)


if __name__ == '__main__':
    p = Process(target=snmp_worker.run_snmp_worker)
    p.start()
    p.join()
