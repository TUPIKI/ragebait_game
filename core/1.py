from moteur import *

blocks = [
    floor(0, 500),
    floor(620, 1000),
    spikes(770, 60, name="s", visible=False),
    door(900),
]

traps = [
    trap((660, 0, 40, GROUND), [("show", "s")]),
]

if __name__ == "__main__":
    play(1, (60, GROUND), blocks, traps)
