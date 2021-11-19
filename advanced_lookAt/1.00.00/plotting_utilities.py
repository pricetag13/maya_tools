from maya import cmds
from maya import mel
from maya import OpenMayaAnim

from functools import wraps


def undo_able(func):
    """
    Decorator - block code into a chunk for easier undo
    """
    @wraps(func)
    def wrap(*args, **kwargs):
        try:
            cmds.undoInfo(openChunk=True)
            return func(*args, **kwargs)
        finally:
            cmds.undoInfo(closeChunk=True)

    return wrap


def disable_viewport(func):
    """
    Decorator - turn off Maya display while func is running.
    if func will fail, the error will be raised after.
    """

    @wraps(func)
    def wrap(*args, **kwargs):

        # Turn $gMainPane Off:
        mel.eval("paneLayout -e -manage false $gMainPane")

        # Decorator will try/except running the function.
        # But it will always turn on the viewport at the end.
        # In case the function failed, it will prevent leaving maya viewport off.
        try:
            return func(*args, **kwargs)
        except Exception:
            # will raise original error
            raise
        finally:
            mel.eval("paneLayout -e -manage true $gMainPane")

    return wrap


def get_timeline_range():
    """Returns integer values of start a and end of maya's timeline"""
    _min = int(OpenMayaAnim.MAnimControl.minTime().value())
    _max = int(OpenMayaAnim.MAnimControl.maxTime().value())
    return _min, _max


def get_current_frame():
    """Returns integer values of start a and end of maya's timeline"""
    _current = int(OpenMayaAnim.MAnimControl.currentTime().value())
    return _current


def flatten_anim_curve(curve_list, startframe, endframe):
    """Flattens a list of animation curves and sets in and out frames to zero.
    (based on the current frame range)"""
    for curve in curve_list:
        cmds.setKeyframe(curve, time=startframe - 1, insert=True)
        cmds.setKeyframe(curve, time=endframe + 1, insert=True, )
        cmds.cutKey(curve, time=(startframe, endframe))
        cmds.setKeyframe(curve, time=startframe, value=0, outTangentType='linear')
        cmds.setKeyframe(curve, time=endframe, value=0, inTangentType='linear')


def get_namespaces():
    """ returns a list of namespaces in the scene """
    # set to the root ":" so that we list all namespaces in the root only.
    stored_namespace = cmds.namespaceInfo(currentNamespace=True)

    cmds.namespace(setNamespace=':')
    all_namespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=False)
    namespaces = [ns for ns in all_namespaces if ns not in ['UI', 'shared']]

    used_namespaces = [':']
    for _namespace in namespaces:
        cmds.namespace(setNamespace=':')
        cmds.namespace(setNamespace=_namespace)
        # if there are any objects in the namespace then return otherwise we don't need it.
        if cmds.namespaceInfo(listOnlyDependencyNodes=True):
            used_namespaces.append(_namespace)

    cmds.namespace(setNamespace=stored_namespace)
    return used_namespaces
