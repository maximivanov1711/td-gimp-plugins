#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import sys

    sys.path.insert(1, "C:\\Users\\user\\AppData\\Roaming\\GIMP\\2.10\\plug-ins\\")
    from td_utilities import *

    from gimpfu import *

    SYMMETRY_GROUP_NAME = "symmetry"

    @save_state
    def td_apply_symmetry(image, drawable, *args):
        symmetry_group = get_group(image, SYMMETRY_GROUP_NAME)
        symmetry_layers = symmetry_group.layers

        if len(symmetry_layers) > 0:
            pass

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
