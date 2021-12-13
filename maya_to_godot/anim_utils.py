import re
import maya.cmds as cmds
import maya.api.OpenMaya as OpenMaya


def get_timeline_info():
    time_line_info = {}
    start = cmds.playbackOptions(query=True, min=True)
    end = cmds.playbackOptions(query=True, max=True)
    current = cmds.currentTime(query=True)
    duration = end - start + 2
    fps_string = cmds.currentUnit(query=True, time=True)
    fps = 0
    if "fps" in fps_string:
        fps = int(re.findall(r'\d+', fps_string)[0])
    elif fps_string == "game":
        fps = 15
    elif fps_string == "film":
        fps = 24
    elif fps_string == "pal":
        fps = 25
    elif fps_string == "ntsc":
        fps = 30
    elif fps_string == "show":
        fps = 48
    elif fps_string == "palf":
        fps = 50
    elif fps_string == "ntscf":
        fps = 60
    else:
        print("No valid FPS specified.")

    length_in_seconds = (end - start) / fps

    time_line_info["Start"] = int(start)
    time_line_info["End"] = int(end)
    time_line_info["Current"] = int(current)
    time_line_info["Duration"] = int(duration)
    time_line_info["FPS"] = fps
    time_line_info["LengthInSeconds"] = length_in_seconds
    return time_line_info


def get_start_or_end_frame(position):
    value = 0
    if position == "start":
        value = get_timeline_info()[0]
    elif position == "end":
        value = get_timeline_info()[1]
    return int(value)


def set_start_or_end_frame(position, value):
    if position == "start":
        cmds.playbackOptions(min=value)
    elif position == "end":
        cmds.playbackOptions(max=value)


def set_fps(fps):
    cmds.currentUnit(time="{0}fps".format(fps))


def get_transform_data(transform):
    transform_data = {}
    translate = cmds.getAttr("{0}.translate".format(transform))[0]
    relative_translate = translate
    attribute_exists = cmds.attributeQuery("restTranslate", node=transform, exists=True)
    if attribute_exists:
        rest_translate = cmds.getAttr("{0}.restTranslate".format(transform))[0]
        relative_translate_list = []
        translate_compare = zip(translate, rest_translate)
        for axis in translate_compare:
            relative_axis = axis[0] - axis[1]
            relative_translate_list.append(relative_axis)
            relative_translate = tuple(relative_translate_list)

    rotate = cmds.getAttr("{0}.rotate".format(transform))[0]
    rest_rotate = cmds.getAttr("{0}.preferredAngle".format(transform))[0]

    eular = OpenMaya.MEulerRotation(rotate)
    rest_eular = OpenMaya.MEulerRotation(rest_rotate)

    quaternion = eular.asQuaternion()
    inverse_quaternion = quaternion.invertIt()
    rest_quaternion = rest_eular.asQuaternion()
    relative_quaternion_inverted = rest_quaternion * inverse_quaternion
    relative_quaternion = relative_quaternion_inverted.invertIt()

    scale = cmds.getAttr("{0}.scale".format(transform))[0]

    transform_data["Translate"] = translate
    transform_data["RelativeTranslate"] = relative_translate
    transform_data["Rotate"] = rotate
    transform_data["Quaternion"] = quaternion
    transform_data["RelativeQuaternion"] = relative_quaternion
    transform_data["Scale"] = scale
    return transform_data


def check_attribute_exists(transform, attribute):
    attribute_exists = cmds.attributeQuery("{0}.{1}".format(transform, attribute), exists=True)
    return attribute_exists


def get_maya_unit_settings():
    maya_unit_setting = {}
    maya_angles = cmds.currentUnit(query=True, angle=True)
    maya_lengths = cmds.currentUnit(query=True, linear=True)
    maya_unit_setting["Angles"] = maya_angles
    maya_unit_setting["Lengths"] = maya_lengths
    return maya_unit_setting


def transform_has_keys(transform):
    check_attributes = ["translate", "rotate", "scale"]
    for attribute in check_attributes:
        if cmds.keyframe(transform, attribute=attribute, query=True, timeChange=True):
            return True


def get_current_selection():
    current_selection = cmds.ls(selection=True)
    return current_selection


def get_nurbs_controls():
    nurbs_curve_shapes = cmds.ls(type='nurbsCurve')
    nurbs_curve_transforms = cmds.listRelatives(nurbs_curve_shapes, parent=True, path=True)
    return nurbs_curve_transforms


def delete_constant_curves():
    for nurbs_control in get_nurbs_controls():
        in_curves = cmds.listConnections(nurbs_control, source=True, destination=False, type="animCurve")
        if in_curves:
            for in_curve in in_curves:
                value_change = cmds.keyframe(in_curve, query=True, valueChange=True, relative=True)
                if not value_change:
                    cmds.delete(in_curve)
                if len(value_change) <= 1:
                    cmds.delete(in_curve)
                if len(value_change) == 2:
                    if value_change[0] == value_change[1]:
                        cmds.delete(in_curve)
