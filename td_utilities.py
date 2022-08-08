#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gimpfu import *


def save_state(func):
    def wrapper(image, drawable):
        gimp.Image.undo_freeze(image)
        prev_active_layer = image.active_layer
        prev_selection = pdb.gimp_selection_save(image)

        res = func(image, drawable)

        gimp.Image.undo_thaw(image)
        image.active_layer = prev_active_layer
        pdb.gimp_selection_load(prev_selection)

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


def duplicate_layer(image, layer, new_layer_name, final_group):
    new_layer = layer.copy()
    new_layer.name = new_layer_name
    pdb.gimp_item_set_visible(new_layer, True)
    image.insert_layer(new_layer, final_group)

    return new_layer


def parse_layer_name(layer_name):
    words = layer_name.split()

    res = {}
    res["name"] = words[0]

    func = None
    for word in words[1:]:
        if word[0] == "_":
            func = word[1:]
            res[func] = []
        elif func:
            res[func].append(word)

    return res
