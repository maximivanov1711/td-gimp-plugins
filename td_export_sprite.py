#!/usr/bin/env python
# -*- coding: utf-8 -*-


# TODO:
# - * fix grayscale
# - fix top layers in FINAL

try:
    import sys

    sys.path.insert(1, "C:\\Users\\user\\AppData\\Roaming\\GIMP\\2.10\\plug-ins\\")
    from td_utilities import *

    from gimpfu import *

    import os.path

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
                        image, layer_name_parsed["args"]["m"][0] + " _mask", "MASKS"
                    )

                    mask_layer = create_temp_layer(
                        image, item, item.name + " _mask", mask_group
                    )
                    pdb.gimp_layer_set_mode(mask_layer, 0)

            else:
                fill_mask_groups(image, item.layers, masks_folder)

    def create_masks(image, items):
        masks_group = pdb.gimp_image_get_layer_by_name(image, "MASKS")
        if masks_group is not None:
            pdb.gimp_image_remove_layer(image, masks_group)

        masks_group = get_group(image, "MASKS")
        for item in masks_group.layers:
            layer_name_parsed = parse_layer_name(item.name)
            if "mask" in layer_name_parsed["args"].keys():
                pdb.gimp_image_remove_layer(image, item)

        fill_mask_groups(image, items, masks_group)

        for item in masks_group.layers:
            layer_name_parsed = parse_layer_name(item.name)
            if (
                "mask" in layer_name_parsed["args"].keys()
                and type(item) == gimp.GroupLayer
            ):
                mask_layer = pdb.gimp_image_merge_layer_group(image, item)

                pdb.gimp_layer_resize_to_image_size(mask_layer)
                mask = pdb.gimp_layer_create_mask(mask_layer, 3)
                pdb.gimp_layer_add_mask(mask_layer, mask)

                real_buffer_name = pdb.gimp_edit_named_copy(mask, "mask")

                floating = pdb.gimp_edit_named_paste(mask, real_buffer_name, True)

                pdb.gimp_floating_sel_attach(floating, mask_layer)

                pdb.gimp_floating_sel_anchor(floating)

                pdb.gimp_layer_remove_mask(mask_layer, 1)

                pdb.gimp_layer_resize_to_image_size(mask_layer)

        grayscale_group = pdb.gimp_image_get_layer_by_name(image, "COPIES").copy()
        grayscale_group.name = "GRAYSCALE"
        pdb.gimp_image_insert_layer(image, grayscale_group, masks_group, 0)
        grayscale_layer = pdb.gimp_image_merge_layer_group(image, grayscale_group)
        pdb.gimp_drawable_desaturate(grayscale_layer, 2)
        pdb.gimp_layer_resize_to_image_size(grayscale_layer)

    def export(image):
        # Export masks
        file_name = os.path.splitext(image.name)[0]

        save_dir = (
            os.path.dirname(pdb.gimp_image_get_uri(image)).replace("file:///", "")
            + "/"
            + file_name
            + "_export/"
        )
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        masks_group = get_group(image, "MASKS")
        for mask_layer in masks_group.layers:
            # Export image
            layer_name_parsed = parse_layer_name(mask_layer.name)
            save_path = save_dir + file_name + "_" + layer_name_parsed["name"] + ".png"
            pdb.file_png_save_defaults(image, mask_layer, save_path, save_path)

        # Hide MASKS group
        pdb.gimp_item_set_visible(masks_group, False)

        # Export Final + COPIES
        save_path = save_dir + file_name + ".png"

        new_image = pdb.gimp_image_duplicate(image)
        layer = pdb.gimp_image_merge_visible_layers(new_image, CLIP_TO_IMAGE)
        pdb.gimp_layer_resize_to_image_size(layer)
        pdb.file_png_save_defaults(new_image, layer, save_path, save_path)
        pdb.gimp_image_delete(new_image)

        pdb.gimp_progress_end()

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
        export(image)

        masks_group = get_group(image, "MASKS")
        pdb.gimp_item_set_expanded(masks_group, False)

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
