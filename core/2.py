from moteur import *

blocks = [
    floor(0, 280),
    floor(280, 420, name="f"),
    floor(420, 1000),
    block(720, 0, 60, 60, name="drop"),
    door(910),
]

traps = [
    trap((330, 300, 60, 125), [("solid", "f", False), ("hide", "f")], 0.1),
    trap((620, 0, 60, GROUND), [("move", "drop", 0, 365, 900)]),
]

if __name__ == "__main__":
    play(2, (60, GROUND), blocks, traps)
