import bpy
import os, sys

from Sun_Power.utils import *


def test_calc_power_lost():
    S = 120
    S_house = 120
    S_floor = 55
    radius = 4
    temp_in_start = 20
    temp_out = -15
    dT = 35
    Kt = 0.04
    N_lost_el = calc_power_lost_heat_el(S, dT, Kt)
    
    N_lost = get_power_lost(S_house, S_floor, radius, temp_in_start, temp_out)
    print(N_lost_el)
    print(N_lost)
    
    
test_calc_power_lost()
