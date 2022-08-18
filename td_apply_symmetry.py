#!/usr/bin/env python
# -*- coding: utf-8 -*-


# TODO
# - fix symmetry undo


try:
    import sys

    sys.path.insert(1, "C:\\Users\\user\\AppData\\Roaming\\GIMP\\2.10\\plug-ins\\")
    from td_utilities import *

    from gimpfu import *

    def flip_layer(image, drawable, layer, symmetry_type, axis):
        if symmetry_type == 0:
            pdb.gimp_image_select_rectangle(
                image, 2, axis + 1, 0, image.height, image.width
            )
        else:
            pdb.gimp_image_select_rectangle(
                image, 2, 0, axis + 1, image.height, image.width
            )

        pdb.gimp_edit_clear(drawable)
        pdb.gimp_selection_none(image)

        real_buffer_name = pdb.gimp_edit_named_copy(layer, "symmetry")

        floating = pdb.gimp_edit_named_paste(layer, real_buffer_name, True)

        # flip selection
        floating = pdb.gimp_item_transform_flip_simple(
            floating, symmetry_type, False, axis
        )

        pdb.gimp_floating_sel_anchor(floating)

        gimp.displays_flush()

    SYMMETRY_GROUP_NAME = "symmetry"

    @save_state
    def td_apply_symmetry(image, drawable, *args):
        active_layer = image.active_layer

        symmetry_group = get_group(image, SYMMETRY_GROUP_NAME)
        symmetry_layers = symmetry_group.layers

        if len(symmetry_layers) == 0:
            return

        layer_name_parsed = parse_layer_name(symmetry_layers[0].name)

        args = layer_name_parsed["args"]

        if "h" in args.keys():
            # apply horizontal symmetry
            flip_layer(
                image=image,
                drawable=drawable,
                layer=active_layer,
                symmetry_type=1,
                axis=float(args["h"][0]),
            )

        if "v" in args.keys():
            # apply vertical symmetry
            flip_layer(
                image=image,
                drawable=drawable,
                layer=active_layer,
                symmetry_type=0,
                axis=float(args["v"][0]),
            )

    # Регистрируем функцию в PDB
    register(
        "python-fu-td-apply-symmetry",
        "TD apply symmetry",
        "",
        "",
        "",
        "",
        "<Image>/TD plugins/TD Apply symmetry",
        "*",
        [],
        [],
        td_apply_symmetry,
    )  # Имя исходной функции и меню в которое будет помещён пункт запускающий дополнение

    # Запускаем скрипт
    main()

except Exception as e:
    gimp.message(str(e))
