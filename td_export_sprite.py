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

        # Get all subgroups in COPIES group
        pdb.gimp_image_set_active_layer(image, copies_group)
        pdb.plug_in_autocrop_layer(image, copies_group)

        orig_y = get_drawable_y_center(copies_group)
        total_offset = pdb.gimp_drawable_height(copies_group) / 2

        for item in copies_group.layers:
            pdb.gimp_image_set_active_layer(image, item)
            pdb.plug_in_autocrop_layer(image, item)

            y = get_drawable_y_center(item)
            size = pdb.gimp_drawable_height(item)
            # Translate layer
            total_offset += size / 2 + 4
            item.translate(0, total_offset + (orig_y - y))
            total_offset += size / 2

    def get_drawable_y_center(drawable):
        return (
            pdb.gimp_drawable_offsets(drawable)[1]
            + pdb.gimp_drawable_height(drawable) / 2
        )

    def fill_mask_groups(image, items, masks_folder):
        items.reverse()

        for item in items:
            if type(item) == gimp.Layer:
                layer_name_parsed = parse_layer_name(item.name)

                if "m" in layer_name_parsed["args"].keys():
                    mask_group = get_group_in_parent(
                        image, "MASK " + layer_name_parsed["args"]["m"][0], "MASKS"
                    )

                    create_temp_layer(image, item, item.name + " _mask", mask_group)
            else:
                fill_mask_groups(image, item.layers, masks_folder)

    def create_masks(image, items):
        masks_folder = pdb.gimp_image_get_layer_by_name(image, "MASKS")
        if masks_folder is not None:
            pdb.gimp_image_remove_layer(image, masks_folder)

        masks_folder = get_group(image, "MASKS")
        for item in masks_folder.layers:
            layer_name_parsed = parse_layer_name(item.name)
            if layer_name_parsed["name"] == "MASK":
                pdb.gimp_image_remove_layer(image, item)

        fill_mask_groups(image, items, masks_folder)

        for item in masks_folder.layers:
            layer_name_parsed = parse_layer_name(item.name)
            if layer_name_parsed["name"] == "MASK" and type(item) == gimp.GroupLayer:
                mask_layer = pdb.gimp_image_merge_layer_group(image, item)

                pdb.gimp_layer_resize_to_image_size(mask_layer)
                mask = pdb.gimp_layer_create_mask(mask_layer, 3)
                pdb.gimp_layer_add_mask(mask_layer, mask)

                real_buffer_name = pdb.gimp_edit_named_copy(mask, "mask")

                floating = pdb.gimp_edit_named_paste(mask, real_buffer_name, True)

                pdb.gimp_floating_sel_attach(floating, mask_layer)

                pdb.gimp_floating_sel_anchor(floating)

                pdb.gimp_layer_remove_mask(mask_layer, 1)

        pdb.gimp_item_set_expanded(masks_folder, False)
        pdb.gimp_item_set_visible(masks_folder, False)

    @save_state
    def td_export_sprite(image, *args):
        # Pack sprite parts
        pack_parts(image)

        copies_group = get_group(image, "COPIES")

        # Create mask layers
        create_masks(image, copies_group.layers)

        for item in copies_group.layers:
            if type(item) == gimp.GroupLayer:
                # Merge group
                pdb.gimp_image_merge_layer_group(image, item)

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
