import bpy
import datetime

from . properties import *
from . sun_calc import Move_sun
from . north import *
from . map import Map
from . hdr import Hdr

# ---------------------------------------------------------------------------


class ControlClass:

    region = None
    handler = None

    def callback(self, os, context):
        if Sun.SP.IsActive:
            if self.panel_changed():
                Move_sun()
        else:
            self.remove_handler()

    def activate(self, context):
        if context.area.type == 'PROPERTIES':
            if Display.ENABLE:
                Display.setAction('PANEL')
                Sun.SP.IsActive = True
                self.region = context.region
                self.add_handler(context)
                return {'RUNNING_MODAL'}
            else:
                Display.setAction('ENABLE')
                Sun.SP.IsActive = False
                Map.deactivate()
                Hdr.deactivate()
                return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Context not available")
            return {'CANCELLED'}

    def add_handler(self, context):
        self.handler = bpy.types.SpaceView3D.draw_handler_add(self.callback,
                              (self, context), 'WINDOW', 'POST_PIXEL')

    def remove_handler(self):
        if self.handler:
            bpy.types.SpaceView3D.draw_handler_remove(self.handler, 'WINDOW')
        self.handler = None

    def panel_changed(self):
        rv = False
        sp = Sun.SP

        if not Sun.UseDayMonth and sp.Day_of_year != Sun.Day_of_year:
            dt = (datetime.date(sp.Year, 1, 1) +
                 datetime.timedelta(sp.Day_of_year - 1))
            Sun.Day = dt.day
            Sun.Month = dt.month
            Sun.Day_of_year = sp.Day_of_year
            sp.Day = dt.day
            sp.Month = dt.month
            rv = True
        elif (sp.Day != Sun.Day or
            sp.Month != Sun.Month):
            try:
                dt = datetime.date(sp.Year, sp.Month, sp.Day)
                sp.Day_of_year = dt.timetuple().tm_yday
                Sun.Day = sp.Day
                Sun.Month = sp.Month
                Sun.Day_of_year = sp.Day_of_year
                rv = True
            except:
                pass

        if Sun.PP.UsageMode == "HDR":
            if sp.BindToSun != Sun.BindToSun:
                Sun.BindToSun = sp.BindToSun
                if Sun.BindToSun:
                    nt = bpy.context.scene.world.node_tree.nodes
                    envTex = nt.get(sp.HDR_texture)
                    if envTex:
                        if envTex.type == "TEX_ENVIRONMENT":
                            Sun.Bind.tex_location = envTex.texture_mapping.rotation
                            Sun.Bind.azStart = sp.HDR_azimuth
                            obj = bpy.context.scene.objects.get(Sun.SunObject)
                Sun.HDR_texture = sp.HDR_texture
                Sun.Elevation = sp.HDR_elevation
                Sun.Azimuth = sp.HDR_azimuth
                Sun.Bind.elevation = sp.HDR_elevation
                Sun.Bind.azimuth = sp.HDR_azimuth
                Sun.SunDistance = sp.SunDistance
                return True
            if (sp.HDR_elevation != Sun.Bind.elevation or
                sp.HDR_azimuth != Sun.Bind.azimuth or
                sp.SunDistance != Sun.SunDistance):
                Sun.Elevation = sp.HDR_elevation
                Sun.Azimuth = sp.HDR_azimuth
                Sun.Bind.elevation = sp.HDR_elevation
                Sun.Bind.azimuth = sp.HDR_azimuth
                Sun.SunDistance = sp.SunDistance
                return True
            return False

        if (rv or sp.Time != Sun.Time or
            sp.TimeSpread != Sun.TimeSpread or
            sp.SunDistance != Sun.SunDistance or
            sp.Latitude != Sun.Latitude or
            sp.Longitude != Sun.Longitude or
            sp.UTCzone != Sun.UTCzone or
            sp.Year != Sun.Year or
            sp.UseSkyTexture != Sun.UseSkyTexture or
            sp.SkyTexture != Sun.SkyTexture or
            sp.HDR_texture != Sun.HDR_texture or
            sp.UseSunObject != Sun.UseSunObject or
            sp.SunObject != Sun.SunObject or
            sp.PowerShowObject != Sun.PowerShowObject or
            sp.UseObjectGroup != Sun.UseObjectGroup or
            sp.ObjectGroup != Sun.ObjectGroup or
            sp.DaylightSavings != Sun.DaylightSavings or
            sp.ShowRefraction != Sun.ShowRefraction or
            sp.ShowNorth != Sun.ShowNorth or
            sp.NorthOffset != Sun.NorthOffset or
            sp.Efficiency != Sun.Efficiency or
            sp.EffectiveAngle != Sun.EffectiveAngle or
            sp.ExportThermoResultsFile != Sun.ExportThermoResultsFile or
            sp.FileTempOutSide != Sun.FileTempOutSide or
            sp.TimeTick != Sun.TimeTick or
            sp.ExportDayFrom != Sun.ExportDayFrom or
            sp.ExportDayTo != Sun.ExportDayTo or
            sp.ExportMonthFrom != Sun.ExportMonthFrom or
            sp.ExportMonthTo != Sun.ExportMonthTo or
            sp.ExportYearFrom != Sun.ExportYearFrom or
            sp.ExportYearTo != Sun.ExportYearTo or
            sp.SizeSunPowerObject != Sun.SizeSunPowerObject or
            sp.ListWorkFaces != Sun.ListWorkFaces or
            sp.StartTempInside != Sun.StartTempInside or
            sp.PowerHeatInside != Sun.PowerHeatInside or
            sp.ExtMassInside != Sun.ExtMassInside
            ):

            Sun.Time = sp.Time
            Sun.TimeSpread = sp.TimeSpread
            Sun.SunDistance = sp.SunDistance
            Sun.Latitude = sp.Latitude
            Sun.Longitude = sp.Longitude
            Sun.UTCzone = sp.UTCzone
            Sun.Year = sp.Year
            Sun.UseSkyTexture = sp.UseSkyTexture
            Sun.SkyTexture = sp.SkyTexture
            Sun.HDR_texture = sp.HDR_texture
            Sun.UseSunObject = sp.UseSunObject
            Sun.SunObject = sp.SunObject
            Sun.PowerShowObject = sp.PowerShowObject
            Sun.UseObjectGroup = sp.UseObjectGroup
            Sun.ObjectGroup = sp.ObjectGroup
            Sun.DaylightSavings = sp.DaylightSavings
            Sun.ShowRefraction = sp.ShowRefraction
            Sun.ShowNorth = sp.ShowNorth
            Sun.NorthOffset = sp.NorthOffset
            Sun.Efficiency = sp.Efficiency
            Sun.EffectiveAngle = sp.EffectiveAngle
            Sun.ExportThermoResultsFile = sp.ExportThermoResultsFile
            Sun.FileTempOutSide = sp.FileTempOutSide
            Sun.TimeTick = sp.TimeTick
            Sun.ExportDayFrom = sp.ExportDayFrom
            Sun.ExportDayTo = sp.ExportDayTo
            Sun.ExportMonthFrom = sp.ExportMonthFrom
            Sun.ExportMonthTo = sp.ExportMonthTo
            Sun.ExportYearFrom = sp.ExportYearFrom
            Sun.ExportYearTo = sp.ExportYearTo
            Sun.SizeSunPowerObject = sp.SizeSunPowerObject
            Sun.ListWorkFaces = sp.ListWorkFaces
            Sun.StartTempInside = sp.StartTempInside
            Sun.PowerHeatInside = sp.PowerHeatInside
            Sun.ExtMassInside = sp.ExtMassInside
            
            return True
        return False


