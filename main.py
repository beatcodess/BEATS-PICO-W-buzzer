import network
import socket
from machine import Pin, PWM
import utime
import ure

# Buzzer setup
buzzer = PWM(Pin(15))
buzzer.duty_u16(0)

# WiFi credentials
ssid = 'wifi name'
password = 'password'

print("Connecting to WiFi...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

while not wlan.isconnected():
    utime.sleep(1)

print('WiFi connected:', wlan.ifconfig())

# Play tone instantly (non-blocking)
def play_tone(freq):
    buzzer.freq(freq)
    buzzer.duty_u16(30000)

# Stop buzzer
def stop_tone():
    buzzer.duty_u16(0)

# HTML page
html = """<!DOCTYPE html>
<html>
<head>
    <title>BEATS PICO W</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { background: #000; color: #a0f; font-family: 'Courier New', monospace; }
        .card { margin: 20px; padding: 20px; border: 1px solid #a0f; box-shadow: 0 0 10px #a0f; }
        button { background: #111; color: #a0f; border: 1px solid #a0f; padding: 10px; margin: 5px; width: 100%; cursor: pointer; }
        button:hover { background: #a0f; color: #000; }
    </style>
</head>
<body>
    <div class="card">
        <h1>BEATS PICO W v1.0</h1>
        <h3>BUZZER PRESETS</h3>
        <button onclick="play(440)">A4 (440Hz)</button>
        <button onclick="play(523)">C5 (523Hz)</button>
        <button onclick="play(659)">E5 (659Hz)</button>
        <button onclick="play(784)">G5 (784Hz)</button>
        <button onclick="stop()">TURN OFF</button>
        <script>
            function play(freq) {
                fetch('/?tone=' + freq);
            }
            function stop() {
                fetch('/?off=1');
            }
        </script>
    </div>
</body>
</html>
"""

# Start web server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
print("Web server running on port 80")

while True:
    cl, addr = s.accept()
    request = cl.recv(1024).decode()

    tone_match = ure.search(r"/\?tone=(\d+)", request)
    if tone_match:
        freq = int(tone_match.group(1))
        play_tone(freq)

    if "/?off=1" in request:
        stop_tone()

    # Respond with page for normal browser load
    if "GET / " in request or "GET /?" in request:
        cl.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n')
        cl.send(html)
    else:
        # Minimal OK for AJAX/fetch
        cl.send('HTTP/1.1 200 OK\r\n\r\n')

    cl.close()
