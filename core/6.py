from moteur import *

blocks = [
    floor(0, 330),
    floor(440, 700),
    floor(810, 1000),
    door(560, flee=(180, 200, 440, 1000, False)),
    spikes(860, 60, name="sp", visible=False),
]

traps = [
    trap((810, 0, 40, GROUND), [("show", "sp")]),
]

if __name__ == "__main__":
    play(6, (60, GROUND), blocks, traps)
