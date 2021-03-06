import bpy
import bmesh
import math
from math import degrees, cos, radians
from mathutils import Vector 

from . utils import * #clamp, calc_sun_power_on_faces, calc_table


class DisplayAction:
    ENABLE = True
    PANEL = False
    PREFERENCES = False

    def __init__(self):
        self.invert_zoom_wheel = False
        self.invert_mouse_zoom = False

    def setAction(self, VAL):
        if VAL == 'ENABLE':
            self.ENABLE = True
            self.PANEL = self.PREFERENCES = False
        elif VAL == 'PANEL':
            self.PANEL = True
            self.ENABLE = self.PREFERENCES = False
        else:
            self.PREFERENCES = True
            self.ENABLE = self.PANEL = False

    def refresh(self):
        # Touching the cursor forces a screen refresh
        bpy.context.scene.cursor_location.x += 0.0


Display = DisplayAction()
Display.setAction('ENABLE')

############################################################################
# SunClass is used for storing and comparing changes in panel values
# as well as general traffic direction.
############################################################################


class SunClass:

    class TazEl:
        time = 0.0
        azimuth = 0.0
        elevation = 0.0

    class CLAMP:
        tex_location = None
        elevation = 0.0
        azimuth = 0.0
        azStart = 0.0
        azDiff = 0.0

    Sunrise = TazEl()
    Sunset = TazEl()
    SolarNoon = TazEl()
    RiseSetOK = False

    Bind = CLAMP()
    BindToSun = False
    PlaceLabel = "Time & Place"
    PanelLabel = "Panel Location"
    MapName = "WorldMapLR.jpg"
    MapLocation = 'VIEWPORT'

    Latitude = 0.0
    Longitude = 0.0
    Elevation = 0.0
    Azimuth = 0.0
    AzNorth = 0.0
    Phi = 0.0
    Theta = 0.0
    LX = 0.0
    LY = 0.0
    LZ = 0.0

    Month = 0
    Day = 0
    Year = 0
    Day_of_year = 0
    Time = 0.0

    UTCzone = 0
    SunDistance = 0.0
    TimeSpread = 23.50
    UseDayMonth = True
    DaylightSavings = False
    ShowRiseSet = True
    ShowRefraction = True
    NorthOffset = 0.0
    
    TotalPower = 0.0
    CountFaces = 0
    IndexFaceMaxPower = 0
    FaceMaxPower = 0.0
    
    Efficiency = 90
    EffectiveAngle = 65.0

    UseSunObject = False
    SunObject = "Sun"
    PowerShowObject = "Icosphere" 
    SizeSunPowerObject = 4
    
    ExportThermoResultsFile = ""
    FileTempOutSide = ""
    TimeTick = 3600
    ExportDayFrom = 0
    ExportDayTo = 0
    ExportMonthFrom = 0
    ExportMonthTo = 0
    ExportYearFrom = 0
    ExportYearTo = 0
    ListWorkFaces = ''
    StartTempInside = 20.0
    PowerHeatInside = 0.0
    ExtMassInside = 0.0

    UseSkyTexture = False
    SkyTexture = "Sky Texture"
    HDR_texture = "Environment Texture"

    UseObjectGroup = False
    ObjectGroup = 'ECLIPTIC'
    Selected_objects = []
    Selected_names = []
    ObjectGroup_verified = False
    PowerObject_verified = False
    PowerObjectLabels_created = False

    PreBlend_handler = None
    Frame_handler = None
    SP = None
    PP = None
    Counter = 0

    # ----------------------------------------------------------------------
    # There are times when the object group needs to be deleted such as
    # when opening a new file or when objects might be deleted that are
    # part of the group. If such is the case, delete the object group.
    # ----------------------------------------------------------------------

    def verify_ObjectGroup(self):
        if not self.ObjectGroup_verified:
            if len(self.Selected_names) > 0:
                names = [x.name for x in bpy.data.objects]
                for x in self.Selected_names:
                    if not x in names:
                        del self.Selected_objects[:]
                        del self.Selected_names[:]
                        break
            self.ObjectGroup_verified = True
            
    def check_power_obj(self, obj_name):
        obj = bpy.context.scene.objects.get(obj_name)
        if 'polygons' in str(dir(obj.data)):
            Sun.PowerObject_verified = True
            
    def get_max_vert(self, obj):
        list = []
        for b in obj.bound_box:
            for v in b:
                list.append(v)
        return max(list)-1
        
    def create_total_labels(self):
        obj = bpy.context.scene.objects.get(self.PowerShowObject)
        max_co = self.get_max_vert(obj)
        bpy.ops.object.text_add(location=(max_co,max_co,max_co))
        tot_power_label = bpy.context.object
        tot_power_label.data.body = "Total Power: 0"
        tot_power_label.name = 'sun_tot_power_label'
        tot_power_label.scale = (0.3,0.3,0.3)
        bpy.ops.object.text_add(location=(max_co,max_co,max_co+1.5))
        temp_in_label = bpy.context.object
        temp_in_label.data.body = "Temp IN: 0"
        temp_in_label.name = 'sun_temp_in_label'
        temp_in_label.scale = (0.3,0.3,0.3)
        bpy.ops.object.text_add(location=(max_co,max_co,max_co+0.5))
        face_power_label = bpy.context.object
        face_power_label.data.body = "Face power: 0"
        face_power_label.name = 'sun_face_power_label'
        face_power_label.scale = (0.3,0.3,0.3)
        bpy.ops.object.text_add(location=(max_co,max_co,max_co+1))
        count_face_label = bpy.context.object
        count_face_label.data.body = "Count work faces: 0"
        count_face_label.name = 'sun_count_face_label'
        count_face_label.scale = (0.3,0.3,0.3)
        tot_power_label.convert_space(from_space='WORLD', to_space='LOCAL')
        tot_power_label.rotation_mode = 'XYZ'
        tot_power_label.rotation_euler = (radians(90),0,0)
        face_power_label.convert_space(from_space='WORLD', to_space='LOCAL')
        face_power_label.rotation_mode = 'XYZ'
        face_power_label.rotation_euler = (radians(90),0,0)
        count_face_label.convert_space(from_space='WORLD', to_space='LOCAL')
        count_face_label.rotation_mode = 'XYZ'
        count_face_label.rotation_euler = (radians(90),0,0)
        temp_in_label.convert_space(from_space='WORLD', to_space='LOCAL')
        temp_in_label.rotation_mode = 'XYZ'
        temp_in_label.rotation_euler = (radians(90),0,0)
        bpy.context.scene.update()
        
    def create_power_labels(self):
        obj = bpy.context.scene.objects.get(self.PowerShowObject)
        self.create_total_labels()
        mat_world = obj.matrix_world
        cam = bpy.context.scene.objects['Camera']
        cam_center = cam.location
        for poly in obj.data.polygons:
            text_name = 'sun_'+obj.name+'_text_'+str(poly.index).replace('.', '_')
            bpy.ops.object.text_add(location=mat_world * Vector(poly.center))
            myFontOb = bpy.context.object
            myFontOb.data.body = "0"
            myFontOb.name = text_name
            myFontOb.data.align = 'CENTER'
            myFontOb.scale = (0.3,0.3,0.3)
            obj.rotation_mode = 'QUATERNION'
            cam_norm = obj.rotation_quaternion * poly.normal
            fnorm = Vector((-1,0,0))
            axis = fnorm.cross(cam_norm)
            dot = fnorm.normalized().dot(cam_norm.normalized())
            dot = clamp(dot, -1.0, 1.0)
            if axis.length < 1.0e-8:
                axis = Vector(get_ortho(fnorm.x, fnorm.y, fnorm.z))
            myFontOb.rotation_mode = 'AXIS_ANGLE'
            myFontOb.rotation_axis_angle = [math.acos(dot) + math.pi, 
                                            axis[0],
                                            axis[1],
                                            axis[2]]
            myFontOb.convert_space(from_space='WORLD', to_space='LOCAL')
            myFontOb.rotation_mode = 'XYZ'
            myFontOb.rotation_euler = (radians(90),
                                        0,
                                        myFontOb.rotation_euler[2]+radians(90))
            bpy.context.scene.update()
            self.PowerObjectLabels_created = True
    
    def delete_power_labels(self):
        for label in bpy.data.objects:
            if 'sun_' in label.name and label.type == 'FONT':
                label.select = True
                bpy.ops.object.delete()
        self.PowerObjectLabels_created = False
        
    def set_powers(self):
        SunObj = bpy.context.scene.objects.get(self.SunObject)
        sun_vec = SunObj.location
        (max_power,index_max_power_face,
        count_faces, total_power) = calc_sun_power_on_faces(sun_vec, 
                                                            self.PowerShowObject, 
                                                            self.Efficiency, 
                                                            self.EffectiveAngle)
        self.IndexFaceMaxPower = index_max_power_face 
        self.FaceMaxPower = max_power
        self.CountFaces = count_faces
        self.TotalPower = total_power
        tot_power_label = bpy.data.objects['sun_tot_power_label']
        tot_power_label.data.body = 'Total Power: '+str(round(self.TotalPower, 2))+' W'
        set_color(tot_power_label, max_power)
        face_power_label = bpy.data.objects['sun_face_power_label']
        face_power_label.data.body = 'Face power: '\
                                    +'('+str(self.IndexFaceMaxPower)+') '\
                                    +str(max_power)+' W'
        set_color(face_power_label, max_power)
        count_face_label = bpy.data.objects['sun_count_face_label']
        count_face_label.data.body = 'Count work faces: '+str(self.CountFaces)
        set_color(count_face_label, max_power)
        count_face_label = bpy.data.objects['sun_temp_in_label']
        count_face_label.data.body = 'Temp IN: '+str(self.CountFaces)
        set_color(count_face_label, max_power)
        bpy.context.scene.update()
        

