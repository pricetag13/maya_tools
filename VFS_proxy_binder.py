import maya.cmds as cmds


def get_required_joints():
    all_meshes = cmds.ls(type='mesh')
    filtered_meshes = [mesh for mesh in all_meshes if 'Proxy_geo' in mesh and 'Orig' not in mesh]
    all_mesh_transforms = []
    required_jnts = ['left_thumbEndJnt', 'left_indexEndJnt', 'left_middleEndJnt', 'left_ringEndJnt',
                     'left_pinkyEndJnt',
                     'right_thumbEndJnt', 'right_indexEndJnt', 'right_middleEndJnt', 'right_ringEndJnt',
                     'right_pinkyEndJnt',
                     'left_toeEndJnt', 'right_toeEndJnt',
                     'jawEndJnt', 'headEndJnt', ]
    for mesh in filtered_meshes:
        filtered_relatives = cmds.listRelatives(mesh, p=True, path=True)
        all_mesh_transforms.append(filtered_relatives[0])
    for mesh in all_mesh_transforms:
        required_jnt = mesh.replace('Proxy_geo', 'Jnt')
        required_jnts.append(required_jnt)
    return required_jnts


def get_missing_joints():
    missing_jnts = []
    for jnt in get_required_joints():
        if jnt not in existing_joints:
            missing_jnts.append(jnt)
    return missing_jnts


def get_misspelled_joints():
    misspelled_jnts = [jnt for jnt in existing_joints if jnt not in required_joints]
    return misspelled_jnts


required_joints = get_required_joints()
existing_joints = cmds.ls(type='joint')
missing_joints = get_missing_joints()
misspelled_joints = get_misspelled_joints()
