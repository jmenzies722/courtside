"""The win-probability model must behave like basketball."""
from winprob import home_win_probability as wp, seconds_left


def test_tip_off_slightly_favors_home():
    assert 0.55 < wp(0, 0, 1, "12:00") < 0.6          # home edge only


def test_same_lead_matters_more_late():
    assert wp(5, 0, 4, "0:10") > wp(5, 0, 4, "10:00") > wp(5, 0, 1, "12:00")


def test_final_buzzer_is_certain():
    assert wp(100, 98, 4, "0.0") == 1.0 and wp(98, 100, 4, "0.0") == 0.0


def test_clock_formats():
    assert seconds_left(4, "2:31") == 151 and seconds_left(4, "45.2") == 45.2
    assert seconds_left(1, "12:00") == 2880
