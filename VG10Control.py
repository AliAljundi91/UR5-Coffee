from pymodbus.client import ModbusTcpClient
import time


class VG10:
    def __init__(self, ip="192.168.1.1", port=502, slave_id=65):
        self.ip = ip
        self.port = port
        self.slave_id = slave_id

        self.client = ModbusTcpClient(
            host=self.ip,
            port=self.port,
            timeout=0.2,
            retries=0
        )

    # -------------------------
    # CONNECT
    # -------------------------
    def connect(self):
        connected = self.client.connect()

        if connected:
            print(f"Connected to VG10 at {self.ip}:{self.port}")
        else:
            print("Failed to connect")

        return connected

    # -------------------------
    # DISCONNECT
    # -------------------------
    def disconnect(self):
        self.client.close()

    # -------------------------
    # INTERNAL WRITE
    # -------------------------
    def _write_channel(self, channel, mode, vacuum=0):
        """
        channel:
            'A' or 'B'

        mode:
            0 = release
            1 = grip

        vacuum:
            0-80
        """

        value = (mode << 8) | vacuum

        # Register selection
        if channel.upper() == "A":
            address = 0x0000
        elif channel.upper() == "B":
            address = 0x0001
        else:
            raise ValueError("Channel must be 'A' or 'B'")

        start = time.time()

        result = self.client.write_register(
            address=address,
            value=value,
            slave=self.slave_id
        )

        elapsed = time.time() - start

        if result.isError():
            print(f"Write failed on channel {channel}")
        #else:
            #print(f"Channel {channel} command sent in {elapsed:.3f}s")

    # -------------------------
    # CHANNEL A
    # -------------------------
    def grip_a(self, vacuum=60):
        self._write_channel("A", mode=1, vacuum=vacuum)

    def release_a(self):
        self._write_channel("A", mode=0, vacuum=0)
    
    def get_vacuum_a(self):

        result = self.client.read_holding_registers(
            address=0x0012,
            count=1,
            slave=self.slave_id
        )

        return result.registers[0] / 10.0

    # -------------------------
    # CHANNEL B
    # -------------------------
    def grip_b(self, vacuum=60):
        self._write_channel("B", mode=1, vacuum=vacuum)

    def release_b(self):
        self._write_channel("B", mode=0, vacuum=0)

    def get_vacuum_b(self):

        result = self.client.read_holding_registers(
            address=0x0013,
            count=1,
            slave=self.slave_id
        )

        return result.registers[0] / 10.0