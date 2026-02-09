# Recycling Bindicator

A BBC micro:bit project that reminds you which bins to put out on collection day using LEDs.

## Hardware

- **BBC micro:bit**
- **Green LED** on pin0 — regular (general waste) bin
- **Yellow LED** on pin1 — recycling bin

The project assumes bins are collected weekly on **Thursday**, with recycling collected every other week.

## How It Works

### Startup Configuration

On boot the micro:bit displays a heart, then walks you through two setup prompts. Both use the same two-button interaction:

- **Button A** — cycle through options
- **Button B** — confirm your selection

**Step 1: "DAY?"** — Set the current day of the week. Press A to cycle through Mon, Tue, Wed, Thu, Fri, Sat, Sun. Press B to confirm.

**Step 2: "REC?"** — Set whether the *next* bin day includes recycling. Press A to toggle between Y (yes) and N (no). Press B to confirm.

### LED Behaviour

| Day       | Green LED          | Yellow LED (if recycling week) |
|-----------|--------------------|--------------------------------|
| Thursday  | Solid on           | Solid on                       |
| Wednesday | Breathing/pulsing  | Breathing/pulsing              |
| All other | Off                | Off                            |

- On **Thursday** (bin day), LEDs stay solid to remind you that today is collection day.
- On **Wednesday** (night before), LEDs pulse with a breathing effect as an advance reminder.
- On all other days, LEDs are off.

If it is not a recycling week, only the green LED activates on Wednesday/Thursday.

### Shake to Check

Shake the micro:bit at any time to check the next collection:

- **Green LED** turns on solid for 2 seconds (regular bin is always collected).
- If the next collection includes recycling, the **yellow LED flashes 5 times** during those 2 seconds.

### Day Rollover

The micro:bit tracks elapsed time internally. Every 24 hours it advances the day by one. When rolling past Thursday, it automatically toggles the recycling flag for the following week.

> **Note:** Since the micro:bit has no real-time clock, the day counter drifts if the device is reset or loses power. Simply re-run the startup configuration after a reset.

## Flashing

Copy `recycling-bindicator.py` to your micro:bit using your preferred method (e.g. the [micro:bit Python Editor](https://python.microbit.org/), Mu Editor, or `uflash`).
