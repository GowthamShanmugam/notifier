from etcd import EtcdException
from etcd import EtcdKeyNotFound
from tendrl.notifier.objects.alert import Alert


def read_key(key):
    try:
        return NS._int.client.read(key, quorum=True)
    except (AttributeError, EtcdException) as ex:
        if type(ex) == EtcdKeyNotFound:
            raise ex
        else:
            try:
                NS._int.reconnect()
                return NS._int.client.read(key, quorum=True)
            except (AttributeError, EtcdException) as ex:
                raise ex

def read(key):
    result = {}
    job = {}
    try:
        job = read_key(key)
    except EtcdKeyNotFound:
        pass
    except (AttributeError, EtcdException) as ex:
        raise ex
    if hasattr(job, 'leaves'):
        for item in job.leaves:
            if key == item.key:
                result[item.key.split("/")[-1]] = item.value
                return result
            if item.dir is True:
                result[item.key.split("/")[-1]] = read(item.key)
            else:
                result[item.key.split("/")[-1]] = item.value
    return result


def get_alert_ids():
    alert_ids = []
    try:
        alerts = read_key(
            '/alerting/alerts'
        )
    except EtcdKeyNotFound:
        return alerts_ids
    except (AttributeError, EtcdException) as ex:
        raise ex
    for alert in alerts.leaves:
        alert_parts = alert.key.split('/')
        if len(alert_parts) >= 4:
            alert_ids.append(alert_parts[3])
    return alert_ids


def get_alerts(alert_ids):
    # TODO: Revert to using object#load instead of etcd read
    # once the issue in object#load is found and fixed.
    alerts_arr = []
    try:
        for alert_id in alert_ids:
            alerts_arr.append(Alert(alert_id=alert_id).load())
    except EtcdKeyNotFound:
        return alerts_arr
    except (EtcdException, AttributeError) as ex:
        raise ex
    return alerts_arr
