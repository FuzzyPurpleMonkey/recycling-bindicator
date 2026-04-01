from microbit import *
import utime
import math

# LED pins
GREEN = pin0  # Regular bin (every Thursday)
YELLOW = pin1  # Recycle bin (every other Thursday)

# Day constants
WEDNESDAY = 2
THURSDAY = 3
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def configure_day():
    """Let user pick current day of week using buttons.
    Button A = cycle to next day, Button B = confirm selection.
    Returns 0=Mon .. 6=Sun.
    """
    display.scroll("DAY?")
    day = 0

    while True:
        display.scroll(DAY_NAMES[day])

        while True:
            a = button_a.is_pressed()
            b = button_b.is_pressed()

            if a:
                day = (day + 1) % 7
                sleep(300)
                break
            if b:
                sleep(500)
                return day

            sleep(50)


def configure_recycle():
    """Ask if next bin day is a recycle day.
    Button A = toggle Y/N, Button B = confirm selection.
    Returns bool.
    """
    display.scroll("REC?")
    choice = True

    while True:
        display.show("Y" if choice else "N")

        while True:
            a = button_a.is_pressed()
            b = button_b.is_pressed()

            if a:
                choice = not choice
                sleep(300)
                break
            if b:
                sleep(500)
                return choice

            sleep(50)


def leds_off():
    GREEN.write_digital(0)
    YELLOW.write_digital(0)


def pulse_value(t):
    """Return 0-1023 analog value for a breathing effect.
    t is time in ms, full cycle ~3 seconds.
    """
    angle = (t % 3000) / 3000.0 * 2 * math.pi
    val = (math.sin(angle - math.pi / 2) + 1) / 2
    return int(val * 1023)


def flash_led(pin, times=3):
    """Flash a single LED pin a given number of times."""
    for _ in range(times):
        pin.write_digital(1)
        sleep(200)
        pin.write_digital(0)
        sleep(200)


STATE_FILE = "state.txt"


def save_state(current_day, next_is_recycle):
    try:
        with open(STATE_FILE, "w") as f:
            f.write("d={}\n".format(current_day))
            f.write("r={}\n".format(1 if next_is_recycle else 0))
    except:
        pass


def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            lines = f.read().split("\n")
        d = None
        r = None
        for line in lines:
            if line.startswith("d="):
                d = int(line[2:])
            elif line.startswith("r="):
                r = bool(int(line[2:]))
        if d is not None and r is not None and 0 <= d <= 6:
            return (d, r)
    except:
        pass
    return None


def handle_shake(next_is_recycle):
    """On shake: green on solid, flash yellow 5x if next is recycle."""
    GREEN.write_digital(1)

    if next_is_recycle:
        for _ in range(5):
            YELLOW.write_digital(1)
            sleep(200)
            YELLOW.write_digital(0)
            sleep(200)
    else:
        sleep(2000)

    GREEN.write_digital(0)


# --- Startup ---
leds_off()
display.show(Image.HEART)
sleep(1000)

# Hold Button A during heart display to force full reconfigure
force_reconfigure = button_a.is_pressed()
saved = None if force_reconfigure else load_state()

if saved is not None:
    current_day, next_is_recycle = saved
    display.scroll("OK " + DAY_NAMES[current_day] + " " + ("REC" if next_is_recycle else "NO REC"))
else:
    current_day = configure_day()
    next_is_recycle = configure_recycle()
    save_state(current_day, next_is_recycle)

display.clear()

# Track time for day rollover (always reset to now on boot)
last_day_change = utime.ticks_ms()
last_shake_ms = utime.ticks_add(utime.ticks_ms(), -10000)  # far in the past

# --- Main loop ---
while True:
    # Day rollover check
    now = utime.ticks_ms()
    elapsed = utime.ticks_diff(now, last_day_change)
    day_changed = False
    while elapsed >= 86400000:  # 24 hours in ms
        last_day_change = utime.ticks_add(last_day_change, 86400000)
        elapsed -= 86400000
        old_day = current_day
        current_day = (current_day + 1) % 7
        # Toggle recycle flag when rolling past Thursday
        if old_day == THURSDAY:
            next_is_recycle = not next_is_recycle
        day_changed = True
    if day_changed:
        save_state(current_day, next_is_recycle)

    # Button presses
    if button_a.was_pressed():
        # Advance day by one (drift correction)
        old_day = current_day
        current_day = (current_day + 1) % 7
        if old_day == THURSDAY:
            next_is_recycle = not next_is_recycle
        last_day_change = utime.ticks_ms()
        save_state(current_day, next_is_recycle)
        flash_led(GREEN, 1)
        continue
    if button_b.was_pressed():
        # Toggle recycle week (phase correction)
        next_is_recycle = not next_is_recycle
        save_state(current_day, next_is_recycle)
        flash_led(YELLOW, 1)
        continue

    # Shake detection (5 second cooldown to suppress phantom shakes from vibration)
    if accelerometer.was_gesture("shake"):
        if utime.ticks_diff(utime.ticks_ms(), last_shake_ms) >= 5000:
            handle_shake(next_is_recycle)
            last_shake_ms = utime.ticks_ms()
        continue

    # LED behavior based on current day
    if current_day in (WEDNESDAY, THURSDAY):
        pv = pulse_value(utime.ticks_ms())
        GREEN.write_analog(pv)
        if next_is_recycle:
            YELLOW.write_analog(min(int(pv * 1.5), 1023))
        else:
            YELLOW.write_digital(0)
        sleep(20)

    else:
        leds_off()
        sleep(100)
