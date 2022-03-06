import notify2


def send_notification(title, message):
    notify2.init("TeutoMonitor")
    notice = notify2.Notification(title, message)
    notice.show()
    return
