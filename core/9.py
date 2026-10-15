from moteur import *

blocks = [
    floor(0, 220),
    block(255, 385, 80, 20, name="p1"),
    block(390, 340, 80, 20, name="p2"),
    floor(520, 1000),
    can(560, name="c1"),
    block(630, 365, 40, 60, name="inv", visible=False),
    spikes(720, 60, name="sp", visible=False),
    ceiling_spikes(820, 60, name="cs"),
    fake_door(910, name="fd", deadly=False),
    door(130, name="real", visible=False),
]

traps = [
    trap("p1", [("solid", "p1", False), ("hide", "p1")], 0.3),
    trap("p2", [("move", "p2", 0, 300, 400)], 0.3),
    trap("c1", [("flip",), ("hide", "c1")]),
    trap("inv", [("show", "inv")]),
    trap((690, 0, 40, GROUND), [("show", "sp")]),
    trap((780, 0, 30, GROUND), [("move", "cs", 0, 385, 700)]),
    trap("fd", [("tp", 60, GROUND), ("show", "real")]),
]

if __name__ == "__main__":
    play(9, (60, GROUND), blocks, traps)
