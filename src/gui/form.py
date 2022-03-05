import ttkbootstrap as ttk
from ttkbootstrap.constants import *


def create_entry_with_label(master=None, name=""):
    frame = ttk.Frame(master=master)
    frame.pack(fill=X, padx=(10, 0), side=LEFT)

    label = ttk.Label(master=frame, text=name)
    label.pack(side=LEFT, ipadx=5, ipady=5, pady=1)

    entry = ttk.Entry(master=frame, bootstyle="default")
    entry.pack(side=LEFT, ipadx=5, ipady=5, pady=1)

    return entry


def create_form(master, groups_of_fields):
    entries = {}

    for group in groups_of_fields:
        row = ttk.Frame(master=master)
        row.pack(fill=X, pady=15, side=TOP)

        for field in group:
            entry = create_entry_with_label(row, group[field]["title"]+":")
            entry.insert(0, group[field]["default"])
            entries[field] = entry

    return entries
