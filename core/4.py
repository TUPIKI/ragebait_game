from moteur import *

blocks = [
    floor(0, 250),
    block(290, 380, 90, 20, name="s1"),
    block(450, 335, 90, 20, name="s2"),
    block(610, 380, 90, 20, name="s3"),
    floor(780, 1000),
    spikes(830, 50, name="sp", visible=False),
    door(915),
]

traps = [
    trap("s1", [("solid", "s1", False), ("hide", "s1")], 0.35),
    trap("s2", [("move", "s2", 0, 300, 500)], 0.4),
    trap("s3", [("move", "s3", -70, 0, 150)]),
    trap((720, 250, 50, 175), [("show", "sp")]),
]

if __name__ == "__main__":
    play(4, (60, GROUND), blocks, traps)
