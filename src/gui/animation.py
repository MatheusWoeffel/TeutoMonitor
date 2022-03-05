from matplotlib import style, dates
from matplotlib import pyplot as plt

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from models.measurements import Measurement

style.use('ggplot')


class Animation():
    def __init__(self, title="", ylabel=""):
        self.title = title
        self.ylabel = ylabel

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(1, 1, 1)

        self.xs = []
        self.ys = []
        self.xs_labels = []

    def create_animation(self, data_filler):
        def animate(i):
            data_filler(self.xs, self.ys, self.xs_labels)

            # Draw x and y lists
            self.ax.clear()
            if len(self.xs_labels) > 0:
                self.ax.set_xticklabels(self.xs_labels)
            self.ax.plot(self.xs, self.ys)

            # Format plot
            plt.xticks(rotation=45, ha='right')
            plt.subplots_adjust(bottom=0.30)
            plt.title(self.title)
            plt.ylabel(self.ylabel)

        return animate


engine = create_engine('sqlite:///db.sqlite3')
db = Session(engine)


def network_traffic_filler(xs, ys, xs_labels):
    data = db.query(Measurement).order_by(
        Measurement.timestamp.desc()).filter(Measurement.metric == 'ifInOctets').limit(100).all()

    data = data[::-1]

    xs.clear()
    ys.clear()
    xs_labels.clear()
    for measure in data:
        xs.append(dates.date2num(measure.timestamp))
        xs_labels.append(measure.timestamp.strftime('%H:%M:%S.%f'))
        ys.append(measure.value)
