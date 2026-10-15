from moteur import *

blocks = [
    floor(0, 190),
    block(130, 265, 40, 160, solid=False),
    can(100, name="c1"),
    floor(290, 430, name="a"),
    ceiling_spikes(330, 60, name="cs1"),
    floor(530, 730),
    block(580, 365, 40, 60, name="inv", visible=False),
    fake_door(650),
    floor(830, 1000),
    sodebo(840, name="sb"),
    spikes(905, 35, name="sp", visible=False),
    block(1000, 365, 60, 60, name="w"),
    door(944, flee=(200, 340, 540, 1000, True)),
]

traps = [
    trap("c1", [("flip",), ("hide", "c1")]),
    trap("a", [("solid", "a", False), ("hide", "a")], 0.45),
    trap((310, 0, 40, GROUND), [("move", "cs1", 0, 385, 600)]),
    trap("inv", [("show", "inv")]),
    trap("sb", [("jump", 0.4), ("hide", "sb")]),
    trap((870, 0, 30, GROUND), [("show", "sp"), ("move", "w", -120, 0, 300)]),
]

if __name__ == "__main__":
    play(10, (60, GROUND), blocks, traps)
