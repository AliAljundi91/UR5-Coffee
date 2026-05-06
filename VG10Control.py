from pymodbus.client import ModbusTcpClient


class VG10:
    def __init__(self, ip="192.168.1.1", port=502):
        self.ip = ip
        self.port = port
        self.client = ModbusTcpClient(ip, port=port)

    def connect(self):
        return self.client.connect()

    def disconnect(self):
        self.client.close()

    # -------------------------
    # Internal write helper
    # -------------------------
    def _write_channel_a(self, mode, vacuum=0):
        value = (mode << 8) | vacuum
        self.client.write_register(0x0000, value)

    # -------------------------
    # GRIP
    # -------------------------
    def grip(self, vacuum=60):
        self._write_channel_a(mode=1, vacuum=vacuum)

    # -------------------------
    # RELEASE
    # -------------------------
    def release(self):
        self._write_channel_a(mode=0, vacuum=0)

    # -------------------------
    # IDLE (optional but useful)
    # -------------------------
    def idle(self):
        self._write_channel_a(mode=2, vacuum=0)