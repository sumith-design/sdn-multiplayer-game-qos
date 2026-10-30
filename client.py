import random
import socket
import struct
import sys
import time

SERVER = ('10.0.0.1', 5000)
PLAYER_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 1
TICK = 0.05  # 20 updates/second
FMT = '!IIdff'

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.01)

x, y = random.uniform(0, 100), random.uniform(0, 100)
seq = 0

while True:
    x += random.uniform(-1, 1)
    y += random.uniform(-1, 1)
    seq += 1
    sock.sendto(struct.pack(FMT, PLAYER_ID, seq, time.time(), x, y), SERVER)

    try:
        while True:
            data, _ = sock.recvfrom(4096)
            if seq % 40 == 0:
                print(f'[client {PLAYER_ID}] tick {seq}: {len(data) // 12} players in world', flush=True)
    except socket.timeout:
        pass

    time.sleep(TICK)
