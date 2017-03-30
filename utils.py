import os, sys
from datetime import datetime
import bpy, colorsys
from math import pi, sin, cos, degrees
from mathutils import Vector    #,Matrix 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


from . settings import *


def clamp(v,min,max):
    if v < min:
        return min
    if v > max:
        return max
    return v
    
    
def get_ortho(a,b,c):
    if c != 0.0 and -a != b:
        return [-b-c, a,a]
    else:
        return [c,c,-a-b]
        
        
def make_new_material(obj, color):
    mat = bpy.data.materials.new(obj.name+'_mat')
    mat.diffuse_color = color
    return mat
    

def set_color(obj, value):
    color = get_color_by_value(value)
    if obj.active_material:
        obj.active_material.diffuse_color = color
    else:
        mat = make_new_material(obj, color)
        obj.active_material = mat
    
        
def get_color_by_value(value):
    h = 1-((float(value) / MAX_POWER_FACE)*0.6+0.4)
    s = 1.0
    v = 1.0
    (r, g, b) = colorsys.hsv_to_rgb(h, s, v)
    return (round(r, 2), round(g, 2), round(b, 2))
    
    
def calc_power_sun(sun_vec):
    ''' calculation made by this article:
    http://ust.su/solar/media/section-inner12/637/'''
    
    sun_ang = sun_vec.angle(Vector((0, 0, 1)))
    q = sun_ang
    AM = 1/(cos(q)+0.50572*(96.07995-q)**-1.6364)
    if AM < 0:
        return 0
    power = round(SPACE_POWER_ON_METER*(0.7**(AM**0.678)), 2) 
    return power
    

def calc_reflect_power(power, sun_ang, cover_material='polycarbonat'):
    ''' power of reflection: https://majetok.blogspot.ru/2014/05/vid-na-teplicu.html'''
#    dict_kr_mat = {'polycarbonat':1.585, 
#                  'glass':1.4}
#    dict_ki_mat = {'polycarbonat':0.82, 
#                    'glass':0.86}
    table_kr_mat = {'polycarbonat':{40:0.04, 
                                    50:0.06, 
                                    60:0.1, 
                                    70:0.18, 
                                    80:0.4, 
                                    90:1}, 
                    }
    kr = 1
    for k, v in table_kr_mat[cover_material].items():
        d_sun_ang = round(degrees(sun_ang), 2)
        if degrees(sun_ang) <= k:
            kr = v
            continue
    refl_power = power*kr
    return refl_power
    

def calc_area_of_lost_heat(radius):
    
    S_circle = math.pi*radius**2
    S = (4*math.pi*radius**2)/2 + S_circle
    return S
    

def get_mass_heat_kepper(radius): 
    
    radius_out = radius - AIR_GAP
    radius_in  = radius_out - THIK_WALL
    Vout = (4/3)*pi*(radius_out**3)
    Vin = (4/3)*pi*(radius_in**3)
    S_floor = pi*radius_in**2
    V_floor = S_floor*THIK_WALL
    V = (Vout - Vin)/2 + V_floor
    Mass = V * RO_MAT
    return Mass
    
    
def calc_power_lost_heat_el(S, dT, Kt):
    #http://infobos.ru/str/916.html
    #a_in = 8.7
    R_in = 1/8.7
    #a_out = 23
    R_out = 1/23
    R_mat = THIK_COVER/Kt
    N_lost = (dT/(R_in+R_out+R_mat))*S
    return N_lost
    
    
def get_power_lost(S_house, S_floor, radius, temp_in_start, temp_out):
    
    dT_house = temp_out - temp_in_start
    dT_floor = T_UNDER_FLOOR - temp_in_start
    N_lost_house = calc_power_lost_heat_el(S_house, dT_house, Kt)
    N_lost_floor = calc_power_lost_heat_el(S_floor, dT_floor, Kt)
    N_lost = N_lost_house + N_lost_floor
    return N_lost
    
    
