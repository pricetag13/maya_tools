import maya.cmds as cmds

import anim_utils

# TODO: Remove reload
import importlib
importlib.reload(anim_utils)


class AnimExport(object):
    """
    Export animation from joints under "Skeleton" transform
    Writes as .tres (Godot native animation format)
    Godot version XX
    Maya version XX
    """
    def __init__(self, output_directory=None,
                 output_file=None,
                 resource=None,
                 skeleton=None):

        # Supplied from UI
        self.output_directory = output_directory
        self.output_file = output_file
        self.resource = resource
        self.skeleton = skeleton

        # Queries scene timeline
        self.start_frame = anim_utils.get_timeline_info()["Start"]
        self.end_frame = anim_utils.get_timeline_info()["End"]
        self.fps = anim_utils.get_timeline_info()["FPS"]
        self.length_in_seconds = anim_utils.get_timeline_info()["LengthInSeconds"]
        self.current_frame = anim_utils.get_timeline_info()["Current"]

        # Queries maya unit settings
        self.scene_angles = anim_utils.get_maya_unit_settings()["Angles"]
        self.scene_lengths = anim_utils.get_maya_unit_settings()["Lengths"]

        # Stores animation data to be written
        self.animation_data = {}

    @staticmethod
    def get_boiler_plate(resource, length):
        boiler_plate = [
            '[gd_resource type = "Animation" format = 2]',
            "",
            "[resource]",
            'resource_name = "{0}"'.format(resource),
            "length = {0}".format(length),
            ""
        ]
        return boiler_plate

    @staticmethod
    def get_track(track_number, transform, pool_real_array):
        track = [
            'tracks/{0}/type = "transform"'.format(track_number),
            'tracks/{0}/path = NodePath("{1}")'.format(track_number, transform),
            'tracks/{0}/interp = 1'.format(track_number),
            'tracks/{0}/loop_wrap = true'.format(track_number),
            'tracks/{0}/imported = false'.format(track_number),
            'tracks/{0}/enabled = true'.format(track_number),
            'tracks/{0}/keys = PoolRealArray{1}'.format(track_number, pool_real_array),
            ''
        ]
        return track

    def collect_animation_data_from_scene(self):
        transforms = cmds.listRelatives(self.skeleton, allDescendents=True, type="joint")
        # Add keys to animation data dictionary
        for index, transform in enumerate(transforms):
            self.animation_data["{0}:{1}".format(self.skeleton, transform)] = []
            # Index is the track number
            self.animation_data["{0}:{1}".format(self.skeleton, transform)].append(index)
            real_pool_array = ()
            self.animation_data["{0}:{1}".format(self.skeleton, transform)].append(real_pool_array)

        # Loop through timeline
        for frame in range(self.start_frame, self.end_frame + 1):
            current_fame = cmds.currentTime(frame)
            # Loop through transforms
            for key, data in self.animation_data.items():
                transform = key.split(":")[1]
                transform_data = anim_utils.get_transform_data(transform)
                time = 1 / self.fps * current_fame
                data[1] += (time,)
                data[1] += (1,)
                data[1] += transform_data["RelativeTranslate"]
                data[1] += tuple(transform_data["RelativeQuaternion"])
                data[1] += transform_data["Scale"]

    def write_boiler_plate(self):
        boiler_plate = self.get_boiler_plate(self.resource, self.length_in_seconds)
        with open(self.output_file, 'w') as outfile:
            outfile.write('\n'.join(boiler_plate))

    def write_track(self, transform, data):
        track = self.get_track(track_number=data[0],
                               transform=transform,
                               pool_real_array=data[1])
        with open(self.output_file, 'a') as outfile:
            outfile.write('\n'.join(track))

    @staticmethod
    def set_units():
        cmds.currentUnit(angle="rad")
        cmds.currentUnit(linear="m")

    def reset_units(self):
        cmds.currentUnit(angle=self.scene_angles)
        cmds.currentUnit(linear=self.scene_lengths)

    def export(self):
        print("Exporting: {0}".format(self.output_file))
        self.set_units()
        self.collect_animation_data_from_scene()
        self.write_boiler_plate()
        for transform, data in self.animation_data.items():
            self.write_track(transform, data)
        cmds.currentTime(self.current_frame)
        self.reset_units()
        print("Export Success: {0}".format(self.output_file))
