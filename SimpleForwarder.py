# Import necessary libraries
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.ipv4 import ipv4

# Initialize logger
log = core.getLogger()

# Define the SimpleForwarding class
class SimpleForwarding(object):
    def __init__(self, connection):
        self.connection = connection
        self.mactable = {}
        connection.addListeners(self)

    def _handle_PacketIn(self, event):
        packet = event.parsed
        packet_in = event.ofp

        # Learn the source MAC address and the port it came from
        self.mactable[packet.src] = packet_in.in_port

        # Check if the destination MAC address is known
        if packet.dst in self.mactable:
            out_port = self.mactable[packet.dst]
            self.resend_packet(packet_in, out_port)
        else:
            self.resend_packet(packet_in, of.OFPP_FLOOD)

    # The resend_packet method
    def resend_packet(self, packet_in, out_port):
        msg = of.ofp_packet_out()
        msg.data = packet_in
        action = of.ofp_action_output(port = out_port)
        msg.actions.append(action)
        self.connection.send(msg)

# Launch the controller
def launch():
    def start_switch(event):
        log.debug("Controlling %s" % (event.connection,))
        SimpleForwarding(event.connection)

    core.openflow.addListenerByName("ConnectionUp", start_switch)