def calc_temp_in(N_lost, time_tick, power_out_heat, power_in_heat, 
                radius, temp_in_start, Mass=None):
    N_res = N_lost + power_out_heat + power_in_heat
    #################
    #Q=m*c*(Т2-Т1)  #
    #Q = N_lost*t   #
    #(T2-T1)=Q/(m*c)#
    #T2 = T1+Q/(m*c)#
    #################
    if not Mass:
        Mass = get_mass_heat_kepper(radius)

    temp_in_end = temp_in_start + N_res*time_tick/(Mass*C_MAT)
    return temp_in_end
    

def get_obj_radius(Sun):
    obj = bpy.context.scene.objects.get(Sun.PowerShowObject)
    return obj.data.vertices[0].co.magnitude
    utils.py
    

def calc_obj_areas(Sun):
    obj = bpy.context.scene.objects.get(Sun.PowerShowObject)
    area_list = []
    for poly in obj.data.polygons:
        area_list.append(poly.area)
    #floor_area = max(area_list)
    #area_list.remove(floor_area)
    total_area = sum(area_list)
    return total_area
    

def calc_sun_power_on_faces(sun_vec, obj, efficiency, effective_angle):
    obj = bpy.context.scene.objects.get(obj)
    sun_powers = []
    sun_angles_dict = {}
    total_power = 0.0
    sun_power = 0.0
    count_faces = 0
    index_max_power_face = 0
    max_power = 0
    for poly in obj.data.polygons:
        text_name = 'sun_'+obj.name+'_text_'+str(poly.index).replace('.', '_')
        sun_ang = sun_vec.angle(obj.matrix_world * poly.normal)
        sun_power = calc_power_sun(sun_vec)*poly.area*cos(sun_ang)
        sun_power = sun_power - calc_reflect_power(sun_power, sun_ang)
        sun_power = sun_power * (efficiency/100)
        if (sun_power > 0 and 
            sun_vec.z > 0 and 
            sun_ang < effective_angle):
            count_faces += 1
            total_power += sun_power
            sun_powers.append(round(sun_power, 2))
            sun_angles_dict.update({round(sun_power, 2):(poly.index,degrees(sun_ang),
                                            round(sun_power, 2))})
            #print((poly.index,degrees(sun_ang),sun_power))
            value = str(round(sun_power,2))
        else:
            value = 0
        text_obj = bpy.data.objects[text_name]
        text_obj.data.body = '('+str(poly.index)+') '+str(value)
        set_color(text_obj, value)
        bpy.context.scene.update()
    if sun_angles_dict and sun_powers:
        max_power = max(sun_powers)
        index_max_power_face = sun_angles_dict[max_power][0]  
    return (max_power, index_max_power_face, count_faces, total_power)
    

def  calc_sun_power_on_hour(Sun, date, hour):
    from . sun_calc import getSunPosition, radToDeg
    day = date.day
    month = date.month
    year = date.year
    total_power_day = 0
    distance = Sun.SunDistance
    power_list = []
    if Sun.Longitude > 0:
        zone = Sun.UTCzone * -1
    else:
        zone = Sun.UTCzone
    if Sun.DaylightSavings:
        zone -= 1
    northOffset = radToDeg(Sun.NorthOffset)
    localTime = hour
    getSunPosition(None, localTime, Sun.Latitude, Sun.Longitude,
            northOffset, zone, month, day, year,
            distance)
    locX = sin(Sun.Phi) * sin(-Sun.Theta) * distance
    locY = sin(Sun.Theta) * cos(Sun.Phi) * distance
    locZ = cos(Sun.Theta) * distance
    location = Vector((locX, locY, locZ))
    (max_power,index_max_power_face,
    count_faces, total_power) = calc_sun_power_on_faces(location, 
                                                            Sun.PowerShowObject, 
                                                            Sun.Efficiency, 
                                                            Sun.EffectiveAngle)
    return total_power

    
def calc_sun_power_on_day(Sun, date):
    
    for hour in range(0, 24):
        total_power = calc_sun_power_on_hour(Sun, date, hour)
        total_power_day += total_power
        power_list.append(total_power)
    print('max power in day = '+str(max(power_list)))
    power_day = total_power_day/24
    print('power on day = '+str(power_day))
    #sys.exit(0)
    return power_day
    
    
