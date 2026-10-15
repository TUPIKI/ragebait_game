from moteur import *

blocks = [
    floor(0, 330),
    floor(440, 700),
    floor(700, 740, name="v"),
    floor(830, 1000),
    sodebo(170, name="sb"),
    block(540, 380, 60, 45),
    block(600, 335, 60, 90),
    ceiling_spikes(480, 40, name="cs"),
    door(920),
]

traps = [
    trap("sb", [("jump", 0.55), ("hide", "sb")]),
    trap((470, 0, 40, GROUND), [("move", "cs", 0, 385, 700)]),
    trap("v", [("solid", "v", False), ("hide", "v")], 0.3),
]

if __name__ == "__main__":
    play(8, (60, GROUND), blocks, traps)
