import machine
import utime
import ustruct

# ==== Register Addresses ====
REG_DEVID       = 0x00
REG_POWER_CTL   = 0x2D
REG_DATA_FORMAT = 0x31
REG_DATAX0      = 0x32

# ==== Constants ====
DEVID  = 0xE5
SCALE  = 9.80665 / 256  # m/s^2 per LSB in full-res mode (256 LSB/g)

# ==== SPI and Chip Select Setup ====
cs = machine.Pin(9, machine.Pin.OUT, value=1)
spi = machine.SPI(1,
                  baudrate=1_000_000,
                  polarity=1,
                  phase=1,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(10),
                  mosi=machine.Pin(11),
                  miso=machine.Pin(12))

# ==== SPI Register Helpers ====
def reg_write(reg, val):
    cs.value(0)
    spi.write(bytearray([reg & 0x3F, val]))
    cs.value(1)

def reg_read(reg, n=1):
    if n <= 0:
        return b''
    cmd = 0x80 | (0x40 if n > 1 else 0) | (reg & 0x3F)
    cs.value(0)
    spi.write(bytearray([cmd]))
    val = spi.read(n)
    cs.value(1)
    return val

# ==== Failsafe / Safe Exit ====
def escape_to_safety(err=None):
    try:
        timer.deinit()
    except:
        pass
    cs.value(1)
    if err:
        print("SAFE STATE: Error ->", err)
    raise err if err else RuntimeError("Unknown failure")

# ==== Sensor Init ====
try:
    if reg_read(REG_DEVID)[0] != DEVID:
        raise RuntimeError("ADXL343 not detected")

    reg_write(REG_DATA_FORMAT, 0x0A)  # ±8g, full res
    reg_write(REG_POWER_CTL, reg_read(REG_POWER_CTL)[0] | 0x08)  # Measure mode
    utime.sleep(0.1)

except Exception as e:
    escape_to_safety(e)

# ==== Periodic Read Function ====
def read_accel(timer):
    try:
        now_ms = utime.ticks_ms()
        raw = reg_read(REG_DATAX0, 6)
        x, y, z = ustruct.unpack('<hhh', raw)
        ax, ay, az = (v * SCALE for v in (x, y, z))
        print("|%d, %.6f, %.6f, %.6f" % (now_ms, ax, ay, az))
    except Exception as e:
        escape_to_safety(e)


# ==== Start Timer at 10 Hz ====
timer = machine.Timer()
timer.init(freq=100, mode=machine.Timer.PERIODIC, callback=read_accel)
