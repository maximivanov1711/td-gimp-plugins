#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO:
# - reorder FINAL group
# - process folders

# INTERESTING:
# freeze layers
# flatten = remove alpha

try:
    import sys

    sys.path.insert(1, "C:\\Users\\user\\AppData\\Roaming\\GIMP\\2.10\\plug-ins\\")
    from td_utilities import *

    from gimpfu import *
    import gimpcolor

    def remove_temp_layers(items):
        for item in items:
            if type(item) == gimp.Layer:
                layer_prefix = item.name.split()[0]

                if layer_prefix == "_temp":
                    image.remove_layer(item)
            else:
                remove_temp_layers(item.layers)

    def process_layers(items):
        items.reverse()

        for item in items:
            if type(item) == gimp.Layer:
                layer_prefix = item.name.split()[0]

                if layer_prefix == "_e":
                    effect(item)
            else:
                process_layers(item.layers)

    def effect(layer):
        global temp_group

        blur_layer = create_temp_layer(image, layer, "_temp " + layer.name, temp_group)
        blur_layer.translate(100, 0)

        # Add blur
        pdb.gimp_layer_resize_to_image_size(blur_layer)
        mask = pdb.gimp_layer_create_mask(blur_layer, 2)
        pdb.gimp_layer_add_mask(blur_layer, mask)
        pdb.plug_in_sel_gauss(image, blur_layer, 1.5, 255)

        edges_layer = create_temp_layer(image, layer, "_temp " + layer.name, temp_group)
        edges_layer.translate(100, 0)

        # Add edges
        pdb.gimp_image_select_color(image, 2, edges_layer, gimpcolor.RGB(0, 0, 0))
        mask = pdb.gimp_layer_create_mask(edges_layer, 4)
        pdb.gimp_layer_add_mask(edges_layer, mask)
        pdb.gimp_layer_set_opacity(edges_layer, 50)

        pdb.gimp_item_set_expanded(temp_group, False)

    image = None
    drawable = None
    temp_group = None

    @save_state
    def td_apply_effects(img, dbl):
        global image, drawable, temp_group

        image = img
        drawable = dbl

        temp_group = get_group(image, "FINAL")

        # TODO:
        # - process multiple effects
        if pdb.gimp_image_is_dirty(image):
            active_layer = image.active_layer

            # remove_temp_layers(image.layers)
            temp_index = remove_active_temp(active_layer)

            # process_layers(image.layers)
            process_layer(active_layer)

            pdb.gimp_image_clean_all(image)

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
