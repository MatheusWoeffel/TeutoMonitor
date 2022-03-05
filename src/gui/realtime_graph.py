import tkinter as tk
from tkinter import ttk
from ttkbootstrap.constants import *
import matplotlib.animation as animation
from matplotlib import style, dates
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from models.measurements import Measurement


engine = create_engine('sqlite:///db.sqlite3')
db = Session(engine)

style.use('ggplot')

# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)


def animate(i):
    xs = []
    xs_labels = []
    ys = []

    data = db.query(Measurement).order_by(
        Measurement.timestamp.desc()).filter(Measurement.metric == 'ifInOctets').limit(100).all()

    data = data[::-1]

    for measure in data:
        xs.append(dates.date2num(measure.timestamp))
        xs_labels.append(measure.timestamp.strftime('%H:%M:%S.%f'))
        ys.append(measure.value)

    # Draw x and y lists
    ax.clear()
    ax.set_xticklabels(xs_labels)
    ax.plot(xs, ys)

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('Real time cool data')
    plt.ylabel('Bytes')


class RealTimeGraph(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Real time data")
        label.pack(pady=10, padx=10)

        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
