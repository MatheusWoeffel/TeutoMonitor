from matplotlib import style, dates
from matplotlib import pyplot as plt

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from models.agents import Agent
from models.measurements import Measurement

style.use('ggplot')


class Animation():
    def __init__(self, title="", ylabel=""):
        self.title = title
        self.ylabel = ylabel

        self.fig = plt.figure(figsize=(4, 4))
        self.ax = self.fig.add_subplot(1, 1, 1)

        self.xs_dict = {}
        self.ys_dict = {}
        self.xs_labels_dict = {}

    def create_animation(self, data_filler):
        def animate(i):
            data_filler(self.xs_dict, self.ys_dict, self.xs_labels_dict)

            self.ax.clear()
            for key in self.xs_dict.keys():
                if len(self.xs_labels_dict[key]) > 0:
                    self.ax.set_xticklabels(self.xs_labels_dict[key])

                self.ax.plot(self.xs_dict[key],
                             self.ys_dict[key], label=key)

            # Format plot
            self.fig.suptitle(self.title)
            self.ax.set_ylabel(self.ylabel)
            if len(self.xs_dict) > 0:
                self.ax.legend(loc="upper left")
            self.ax.tick_params(axis="x", rotation=45)
            self.fig.subplots_adjust(bottom=0.30)

        return animate


engine = create_engine('sqlite:///db.sqlite3')
db = Session(engine)


def base_network_traffic_filler(data, xs_dict, ys_dict, xs_labels_dict):
    agents = db.query(Agent).all()
    agents_by_id = {}
    for agent in agents:
        agents_by_id[agent.id] = agent

    data_by_agent = {}
    for measure in data:
        if measure.agent_id not in data_by_agent:
            data_by_agent[measure.agent_id] = []
        data_by_agent[measure.agent_id].append(measure)

    estimated_traffic_by_agent = {}
    for agent, measures in data_by_agent.items():
        estimated_traffic_by_agent[agent] = []
        for i in range(1, len(measures)):
            currentPoint = measures[i]
            beforePoint = measures[i - 1]
            bytesIncrease = currentPoint.value - beforePoint.value
            timeDifference = currentPoint.timestamp - beforePoint.timestamp
            timeDifferenceInSeconds = timeDifference.microseconds / 1000000

            estimated_traffic_by_agent[agent].append({
                "value": (bytesIncrease / timeDifferenceInSeconds) / (1024*1024),
                "timestamp": currentPoint.timestamp
            })

    xs_dict.clear()
    ys_dict.clear()
    xs_labels_dict.clear()

    for agent, estimated_traffic in estimated_traffic_by_agent.items():
        agent_key = agents_by_id[agent].host_ip
        if agents_by_id[agent].snmp_version == 3:
            agent_key = agents_by_id[agent].security_username + \
                "@" + agents_by_id[agent].host_ip
        xs_dict[agent_key] = []
        ys_dict[agent_key] = []
        xs_labels_dict[agent_key] = []
        for traffic in estimated_traffic:
            xs_dict[agent_key].append(dates.date2num(traffic['timestamp']))
            xs_labels_dict[agent_key].append(
                traffic['timestamp'].strftime('%H:%M:%S.%f'))
            ys_dict[agent_key].append(traffic['value'])


def network_traffic_in_filler(xs_dict, ys_dict, xs_labels_dict):
    data = db.query(Measurement).order_by(Measurement.timestamp.desc()).filter(
        Measurement.metric == 'ifInOctets').distinct(Measurement.timestamp).limit(100).all()
    data = data[::-1]

    base_network_traffic_filler(data, xs_dict, ys_dict, xs_labels_dict)


def network_traffic_out_filler(xs_dict, ys_dict, xs_labels_dict):
    data = db.query(Measurement).order_by(Measurement.timestamp.desc()).filter(
        Measurement.metric == 'ifOutOctets').distinct(Measurement.timestamp).limit(100).all()
    data = data[::-1]

    base_network_traffic_filler(data, xs_dict, ys_dict, xs_labels_dict)
