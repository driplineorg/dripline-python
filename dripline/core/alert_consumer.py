from _dripline.core import Service

__all__ = []

__all__.append('AlertConsumer')
class AlertConsumer(Service):
    '''
    A base class for implementing custom alert message consumers.

    One is expected to extend this class in one of two ways:
    1) More advanced: override the existing on_alert_message method with whatever behavior is desired
    2) Use the existing on_alert_message, which proceeds in two steps by calling parse_routing_key, followed by process_payload.
       The first may be used or overriden, the second must always be implemented.
    '''
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
        routing_data = self.parse_routing_key(an_alert.routing_key)
        self.process_payload(an_alert.payload, routing_data)

    def parse_routing_key(self, a_routing_key):
        pass

    def process_payload(self, a_payload, a_routing_key_data):
        pass
