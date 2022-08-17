#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    import sys

    sys.path.insert(1, "C:\\Users\\user\\AppData\\Roaming\\GIMP\\2.10\\plug-ins\\")
    from td_utilities import *

    from gimpfu import *

    def pack_parts(image):
        # Remove COPIES group
        old_copies_group = pdb.gimp_image_get_layer_by_name(image, "COPIES")
        if old_copies_group is not None:
            pdb.gimp_image_remove_layer(image, old_copies_group)

        # Dublicate FINAL group
        copies_group = pdb.gimp_image_get_layer_by_name(image, "FINAL").copy()
        copies_group.name = "COPIES"
        pdb.gimp_image_insert_layer(image, copies_group, None, 0)

        total_offset = 0

        # Get all subgroups in COPIES group
        for item in copies_group.layers:
            if type(item) == gimp.GroupLayer:
                # Merge group
                pdb.gimp_image_merge_layer_group(image, item)

        for item in copies_group.layers:
            pdb.gimp_image_set_active_layer(image, item)
            pdb.plug_in_autocrop_layer(image, item)

            gimp.message("1")

            # Translate layer
            part_height = pdb.gimp_drawable_height(item)
            total_offset += part_height + 1

            gimp.message("2")

            item.translate(0, total_offset)

            gimp.message("3")

    @save_state
    def td_export_sprite(image, drawable, *args):
        pdb.gimp_image_undo_thaw(image)
        pdb.gimp_image_undo_group_start(image)

        # Pack sprite parts
        pack_parts(image)

        pdb.gimp_image_undo_group_end(image)
        pdb.gimp_image_undo_freeze(image)

        # Create mask layers

        # Export

    # Регистрируем функцию в PDB
    register(
        "python-fu-td-export-sprite",
        "TD export sprite",
        "",
        "",
        "",
        "",
        "<Image>/TD plugins/TD export sprite",
        "*",
        [],
        [],
        td_export_sprite,
    )  # Имя исходной функции и меню в которое будет помещён пункт запускающий дополнение

    # Запускаем скрипт
    main()

except Exception as e:
    gimp.message(str(e))