Sun = SunClass()

############################################################################
# Sun panel properties
############################################################################


class SunPosSettings(bpy.types.PropertyGroup):

    from bpy.props import StringProperty, EnumProperty, \
                          IntProperty, FloatProperty

    IsActive = bpy.props.BoolProperty(
        description="True if panel enabled.",
        default=False)

    ShowMap = bpy.props.BoolProperty(
        description="Show world map.",
        default=False)

    DaylightSavings = bpy.props.BoolProperty(
        description="Daylight savings time adds 1 hour to standard time.",
        default=0)

    ShowRefraction = bpy.props.BoolProperty(
        description="Show apparent sun position due to refraction.",
        default=1)

    ShowNorth = bpy.props.BoolProperty(
        description="Draws line pointing north.",
        default=0)

    Latitude = FloatProperty(
        attr="",
        name="Latitude",
        description="Latitude: (+) Northern (-) Southern",
        soft_min=-90.000, soft_max=90.000, step=3.001,
        default=40.000, precision=3)

    Longitude = FloatProperty(
        attr="",
        name="Longitude",
        description="Longitude: (-) West of Greenwich  (+) East of Greenwich",
        soft_min=-180.000, soft_max=180.000,
        step=3.001, default=1.000, precision=3)

    Month = IntProperty(
        attr="",
        name="Month",
        description="",
        min=1, max=12, default=6)

    Day = IntProperty(
        attr="",
        name="Day",
        description="",
        min=1, max=31, default=21)

    Year = IntProperty(
        attr="",
        name="Year",
        description="",
        min=1800, max=4000, default=2012)

    Day_of_year = IntProperty(
        attr="",
        name="Day of year",
        description="",
        min=1, max=366, default=1)

    UTCzone = IntProperty(
        attr="",
        name="UTC zone",
        description="Time zone: Difference from Greenwich England in hours.",
        min=0, max=12, default=0)

    Time = FloatProperty(
        attr="",
        name="Time",
        description="",
        precision=4,
        soft_min=0.00, soft_max=23.9999, step=1.00, default=12.00)

    NorthOffset = FloatProperty(
        attr="",
        name="",
        description="North offset in degrees or radians "
                    "from scene's units settings",
        unit="ROTATION",
        soft_min=-3.14159265, soft_max=3.14159265, step=10.00, default=0.00)

    SunDistance = FloatProperty(
        attr="",
        name="Distance",
        description="Distance to sun from XYZ axes intersection.",
        unit="LENGTH",
        soft_min=1, soft_max=3000.00, step=10.00, default=50.00)

    UseSunObject = bpy.props.BoolProperty(
        description="Enable sun positioning of named lamp or mesh",
        default=False)
        
    ShowPowerOnObject = bpy.props.BoolProperty(
        description="Enable show power in faces of object",
        default=False)
        
    EffectiveAngle = FloatProperty(
        attr="",
        name="EffectiveAngle",
        description="Effective angle bettwen sun rays and normal of face for get power",
        unit="ROTATION",
        soft_min=-3.14159265, 
        soft_max=3.14159265, 
        step=10.00,
        default=radians(Sun.EffectiveAngle))
        
    Efficiency = FloatProperty(
        attr="",
        name="Efficiency",
        description="Efficiency %",
        unit="LENGTH",
        soft_min=0,
        soft_max=100.00,
        step=1.00,
        default=Sun.Efficiency)

    SunObject = StringProperty(
        default="Sun",
        name="theSun",
        description="Name of sun object")
        
    PowerShowObject = StringProperty(
        default="Icosphere",
        name="thePowerObject",
        description="Name of power object")

    UseSkyTexture = bpy.props.BoolProperty(
        description="Enable use of Cycles' "
                    "sky texture. World nodes must be enabled, "
                    "then set color to Sky Texture.",
        default=False)

    SkyTexture = StringProperty(
        default="Sky Texture",
        name="sunSky",
        description="Name of sky texture to be used")

    ShowHdr = bpy.props.BoolProperty(
        description="Click to set sun location on environment texture",
        default=False)

    HDR_texture = StringProperty(
        default="Environment Texture",
        name="envSky",
        description="Name of texture to use. World nodes must be enabled "
                    "and color set to Environment Texture")

    HDR_azimuth = FloatProperty(
        attr="",
        name="Rotation",
        description="Rotation angle of sun and environment texture "
                    "in degrees or radians from scene's units settings",
        unit="ROTATION",
        step=1.00, default=0.00, precision=3)

    HDR_elevation = FloatProperty(
        attr="",
        name="Elevation",
        description="Elevation angle of sun",
        step=3.001,
        default=0.000, precision=3)

    BindToSun = bpy.props.BoolProperty(
        description="If true, Environment texture moves with sun.",
        default=False)

    UseObjectGroup = bpy.props.BoolProperty(
        description="Allow a group of objects to be positioned.",
        default=False)

    TimeSpread = FloatProperty(
        attr="",
        name="Time Spread",
        description="Time period in which to spread object group",
        precision=4,
        soft_min=1.00, soft_max=24.00, step=1.00, default=23.00)

    ObjectGroup = EnumProperty(
        name="Display type",
        description="Show object group on ecliptic or as analemma",
        items=(
            ('ECLIPTIC', "On the Ecliptic", ""),
            ('ANALEMMA', "As and Analemma", ""),
            ),
        default='ECLIPTIC')

    Location = StringProperty(
        default="view3d",
        name="location",
        description="panel location")
        
    SizeSunPowerObject = FloatProperty(
        attr="",
        name="SizeSunPowerObject",
        description="Size of house",
        unit="LENGTH",
        soft_min=0,
        soft_max=100.00,
        step=1.00,
        default=Sun.SizeSunPowerObject)
        
    ExportThermoResultsFile = StringProperty(
        default=".config/blender/Exports/results.csv",
        subtype="FILE_PATH", 
        name="ExportThermoResultsFile", 
        description="Export data to file")
        
    FileTempOutSide = StringProperty(
        default=".config/blender/Exports/outside_temp.csv",
        subtype="FILE_PATH", 
        name="FileTempOutSide", 
        description="file temperature outside")
    
    TimeTick = IntProperty(
        attr="",
        name="TimeTick",
        description="Time period in which to make calculation lost power",
        min=300, max=31104000, default=3600)
        
    ExportMonthFrom = IntProperty(
        attr="",
        name="ExportMonthFrom",
        description="mouth export data",
        min=1, max=12, default=6)

    ExportDayFrom = IntProperty(
        attr="",
        name="ExportDayFrom",
        description="day export data from",
        min=1, max=31, default=21)

    ExportYearFrom = IntProperty(
        attr="",
        name="ExportYearFrom",
        description="export from year",
        min=1800, max=4000, default=2012)
        
    ExportMonthTo = IntProperty(
        attr="",
        name="ExportMonthTo",
        description="mouth export to",
        min=1, max=12, default=6)

    ExportDayTo = IntProperty(
        attr="",
        name="ExportDayTo",
        description="day export data to",
        min=1, max=31, default=21)

    ExportYearTo = IntProperty(
        attr="",
        name="ExportYearTo",
        description="export to year",
        min=1800, max=4000, default=2012)
        
    ListWorkFaces = StringProperty(
        default="",
        name="ListWorkFaces",
        description="list of work faces")
        
    StartTempInside = FloatProperty(
        attr="",
        name="StartTempInside",
        description="Start temperature inside",
        step=1.0,
        default=20.0, precision=1)
        
    PowerHeatInside = FloatProperty(
        attr="",
        name="PowerHeatInside",
        description="External power of heat inside",
        step=1.0,
        default=0.0, precision=1)
        
    ExtMassInside = FloatProperty(
        attr="",
        name="ExtMassInside",
        description="External mass inside",
        step=1.0,
        default=0.0, precision=1)


