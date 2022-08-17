#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from gimpfu import *

    def save_state(func):
        def wrapper(image, drawable):
            prev_active_layer = image.active_layer
            pdb.gimp_image_undo_freeze(image)
            prev_selection = pdb.gimp_selection_save(image)

            image.active_layer = prev_active_layer

            res = func(image, drawable)

            image.active_layer = prev_active_layer

            pdb.gimp_selection_load(prev_selection)
            pdb.gimp_image_undo_thaw(image)

            gimp.displays_flush()

            return res

        return wrapper

    def get_group(image, group_name):
        new_group = pdb.gimp_image_get_layer_by_name(image, group_name)
        if new_group is None:
            new_group = pdb.gimp_layer_group_new(image)
            new_group.name = group_name
            pdb.gimp_image_insert_layer(image, new_group, None, 0)

        return new_group

    def create_temp_layer(image, orig_layer, temp_layer_name, group, all_temps=None):
        temp_layer = orig_layer.copy()
        temp_layer.name = temp_layer_name
        pdb.gimp_item_set_visible(temp_layer, True)

        prev_temp = pdb.gimp_image_get_layer_by_name(image, temp_layer_name)
        if prev_temp is not None:
            prev_position = pdb.gimp_image_get_item_position(image, prev_temp)
            image.remove_layer(prev_temp)
            image.insert_layer(temp_layer, group, prev_position)
        elif len(group.layers) > 0:
            index = 0

            for i, layer in enumerate(group.layers):
                layer_name_parsed = parse_layer_name(layer.name)
                if "top" in layer_name_parsed["args"].keys():
                    index = i + 1

            image.insert_layer(temp_layer, group, index)
        else:
            image.insert_layer(temp_layer, group)

        if all_temps is not None:
            all_temps.append(temp_layer)

        return temp_layer

    def parse_layer_name(layer_name):
        words = layer_name.split()

        res = {}
        res["name"] = words[0]
        res["args"] = {}

        if len(words) > 1:
            func = None
            for word in words[1:]:
                if word[0] == "_":
                    func = word[1:]
                    res["args"][func] = []
                elif func:
                    res["args"][func].append(word)

        return res

except Exception as e:
    gimp.message(str(e))
