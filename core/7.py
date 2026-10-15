from moteur import *

blocks = [
    floor(0, 1000),
    fake_door(430),
    block(1000, 365, 60, 60, name="w"),
    ceiling_spikes(850, 60, name="cs"),
    door(930),
]

traps = [
    trap((600, 0, 40, GROUND), [("move", "w", -300, 0, 450)]),
    trap((800, 0, 40, GROUND), [("move", "cs", 0, 385, 700)]),
]

if __name__ == "__main__":
    play(7, (60, GROUND), blocks, traps)
