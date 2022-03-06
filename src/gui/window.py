import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Dialog

from gui.realtime_graph import RealTimeGraph
import matplotlib.animation as animation
from gui.animation import Animation, network_traffic_filler

from models.agents import Agent
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from gui.form import create_entry_with_label, create_form
from models.alert import Alert

create_agent_form = [{
    "host_ip": {"title": "IP", "default": "0.0.0.0"},
    "snmp_version": {"title": "SNMP version", "default": "3"}
}, {
    "security_username": {"title": "Security username", "default": ""},
    "privacy_password": {"title": "Privacy password", "default": ""},
    "privacy_protocol": {"title": "Privacy protocol", "default": ""},
}, {
    "auth_password": {"title": "Auth password", "default": ""},
    "auth_protocol": {"title": "Auth protocol", "default": ""},
}]

traffic_animation = Animation("Network Traffic", ylabel="Traffic rate(Mbps)")
graph_refresher = traffic_animation.create_animation(
    network_traffic_filler)


class CreateAgentDialog(Dialog):
    def __init__(self, parent=None, title='', alert=False):
        super().__init__(parent, title, alert)
        self.entries = {}

    def create_body(self, master):
        frame = ttk.Frame(master=master)
        frame.pack(fill=X, ipadx=10, ipady=10, side=TOP)

        self.entries = create_form(frame, create_agent_form)

        return frame

    def create_buttonbox(self, master):
        frame = ttk.Frame(master=master)
        frame.pack(fill=X, pady=1, ipadx=10, ipady=10, side=BOTTOM)

        def on_click_save_agent():
            agent = Agent(
                host_ip=self.entries["host_ip"].get(),
                snmp_version=int(self.entries["snmp_version"].get()),
                security_username=self.entries["security_username"].get(),
                privacy_password=self.entries["privacy_password"].get(),
                privacy_protocol=self.entries["privacy_protocol"].get(),
                auth_password=self.entries["auth_password"].get(),
                auth_protocol=self.entries["auth_protocol"].get(),
            )
            engine = create_engine('sqlite:///db.sqlite3')
            db = Session(engine)
            db.add(agent)
            db.commit()

            self.destroy()

        btn = ttk.Button(
            master=master, text='Add agent',
            compound=LEFT,
            command=on_click_save_agent
        )
        btn.pack(side=RIGHT, ipadx=5, ipady=5, padx=(0, 15), pady=1)
        return btn


create_alert_form = [{
    "metric": {"title": "Metric", "default": "ifInOctets"},
    "increase_threshold": {"title": "Increase threshold", "default": "30000"}
}]


class CreateAlertDialog(Dialog):
    def __init__(self, parent=None, title='', alert=False):
        super().__init__(parent, title, alert)
        self.entries = {}

    def create_body(self, master):
        frame = ttk.Frame(master=master)
        frame.pack(fill=X, ipadx=10, ipady=10, side=TOP)

        self.entries = create_form(frame, create_alert_form)

        return frame

    def create_buttonbox(self, master):
        frame = ttk.Frame(master=master)
        frame.pack(fill=X, pady=1, ipadx=10, ipady=10, side=BOTTOM)

        def on_click_save_alert():
            alert = Alert(
                metric=self.entries["metric"].get(),
                increase_threshold=self.entries["increase_threshold"].get(),
            )
            engine = create_engine('sqlite:///db.sqlite3')
            db = Session(engine)
            db.add(alert)
            db.commit()

            self.destroy()

        btn = ttk.Button(
            master=master, text='Add alert',
            compound=LEFT,
            command=on_click_save_alert
        )
        btn.pack(side=RIGHT, ipadx=5, ipady=5, padx=(0, 15), pady=1)
        return btn


class MainScreen(ttk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pack(fill=BOTH, expand=YES)

        # buttonbar
        buttonbar = ttk.Frame(self, style='secondary.TFrame')
        buttonbar.pack(fill=X, pady=1, side=TOP)

        # add agent button
        def createAgentDialog(): return CreateAgentDialog(
            parent=self, title="Add new agent").show()
        btn = ttk.Button(
            master=buttonbar, text='Add agent',
            compound=LEFT,
            style='secondary',
            command=createAgentDialog
        )
        btn.pack(side=LEFT, ipadx=5, ipady=5, padx=(1, 0), pady=1)

        # add  alert button
        def createAlertDialog(): return CreateAlertDialog(
            parent=self, title="Add new Alert").show()
        btn = ttk.Button(
            master=buttonbar, text='Add Alert',
            compound=LEFT,
            style='secondary',
            command=createAlertDialog
        )
        btn.pack(side=LEFT, ipadx=5, ipady=5, padx=(1, 0), pady=1)

        # graph
        graph = RealTimeGraph(self, traffic_animation.fig)
        graph.pack(fill=X, pady=1, side=TOP)


def start():
    app = ttk.Window(title="TeutoMonitor",
                     themename="superhero", minsize=(1280, 720))
    MainScreen(app)

    anim = animation.FuncAnimation(
        traffic_animation.fig, graph_refresher, interval=1000)

    app.mainloop()
