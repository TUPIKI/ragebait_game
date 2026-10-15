from moteur import *

blocks = [
    floor(0, 1000),
    block(380, 265, 40, 160, solid=False),
    block(570, 365, 40, 60, name="inv", visible=False),
    spikes(760, 100, name="p", visible=False),
    door(925),
]

traps = [
    trap("inv", [("show", "inv")]),
    trap((700, 0, 40, GROUND), [("show", "p")]),
]

if __name__ == "__main__":
    play(3, (60, GROUND), blocks, traps)
