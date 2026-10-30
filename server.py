import socket
import struct
import time

HOST, PORT = '10.0.0.1', 5000
FMT = '!IIdff'  # player_id, seq, timestamp, x, y
FMT_SIZE = struct.calcsize(FMT)
REPORT_EVERY = 5  # seconds

players = {}  # pid -> (addr, x, y)
stats = {}    # pid -> dict(last_seq, received, lost, lat_sum, jit_sum, last_lat, n_jit)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))
sock.settimeout(1.0)
print(f'Game server listening on {HOST}:{PORT}', flush=True)

log = open('game_log.csv', 'w')
log.write('time,player,seq,latency_ms\n')
next_report = time.time() + REPORT_EVERY


def broadcast():
    msg = b''.join(struct.pack('!Iff', pid, x, y) for pid, (_, x, y) in players.items())
    for addr, _, _ in players.values():
        sock.sendto(msg, addr)


def report():
    for pid, s in sorted(stats.items()):
        total = s['received'] + s['lost']
        loss = 100 * s['lost'] / total if total else 0
        lat = s['lat_sum'] / s['received'] if s['received'] else 0
        jit = s['jit_sum'] / s['n_jit'] if s['n_jit'] else 0
        print(f'[player {pid}] recv={s["received"]} lost={s["lost"]} '
              f'loss={loss:.1f}% avg_latency={lat:.2f}ms jitter={jit:.2f}ms', flush=True)
    log.flush()


while True:
    try:
        data, addr = sock.recvfrom(1024)
    except socket.timeout:
        data = None

    if data and len(data) == FMT_SIZE:
        pid, seq, ts, x, y = struct.unpack(FMT, data)
        now = time.time()
        lat = (now - ts) * 1000
        s = stats.setdefault(pid, dict(last_seq=0, received=0, lost=0, lat_sum=0.0,
                                       jit_sum=0.0, last_lat=None, n_jit=0))
        if seq > s['last_seq']:
            if s['last_seq'] and seq > s['last_seq'] + 1:
                s['lost'] += seq - s['last_seq'] - 1
            s['last_seq'] = seq
        s['received'] += 1
        s['lat_sum'] += lat
        if s['last_lat'] is not None:
            s['jit_sum'] += abs(lat - s['last_lat'])
            s['n_jit'] += 1
        s['last_lat'] = lat
        log.write(f'{now:.3f},{pid},{seq},{lat:.3f}\n')
        players[pid] = (addr, x, y)
        broadcast()

    if time.time() >= next_report:
        report()
        next_report = time.time() + REPORT_EVERY