def calc_table(Sun):
    x_list = []
    temp_out_list = []
    temp_in_start_list = []
    sun_day_power_list = []
    max_day_power_list = []
    lost_power_day_list = []
    #max_lost_power_day_list = []
    time_tick = Sun.TimeTick    #1 hours
    temp_in_start = Sun.StartTempInside
    power_in_heat = Sun.PowerHeatInside
    Mass = Sun.ExtMassInside
    path = os.path.dirname(os.path.realpath(__file__))
    count_x = 0
    with open(Sun.FileTempOutSide,'r') as file_in:
        for line in file_in.readlines():
            count_x+=1
            with open(Sun.ExportThermoResultsFile, 'a') as file_out:
                cols = line.split(',')
                if len(cols)>4:
                    if '−' in cols[3]:
                        znak = -1
                    else:
                        znak = 1
                    temp_out = float(cols[3].replace('°C', '').replace('−', ''))*znak
                    date_str = cols[1]
                    walls_total_area = calc_obj_areas(Sun)
                    date = datetime.strptime(date_str, "%m/%d/%y")
                    radius = get_obj_radius(Sun)
                    floor_area = pi*radius**2
                    print('date = '+date_str)
                    x_list.append(count_x)
                    file_out.write(date_str+';')
                    print('temp_out = '+str(temp_out))
                    temp_out_list.append(temp_out)
                    file_out.write(str(temp_out)+';')
                    print('temp_in start of day = '+str(temp_in_start))
                    file_out.write(str(temp_in_start)+';')
                    tot_day_power = 0
                    #power_lost_dict = []
                    sun_day_power_hours_list = []
                    lost_day_power_hours_list = []
                    for hour in range(0, 24):
                        power_out_heat = calc_sun_power_on_hour(Sun, date, hour)
                        #power_out_heat = 0
                        N_lost = get_power_lost(walls_total_area, floor_area, 
                                                radius, temp_in_start, 
                                                temp_out) 
                        lost_day_power_hours_list.append(N_lost)
                        temp_in_end = calc_temp_in(N_lost, time_tick, 
                                                    power_out_heat, 
                                                    power_in_heat, radius, 
                                                    temp_in_start, Mass)
                        temp_in_start = temp_in_end
                        sun_day_power_hours_list.append(power_out_heat)
                        
                    lost_day_power = sum(lost_day_power_hours_list)/24
                    lost_power_day_list.append(round(lost_day_power, 2)/1000)
                    temp_in_start_list.append(temp_in_start)
                    sun_day_power = sum(sun_day_power_hours_list)/24
                    sun_day_power_list.append(round(sun_day_power, 2)/1000)
                    max_day_power = max(sun_day_power_hours_list)
                    max_day_power_list.append(round(max_day_power, 2)/1000)
                    #lost_power_day = sum(power_lost_dict)/24
                    
                    #max_lost_power_day = max(power_lost_dict)
                    #max_lost_power_day_list.append(max_lost_power_day)
                    print('day_power of day = '+str(round(sun_day_power, 2)/1000))
                    file_out.write(str(round(sun_day_power, 2)/1000)+';')
                    print('max_day_power of day = '+str(round(max_day_power, 2)/1000))
                    file_out.write(str(round(max_day_power, 2)/1000)+';')
                    print('lost power of day = '+str(round(N_lost, 2)/1000))
                    file_out.write(str(round(N_lost, 2)/1000)+';')
                    #print('max lost power of day = '+str(max_lost_power_day))
                    #file_out.write(str(max_lost_power_day)+';')
                    print('temp_in end of day = '+str(temp_in_end))
                    file_out.write(str(temp_in_end)+';')
                file_out.write('\n')
                
    data = [x_list, {'label':'Temp out', 'data':temp_out_list}, 
                    {'label':'Temp inside', 'data':temp_in_start_list}, 
                    {'label':'Sun Power of day', 'data':sun_day_power_list},
                    {'label':'Heat loss', 'data': lost_power_day_list}]
    create_graph(data)
    
    
def create_graph(data):
    name_fig = str(datetime.now())
    fig1 = plt.figure()
    x_series = data.pop(0)
    for y_series in data:
        plt.plot(x_series, y_series['data'], label=y_series['label'])
    plt.xlabel('date')
    plt.legend()
    plt.title('Sun Power')
    plt.savefig(name_fig+'.png', dpi=200)
    #plt.show()
                
                
                
