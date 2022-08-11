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
            image.add_layer(new_group)

        return new_group

    def duplicate_layer(image, layer, new_layer_name, group):
        new_layer = layer.copy()
        new_layer.name = new_layer_name
        pdb.gimp_item_set_visible(new_layer, True)

        prev_temp = pdb.gimp_image_get_layer_by_name(image, new_layer_name)
        if prev_temp is not None:
            prev_position = pdb.gimp_image_get_item_position(image, prev_temp)
            image.remove_layer(prev_temp)
            image.insert_layer(new_layer, group, prev_position)
        else:
            image.insert_layer(new_layer, group)

        return new_layer

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
