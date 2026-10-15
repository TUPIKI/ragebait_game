from moteur import *

blocks = [
    floor(0, 440),
    floor(540, 690),
    floor(790, 1000),
    can(230, name="c1"),
    can(600, name="c2"),
    spikes(850, 60, name="sp", visible=False),
    door(920),
]

traps = [
    trap("c1", [("flip",), ("hide", "c1")]),
    trap("c2", [("flip",), ("hide", "c2")]),
    trap((800, 0, 40, GROUND), [("show", "sp")]),
]

if __name__ == "__main__":
    play(5, (60, GROUND), blocks, traps)
