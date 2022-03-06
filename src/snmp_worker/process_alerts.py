from datetime import datetime

from models.alert import Alert
from models.measurements import Measurement
from snmp_worker.send_notification import send_notification


last_processed_time = datetime.now()


def process_alerts(session):
    global last_processed_time
    alerts = session.query(Alert).all()

    for alert in alerts:
        newer_measurement = session.query(Measurement).filter(
            Measurement.timestamp > last_processed_time
        ).filter(
            Measurement.metric == alert.metric
        ).order_by(
            Measurement.timestamp.desc()
        ).first()

        last_measurement = session.query(Measurement).filter(
            Measurement.timestamp < last_processed_time
        ).filter(
            Measurement.metric == alert.metric
        ).order_by(
            Measurement.timestamp.desc()
        ).first()
        last_processed_time = datetime.utcnow()
        if last_measurement is None or newer_measurement is None:
            continue

        increase_in_value = newer_measurement.value - last_measurement.value
        if increase_in_value > alert.increase_threshold:
            title = f'ALERT - {alert.metric} increased more than {alert.increase_threshold}'
            message = f'Measurement has increased by {increase_in_value} at {newer_measurement.timestamp}'
            send_notification(title, message)
