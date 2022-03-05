from multiprocessing import Process
from snmp_worker import snmp_worker
import gui.window as window


def f(name):
    print('hello', name)


if __name__ == '__main__':
    p_window = Process(target=window.start)
    p_worker = Process(target=snmp_worker.run_snmp_worker)

    p_window.start()
    p_worker.start()

    p_worker.join()
    p_window.join()
