from _dripline.core import Service

__all__ = []

__all__.append('AlertConsumer')
class AlertConsumer(Service):
    def __init__(self, alert_keys=["#"], **kwargs):
        print("in AlertConsumer init")
        Service.__init__(self, **kwargs)
        self._alert_keys = alert_keys

    def bind_keys(self):
        print("in python's bind keys")
        to_return = Service.bind_keys(self);
        for a_key in self._alert_keys:
            print(" binding alert key {}".format(a_key))
            to_return = to_return and self.bind_key("alerts", a_key)
        return to_return

    def on_alert_message(self, an_alert):
        print("in python's on alert")
