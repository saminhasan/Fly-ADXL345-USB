import serial
import time

# ==== Config ====
PORT = 'COM21'  # Change as needed
BAUD = 115200

# ==== Runtime ====
last_mcu_time = None

try:
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        print(f"Connected to {PORT} at {BAUD} baud\n")
        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.startswith('|'):
                try:
                    # Remove leading pipe and split values
                    parts = line.strip('|').split(',')
                    if len(parts) != 4:
                        continue  # skip malformed lines

                    mcu_time_ms = int(parts[0].strip())
                    ax = float(parts[1].strip())
                    ay = float(parts[2].strip())
                    az = float(parts[3].strip())

                    # Compute MCU-side dt
                    if last_mcu_time is not None:
                        dt = (mcu_time_ms - last_mcu_time) / 1000
                    else:
                        dt = 0
                    last_mcu_time = mcu_time_ms

                    # Wall clock timestamp
                    host_time = time.strftime("%H:%M:%S", time.localtime())
                    print(f"[{host_time}] dt={dt:.3f}s  ax={ax:.6f}  ay={ay:.6f}  az={az:.6f}")
                except ValueError:
                    continue  # skip parsing errors
except KeyboardInterrupt:
    print("\nStopped by user.")
except Exception as e:
    print("ERROR:", e)
