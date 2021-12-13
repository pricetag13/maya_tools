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

        # Compare states
        self.base_translation = (0.0, 0.0, 0.0)
        self.base_rotation = (0.0, 0.0, 0.0, 1.0)
        self.base_scale = (1.0, 1.0, 1.0)
        
        self.set_translation_dict = {}
        self.trailing_translation_dict = {}

        self.set_rotation_dict = {}
        self.trailing_rotation_dict = {}

        self.set_scale_dict = {}
        self.trailing_scale_dict = {}

        self.translation_tolerance = 0.00005
        self.rotation_tolerance = 0.00000001
        self.scale_tolerance = 0.005

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
        for frame in range(self.start_frame, self.end_frame + 2):
            current_frame = cmds.currentTime(frame)
            # Loop through transforms
            for key, data in self.animation_data.items():
                transform = key.split(":")[1]
                transform_data = anim_utils.get_transform_data(transform)
                set_time = 1 / self.fps * (current_frame - 1)
                translation = transform_data["RelativeTranslate"]
                rotation = tuple(transform_data["RelativeQuaternion"])
                scale = transform_data["Scale"]

                add_data = False

                if frame == self.start_frame:
                    self.trailing_translation_dict[key] = self.base_translation
                    self.set_translation_dict[key] = translation

                    self.trailing_rotation_dict[key] = self.base_rotation
                    self.set_rotation_dict[key] = rotation

                    self.trailing_scale_dict[key] = self.base_scale
                    self.set_scale_dict[key] = scale
                    continue

                translation_comparator = list(zip(self.trailing_translation_dict[key],
                                                  self.set_translation_dict[key],
                                                  translation))

                rotation_comparator = list(zip(self.trailing_rotation_dict[key],
                                               self.set_rotation_dict[key],
                                               rotation))

                scale_comparator = list(zip(self.trailing_scale_dict[key],
                                            self.set_scale_dict[key],
                                            scale))

                rotation_change = False
                scale_change = False

                translation_change = self.compare_frames(comparator=translation_comparator,
                                                         tolerance=self.translation_tolerance)

                if translation_change:
                    add_data = True
                else:
                    rotation_change = self.compare_frames(comparator=rotation_comparator,
                                                          tolerance=self.rotation_tolerance)

                if rotation_change:
                    add_data = True
                else:
                    scale_change = self.compare_frames(comparator=scale_comparator, tolerance=self.scale_tolerance)

                if scale_change:
                    add_data = True

                if add_data:
                    set_data = (set_time, 1)
                    set_data += self.set_translation_dict[key]
                    set_data += self.set_rotation_dict[key]
                    set_data += self.set_scale_dict[key]
                    data[1] += set_data

                self.trailing_translation_dict[key] = self.set_translation_dict[key]
                self.trailing_rotation_dict[key] = self.set_rotation_dict[key]
                self.trailing_scale_dict[key] = self.set_scale_dict[key]

                self.set_translation_dict[key] = translation
                self.set_rotation_dict[key] = rotation
                self.set_scale_dict[key] = scale

    @staticmethod
    def compare_frames(comparator, tolerance):
        """Return true if there is a change in frame value beyond specified tolerance"""
        for compare_set in comparator:
            trailing_min = compare_set[0] - tolerance
            trailing_max = compare_set[0] + tolerance
            next_min = compare_set[-1] - tolerance
            next_max = compare_set[-1] + tolerance
            set_value = compare_set[1]
            if not trailing_min < set_value < trailing_max or not next_min < set_value < next_max:
                return True

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
        self.set_units()
        self.collect_animation_data_from_scene()
        self.write_boiler_plate()
        for transform, data in self.animation_data.items():
            self.write_track(transform, data)
        cmds.currentTime(self.current_frame)
        self.reset_units()
        print("Export Success: {0}".format(self.output_file))
