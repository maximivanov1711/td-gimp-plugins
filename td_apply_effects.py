#!/usr/bin/env python
# -*- coding: utf-8 -*-

# INTERESTING:
# freeze layers
# flatten = remove alpha

# TODO:
# - fix effects outside subgroups in RAW group
# - ? thaw layers in save_state


try:
    import sys

    sys.path.insert(1, "C:\\Users\\user\\AppData\\Roaming\\GIMP\\2.10\\plug-ins\\")
    from td_utilities import *

    from gimpfu import *
    import gimpcolor

    def remove_unused_temp_layers(items):
        global created_temps

        # Remove temp layers
        for item in items:
            layer_name_parsed = parse_layer_name(item.name)
            if item not in created_temps:
                if "temp" in layer_name_parsed["args"].keys():
                    image.remove_layer(item)
            elif type(item) == gimp.GroupLayer:
                remove_unused_temp_layers(item.layers)

    def process_layers(items):
        global image, created_temps

        items.reverse()

        for item in items:
            if type(item) == gimp.Layer:
                layer_name_parsed = parse_layer_name(item.name)
                if "e" in layer_name_parsed["args"].keys():
                    effect(item, layer_name_parsed["args"]["e"][0])
                else:
                    effect(item, 2)
            else:
                # Create subfolder in item parent group
                parent_group = pdb.gimp_item_get_parent(item)
                if parent_group.name == "RAW":
                    temp_parent_group = pdb.gimp_image_get_layer_by_name(image, "FINAL")
                else:
                    temp_parent_group = pdb.gimp_image_get_layer_by_name(
                        image, parent_group.name + " _temp"
                    )

                temp_group = pdb.gimp_image_get_layer_by_name(
                    image, item.name + " _temp"
                )
                if temp_group is None:
                    temp_group = pdb.gimp_layer_group_new(image)
                    temp_group.name = item.name + " _temp"
                    pdb.gimp_image_insert_layer(image, temp_group, temp_parent_group, 0)

                created_temps.append(temp_group)

                process_layers(item.layers)

    def effect(layer, arg1):
        global created_temps

        # Get temp group
        parent_group = pdb.gimp_item_get_parent(layer)
        temp_group = pdb.gimp_image_get_layer_by_name(
            image, parent_group.name + " _temp"
        )

        blur_layer = create_temp_layer(
            image, layer, layer.name + " _temp blur", temp_group, created_temps
        )

        # Add blur
        pdb.gimp_layer_resize_to_image_size(blur_layer)
        mask = pdb.gimp_layer_create_mask(blur_layer, 2)
        pdb.gimp_layer_add_mask(blur_layer, mask)
        pdb.plug_in_sel_gauss(image, blur_layer, arg1, 255)

        edges_layer = create_temp_layer(
            image, layer, layer.name + " _temp edges", temp_group, created_temps
        )

        # Add edges
        pdb.gimp_image_select_color(image, 2, edges_layer, gimpcolor.RGB(0, 0, 0))
        mask = pdb.gimp_layer_create_mask(edges_layer, 4)
        pdb.gimp_layer_add_mask(edges_layer, mask)
        pdb.gimp_layer_set_opacity(edges_layer, 50)
        pdb.gimp_selection_clear(image)

    image = None
    drawable = None
    final_group = None
    created_temps = []

    @save_state
    def td_apply_effects(img, dbl):
        global image, drawable, final_group, created_temps

        created_temps = []

        image = img
        drawable = dbl

        final_group = get_group(image, "FINAL")
        raw_group = get_group(image, "RAW")

        process_layers(raw_group.layers)
        remove_unused_temp_layers(final_group.layers)

        pdb.gimp_item_set_expanded(final_group, False)

        pdb.gimp_image_undo_group_end(image)
        pdb.gimp_image_undo_group_start(image)

        pdb.gimp_item_set_visible(final_group, True)

    # Регистрируем функцию в PDB
    register(
        "python-fu-td-apply-effects",
        "TD apply effects",
        "",
        "",
        "",
        "",
        "<Image>/TD plugins/TD Apply effects",
        "*",
        [],
        [],
        td_apply_effects,
    )  # Имя исходной функции и меню в которое будет помещён пункт запускающий дополнение

    # Запускаем скрипт
    main()

except Exception as e:
    gimp.message(str(e))
