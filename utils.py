import bpy, colorsys

END = 2000.0

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