Controller = ControlClass()

# ---------------------------------------------------------------------------


class SunPos_OT_Controller(bpy.types.Operator):
    bl_idname = "world.sunpos_controller"
    bl_label = "Sun panel event handler"
    bl_description = "Enable sun panel"

    def __del__(self):
        Stop_all_handlers()
        Controller.remove_handler()
        Display.setAction('ENABLE')
        Sun.SP.IsActive = False

    def modal(self, context, event):

        if Display.PANEL:

            if Sun.SP.ShowMap:
                if not Map.isActive:
                    if not Map.activate(context):
                        Sun.SP.ShowMap = False
            elif Map.isActive:
                Map.deactivate()

            if Sun.SP.ShowHdr:
                if not Hdr.isActive:
                    Sun.SP.BindToSun = False
                    if not Hdr.activate(context):
                        Sun.SP.ShowHdr = False
            elif Hdr.isActive:
                Hdr.deactivate()

            if Sun.SP.ShowNorth:
                if not North.isActive:
                    North.activate(context)
            elif North.isActive:
                North.deactivate()

            return {'PASS_THROUGH'}

        Display.refresh()
        return {'FINISHED'}

    def invoke(self, context, event):

        Sun.verify_ObjectGroup()
        Map.init(Sun.PP.MapLocation)
        Hdr.init()
        retval = Controller.activate(context)
        if retval != {'RUNNING_MODAL'}:
            return retval

        context.window_manager.modal_handler_add(self)
        Sun.PreBlend_handler = SunPos_new_blendfile
        bpy.app.handlers.load_pre.append(SunPos_new_blendfile)
        Sun.Frame_handler = Frame_handler
        bpy.app.handlers.frame_change_pre.append(Frame_handler)

        Display.setAction('PANEL')
        Sun.SP.IsActive = True

        return {'RUNNING_MODAL'}

############################################################################


class SunPos_OT_Map(bpy.types.Operator):
    bl_idname = "sunpos.map"
    bl_label = "World map"

    def modal(self, context, event):
        if Map.view3d_area != context.area or not Sun.SP.ShowMap:
            Map.deactivate()
            Display.refresh()
            return {'FINISHED'}
        elif not Display.PANEL:
            Stop_all_handlers()
            return {'FINISHED'}
        return  Map.event_controller(context, event)

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        Display.refresh()
        return {'RUNNING_MODAL'}

