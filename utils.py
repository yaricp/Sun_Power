import bpy, colorsys
from math import cos, degrees
from mathutils import Vector    #,Matrix 

END = 2000.0
SPACE_POWER_ON_METER = 1353

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
    h = 1-((float(value) / END)*0.6+0.4)
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
    #print('AM = '+str(AM))
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
        print(k)
        d_sun_ang = round(degrees(sun_ang), 2)
        print(d_sun_ang)
        if degrees(sun_ang) <= k:
            print(v)
            kr = v
            continue
    refl_power = power*kr
    return refl_power
    
