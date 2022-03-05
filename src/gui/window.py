import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Dialog
from models.agents import Agent
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from gui.form import create_entry_with_label, create_form

create_agent_form = [{
    "host_ip": {"title": "IP", "default": "0.0.0.0"},
    "snmp_version": {"title": "SNMP version", "default": "3"}
}, {
    "security_username": {"title": "Security username", "default": ""},
    "privacy_password": {"title": "Privacy password", "default": ""},
    "privacy_protocol": {"title": "Privacy protocol", "default": ""},
    "auth_password": {"title": "Auth password", "default": ""},
    "auth_protocol": {"title": "Auth protocol", "default": ""},
}]


class CreateAgentDialog(Dialog):
    def __init__(self, parent=None, title='', alert=False):
        super().__init__(parent, title, alert)
        self.entries = {}

    def create_body(self, master):
        frame = ttk.Frame(master=master)
        frame.pack(fill=X, pady=1, side=TOP)

        self.entries = create_form(frame, create_agent_form)

        return frame

    def create_buttonbox(self, master):
        frame = ttk.Frame(master=master)
        frame.pack(fill=X, pady=1, side=BOTTOM)

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
        btn = ttk.Button(
            master=master, text='Add agent',
            compound=LEFT,
            command=on_click_save_agent
        )
        btn.pack(side=RIGHT, ipadx=5, ipady=5, padx=(1, 0), pady=1)
        return btn


class MainScreen(ttk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pack(fill=BOTH, expand=YES)

        # buttonbar
        buttonbar = ttk.Frame(self, style='primary.TFrame')
        buttonbar.pack(fill=X, pady=1, side=TOP)

        # new backup

        def _func(): return CreateAgentDialog(parent=self, title="adad").show()
        btn = ttk.Button(
            master=buttonbar, text='Add agent',
            compound=LEFT,
            command=_func
        )
        btn.pack(side=LEFT, ipadx=5, ipady=5, padx=(1, 0), pady=1)


def start():
    app = ttk.Window(title="Back Me Up", themename="superhero")
    MainScreen(app)
    app.mainloop()