############################################################################


class SunPos_OT_Hdr(bpy.types.Operator):
    bl_idname = "sunpos.hdr"
    bl_label = "HDR map"

    def modal(self, context, event):
        if Hdr.view3d_area != context.area or not Sun.SP.ShowHdr:
            Hdr.deactivate()
            Display.refresh()
            return {'FINISHED'}
        elif not Display.PANEL:
            Stop_all_handlers()
            return {'FINISHED'}
        return  Hdr.event_controller(context, event)

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        Display.refresh()
        return {'RUNNING_MODAL'}
        
        
class SunPos_OT_start_calc_table(bpy.types.Operator):
    bl_idname = "sunpos.start_calc_table"
    bl_label = "Start Calc Saved power"
    
    def execute(self, context):
        calc_table(Sun)
        return {'FINISHED'}
        
        
class SunPos_OT_create_new_obj(bpy.types.Operator):
    bl_idname = "sunpos.create_new_obj"
    bl_label = "Create new sun Power Object"
    
    def execute(self, context):
        print('Create new object')
        Sun.delete_power_labels()
        obj = bpy.data.objects.get(Sun.PowerShowObject)
        Sun.PowerObject_verified = False
        Sun.PowerShowObject = None
        if obj:
            obj.select = True
            bpy.ops.object.delete()
        #Create new sun object
        subdivisions = ICO_SUBDIV
        size = Sun.SizeSunPowerObject
        bpy.ops.mesh.primitive_ico_sphere_add(location=(0, 0, 0), 
                                                subdivisions = subdivisions, 
                                                size = size)
        obj = bpy.context.active_object
        obj.name = 'Icosphere'
        bpy.ops.object.mode_set(mode='EDIT')
        import bmesh
        bm = bmesh.from_edit_mesh(obj.data)
        del_vertices_select = []
        floor_verts = []
        for v in bm.verts:
            if v.co.z<0:
                del_vertices_select.append(v)
        bmesh.ops.delete(bm, geom=del_vertices_select, context=1)
        bmesh.update_edit_mesh(obj.data, True)
        bpy.ops.object.mode_set(mode='OBJECT')
        Sun.PowerObject_verified = True
        Sun.PowerShowObject = 'Icosphere'
        
        return {'FINISHED'}
        
        
class SunPos_OT_start_export(bpy.types.Operator):
    bl_idname = "sunpos.start_export"
    bl_label = "Start Export Power"

    def modal(self, context, event):
        if Hdr.view3d_area != context.area or not Sun.SP.ShowHdr:
            Hdr.deactivate()
            Display.refresh()
            return {'FINISHED'}
        elif not Display.PANEL:
            Stop_all_handlers()
            return {'FINISHED'}
        return  Hdr.event_controller(context, event)
        
    def execute(self, context):
        print('Start Export')
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        print('Start Export')
        Display.refresh()
        return {'RUNNING_MODAL'}
        
        
class SunPos_OT_stop_export(bpy.types.Operator):
    bl_idname = "sunpos.stop_export"
    bl_label = "Stop Export Power"

    def modal(self, context, event):
        if Hdr.view3d_area != context.area or not Sun.SP.ShowHdr:
            Hdr.deactivate()
            Display.refresh()
            return {'FINISHED'}
        elif not Display.PANEL:
            Stop_all_handlers()
            return {'FINISHED'}
        return  Hdr.event_controller(context, event)

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        print('Stop Export')
        Display.refresh()
        return {'RUNNING_MODAL'}

############################################################################


def SunPos_new_blendfile(context):
    Stop_all_handlers()
    Cleanup_objects()


def Cleanup_callback(self, context):
    Stop_all_handlers()
    Cleanup_objects()


def Cleanup_objects():
    try:
        Sun.SP.UseObjectGroup = False
        Sun.UseObjectGroup = False
    except:
        pass
    del Sun.Selected_objects[:]
    del Sun.Selected_names[:]
    Display.setAction('ENABLE')
    Sun.SP.IsActive = False


def Stop_all_handlers():
    North.deactivate()
    Map.deactivate()
    Hdr.deactivate()

    if Sun.Frame_handler is not None:
        try:
            bpy.app.handlers.frame_change_pre.remove(Frame_handler)
        except:
            pass
    Sun.Frame_handler = None

    if Sun.PreBlend_handler is not None:
        try:
            bpy.app.handlers.load_pre.remove(SunPos_new_blendfile)
        except:
            pass
    Sun.PreBlend_handler = None

############################################################################
# The Frame_handler is called while rendering when the scene changes
# to make sure objects are updated according to any keyframes.
############################################################################


def Frame_handler(context):
    Controller.panel_changed()
    Move_sun()