############################################################################
# Preference panel properties
############################################################################


class SunPosPreferences(bpy.types.PropertyGroup):
    from bpy.props import StringProperty, EnumProperty

    UsageMode = EnumProperty(
        name="Usage mode",
        description="operate in normal mode or environment texture mode",
        items=(
            ('NORMAL', "Normal", ""),
            ('HDR', "Sun + HDR texture", ""),
            ),
        default='NORMAL')

    MapLocation = EnumProperty(
        name="Map location",
        description="Display map in viewport or world panel",
        items=(
            ('VIEWPORT', "Viewport", ""),
            ('PANEL', "Panel", ""),
            ),
        default='VIEWPORT')

    UseOneColumn = bpy.props.BoolProperty(
        description="Set panel to use one column.",
        default=False)

    UseTimePlace = bpy.props.BoolProperty(
        description="Show time/place presets.",
        default=False)

    UseObjectGroup = bpy.props.BoolProperty(
        description="Use object group option.",
        default=True)

    ShowDMS = bpy.props.BoolProperty(
        description="Show lat/long degrees,minutes,seconds labels.",
        default=True)

    ShowNorth = bpy.props.BoolProperty(
        description="Show north offset choice and slider.",
        default=True)

    ShowRefraction = bpy.props.BoolProperty(
        description="Show sun refraction choice.",
        default=True)

    ShowAzEl = bpy.props.BoolProperty(
        description="Show azimuth and solar elevation info.",
        default=True)

    ShowDST = bpy.props.BoolProperty(
        description="Show daylight savings time choice.",
        default=True)

    ShowRiseSet = bpy.props.BoolProperty(
        description="Show sunrise and sunset.",
        default=True)

    MapName = StringProperty(
        default="WorldMap.jpg",
        name="WorldMap",
        description="Name of world map")
