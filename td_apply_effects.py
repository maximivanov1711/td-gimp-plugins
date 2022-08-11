#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO:
# - reorder FINAL group
# - save order

# INTERESTING:
# freeze layers
# flatten = remove alpha

try:
    import sys

    sys.path.insert(1, "C:\\Users\\user\\AppData\\Roaming\\GIMP\\2.10\\plug-ins\\")
    from td_utilities import *

    from gimpfu import *
    import gimpcolor

    def remove_unused_temp_layers(items):

        # Save temp layers positions
        # for item in items:
        #     if type(item) == gimp.Layer:
        #         layer_prefix = item.name.split()[0]
        #         if layer_prefix == "_temp":
        #             prev_position = pdb.gimp_image_get_item_position(image, item)
        #             temps[item.name] = int(prev_position)

        # Remove temp layers
        for item in items:
            if type(item) == gimp.Layer:
                layer_name_parsed = parse_layer_name(item.name)
                if "temp" in layer_name_parsed["args"].keys():
                    orig_layer_name = layer_name_parsed["name"]

                    orig_layer = pdb.gimp_image_get_layer_by_name(
                        image, orig_layer_name
                    )

                    if orig_layer is None:
                        image.remove_layer(item)
            else:
                remove_unused_temp_layers(item.layers)

    def process_layers(items):
        items.reverse()

        for item in items:
            if type(item) == gimp.Layer:
                layer_name_parsed = parse_layer_name(item.name)
                for arg_name in layer_name_parsed["args"].keys():
                    if arg_name == "e":
                        effect(item)
            else:
                process_layers(item.layers)

    def effect(layer):
        global final_group

        blur_layer = duplicate_layer(
            image, layer, layer.name + " _temp blur", final_group
        )
        blur_layer.translate(100, 0)

        # Add blur
        pdb.gimp_layer_resize_to_image_size(blur_layer)
        mask = pdb.gimp_layer_create_mask(blur_layer, 2)
        pdb.gimp_layer_add_mask(blur_layer, mask)
        pdb.plug_in_sel_gauss(image, blur_layer, 1.5, 255)

        edges_layer = duplicate_layer(
            image, layer, layer.name + " _temp edges", final_group
        )
        edges_layer.translate(100, 0)

        # Add edges
        pdb.gimp_image_select_color(image, 2, edges_layer, gimpcolor.RGB(0, 0, 0))
        mask = pdb.gimp_layer_create_mask(edges_layer, 4)
        pdb.gimp_layer_add_mask(edges_layer, mask)
        pdb.gimp_layer_set_opacity(edges_layer, 50)

    image = None
    drawable = None
    final_group = None

    @save_state
    def td_apply_effects(img, dbl):
        global image, drawable, final_group, temps

        image = img
        drawable = dbl

        pdb.gimp_image_freeze_layers(image)

        final_group = get_group(image, "FINAL")
        raw_group = get_group(image, "RAW")

        remove_unused_temp_layers(final_group.layers)

        process_layers(raw_group.layers)

        pdb.gimp_image_thaw_layers(image)
        pdb.gimp_item_set_expanded(final_group, False)

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
