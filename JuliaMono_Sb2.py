#!/usr/bin/env python
# -*- coding: utf-8 -*-
import fontforge
import psMat
import os
import sys
import math
import glob
from datetime import datetime

ASCENT = 1600
DESCENT = 400
SOURCE = os.getenv("JULIAMONO_SB2_SOURCE_FONTS_PATH", "./sourceFonts")
LICENSE = open("./LICENSE.txt").read()
COPYRIGHT = "Copyright (c) 2021, Shunsuke GOTOH (antimon2.me@gmail.com)"
VERSION = "0.0.5"
FAMILY = "JuliaMono_Sb2"

fonts = [
    {
        "family": FAMILY,
        "name": FAMILY + "-Regular",
        "filename": FAMILY + "-Regular.ttf",
        "weight": 400,
        "weight_name": "Regular",
        "style_name": "Regular",
        "juliamono": "JuliaMono_wo_lg-Regular.ttf",
        "mgen_plus": "mgenplus-1m-regular.ttf",
        "hack_weight_reduce": 0,
        "mgen_weight_add": 0,
        "italic": False,
    },
    {
        "family": FAMILY,
        "name": FAMILY + "-RegularItalic",
        "filename": FAMILY + "-RegularItalic.ttf",
        "weight": 400,
        "weight_name": "Regular",
        "style_name": "Italic",
        "juliamono": "JuliaMono_wo_lg-RegularItalic.ttf",
        "mgen_plus": "mgenplus-1m-regular.ttf",
        "hack_weight_reduce": 0,
        "mgen_weight_add": 0,
        "italic": True,
    },
    {
        "family": FAMILY,
        "name": FAMILY + "-Bold",
        "filename": FAMILY + "-Bold.ttf",
        "weight": 700,
        "weight_name": "Bold",
        "style_name": "Bold",
        "juliamono": "JuliaMono_wo_lg-Bold.ttf",
        "mgen_plus": "mgenplus-1m-bold.ttf",
        "hack_weight_reduce": 0,
        "mgen_weight_add": 0,
        "italic": False,
    },
    {
        "family": FAMILY,
        "name": FAMILY + "-BoldItalic",
        "filename": FAMILY + "-BoldItalic.ttf",
        "weight": 700,
        "weight_name": "Bold",
        "style_name": "Bold Italic",
        "juliamono": "JuliaMono_wo_lg-BoldItalic.ttf",
        "mgen_plus": "mgenplus-1m-bold.ttf",
        "hack_weight_reduce": 0,
        "mgen_weight_add": 0,
        "italic": True,
    },
]


def log(_str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(now + " " + _str)


def remove_glyph_from_juliamono(_font):
    """Rounded Mgen+を採用したいグリフをJuliaMonoから削除"""
    glyphs = (
        list(range(0x3001, 0x3040))
        + list(range(0xFE10, 0xFE49))
        + list(range(0xFF01, 0xFF66))
        + list(range(0xFFE0, 0xFFE8))
    )

    for g in glyphs:
        _font.selection.select(g)
        _font.clear()

    return _font


def remove_glyph_from_mgenplus(_font):
    """JuliaMonoを採用したいグリフをmgenplusから削除"""
    glyphs = (
        list(range(0x0000, 0x2E52))
        + list(range(0x1D538, 0x1D7FF))
        + list(range(0x110000, 0x110254))
    )

    for g in glyphs:
        _font.selection.select(g)
        _font.clear()

    return _font


def check_files():
    err = 0
    for f in fonts:
        if not os.path.isfile(os.path.join(SOURCE, f.get("juliamono"))):
            log("%s not exists." % f)
            err = 1

        if not os.path.isfile(os.path.join(SOURCE, f.get("mgen_plus"))):
            log("%s not exists." % f)
            err = 1

    if err > 0:
        sys.exit(err)


def set_os2_values(_font, _info, _org):
    weight = _info.get("weight")
    style_name = _info.get("style_name")
    _font.os2_weight = weight
    _font.os2_width = _org.os2_width
    _font.os2_fstype = _org.os2_fstype
    if style_name == "Regular":
        _font.os2_stylemap = 64
    elif style_name == "Bold":
        _font.os2_stylemap = 32
    elif style_name == "Italic":
        _font.os2_stylemap = 1
    elif style_name == "Bold Italic":
        _font.os2_stylemap = 33
    _font.os2_vendor = _org.os2_vendor  # 'TMNM'
    _font.os2_version = _org.os2_version  # 1
    _font.os2_winascent = _org.os2_winascent  # ASCENT
    _font.os2_winascent_add = _org.os2_winascent_add  # False
    _font.os2_windescent = _org.os2_windescent  # DESCENT
    _font.os2_windescent_add = _org.os2_windescent_add  # False

    _font.os2_typoascent = _org.os2_typoascent  # -150
    _font.os2_typoascent_add = _org.os2_typoascent_add  # True
    _font.os2_typodescent = _org.os2_typodescent  # 100
    _font.os2_typodescent_add = _org.os2_typodescent_add  # True
    _font.os2_typolinegap = _org.os2_typolinegap  # 0

    _font.hhea_ascent = -150
    _font.hhea_ascent_add = True
    _font.hhea_descent = 100
    _font.hhea_descent_add = True
    _font.hhea_linegap = 0
    _font.os2_panose = (
        _org.os2_panose
    )  # (2, 11, int(weight / 100), 9, 2, 2, 3, 2, 2, 7)
    return _font


def align_to_center(_g):
    width = 0

    if _g.width > 1600:
        width = 2400
    else:
        width = 1200

    _g.width = width
    _g.left_side_bearing = _g.right_side_bearing = (
        _g.left_side_bearing + _g.right_side_bearing
    ) / 2
    _g.width = width

    return _g


def align_to_left(_g):
    width = _g.width
    _g.left_side_bearing = 0
    _g.width = width


def align_to_right(_g):
    width = _g.width
    bb = _g.boundingBox()
    left = width - (bb[2] - bb[0])
    _g.left_side_bearing = left
    _g.width = width


def reiwa(_f, _weight):
    reiwa = fontforge.open(os.path.join(SOURCE, "reiwa_Sb2.sfd"))
    if _weight == "Bold":
        reiwa.close()
        reiwa = fontforge.open(os.path.join(SOURCE, "reiwa_Sb2-Bold.sfd"))
    for g in reiwa.glyphs():
        if g.isWorthOutputting:
            # g.transform((1.82,0,0,1.82,0,0))
            g = align_to_center(g)
            reiwa.selection.select(0x00)
            reiwa.copy()
            _f.selection.select(0x32FF)
            _f.paste()
    reiwa.close()
    return _f


def fix_overflow(glyph):
    """上が1600を超えている、または下が-400を超えているグリフを
    2000x2400の枠にはまるように修正する
    ※全角のグリフのみに実施する
    """
    if glyph.width < 2400:
        return glyph
    if glyph.isWorthOutputting:
        bb = glyph.boundingBox()
        height = bb[3] - bb[1]
        if height > 2000:
            # resize
            scale = 2000 / height
            glyph.transform(psMat.scale(scale, scale))
        bb = glyph.boundingBox()
        bottom = bb[1]
        top = bb[3]
        if bottom < -400:
            glyph.transform(psMat.translate(0, -400 - bottom))
        elif top > 1600:
            glyph.transform(psMat.translate(0, 1600 - top))
    return glyph


def build_font(_f):
    juliamono = fontforge.open(os.path.join(SOURCE, _f.get("juliamono")))
    mgenplus = fontforge.open(os.path.join(SOURCE, _f.get("mgen_plus")))
    log("remove_glyph_from_mgenplus()")
    mgenplus = remove_glyph_from_mgenplus(mgenplus)

    if _f.get("mgen_weight_add") != 0:
        for g in mgenplus.glyphs():
            # g.changeWeight(_f.get('mgen_weight_add'), 'auto', 0, 0, 'auto')
            g.stroke(
                "caligraphic",
                _f.get("mgen_weight_add"),
                _f.get("mgen_weight_add"),
                45,
                "removeinternal",
            )
            # g.stroke("circular", _f.get('mgen_weight_add'), 'butt', 'round', 'removeinternal')

    ignoring_center = [
        0x3001,
        0x3002,
        0x3008,
        0x3009,
        0x300A,
        0x300B,
        0x300C,
        0x300D,
        0x300E,
        0x300F,
        0x3010,
        0x3011,
        0x3014,
        0x3015,
        0x3016,
        0x3017,
        0x3018,
        0x3019,
        0x301A,
        0x301B,
        0x301D,
        0x301E,
        0x3099,
        0x309A,
        0x309B,
        0x309C,
    ]
    FULLWIDTH_LEFT_BRACKETS = (0xFF08, 0xFF3B, 0xFF5B, 0xFF5F)
    FULLWIDTH_RIGHT_BRACKETS = (0xFF09, 0xFF3D, 0xFF5D, 0xFF60)
    log("transform Mgen+")
    for g in mgenplus.glyphs():
        g.transform((1.82, 0, 0, 1.82, 0, 0))
        full_half_threshold = 1600
        if _f.get("italic"):
            g.transform(psMat.skew(0.25))
            skew_amount = g.font.ascent * 0.91 * 0.25
            g.width = g.width + skew_amount
            full_half_threshold += skew_amount
        if g.width > full_half_threshold:
            width = 2400
        else:
            width = 1200
        g.transform(psMat.translate((width - g.width) / 2, 0))
        g.width = width
        if g.encoding in ignoring_center:
            pass
        else:
            g = align_to_center(g)
        if g.encoding in FULLWIDTH_LEFT_BRACKETS:
            # 全角左カッコ→右寄せ
            width = g.width  # 1200
            # g.right_side_bearing = g.right_side_bearing - 300
            g.transform(psMat.translate(500, 0))
            g.width = width
        elif g.encoding in FULLWIDTH_RIGHT_BRACKETS:
            # 全角右カッコ→左寄せ
            width = g.width  # 1200
            # g.left_side_bearing = g.left_side_bearing - 300
            g.transform(psMat.translate(-500, 0))
            g.width = width

    log("modify border glyphs")
    for g in mgenplus.glyphs():
        if g.isWorthOutputting:
            if _f.get("italic"):
                g.transform(psMat.skew(0.25))
            if g.encoding >= 0x2500 and g.encoding <= 0x257F:
                # 全角の罫線を0xf0000以降に退避
                mgenplus.selection.select(g.encoding)
                mgenplus.copy()
                mgenplus.selection.select(g.encoding + 0xF0000)
                mgenplus.paste()
            mgenplus.selection.select(g.encoding)
            mgenplus.copy()
            try:
                juliamono.selection.select(g.encoding)
                juliamono.paste()
            except Exception as ex:
                log("WARN: " + str(ex))

    juliamono = reiwa(juliamono, _f.get("weight_name"))

    log("fix_overflow()")
    for g in juliamono.glyphs():
        g = fix_overflow(g)
    juliamono.ascent = ASCENT
    juliamono.descent = DESCENT
    juliamono.upos = 45
    juliamono.fontname = _f.get("family")
    juliamono.familyname = _f.get("family")
    juliamono.fullname = _f.get("name")
    juliamono.weight = _f.get("weight_name")
    # juliamono = set_os2_values(juliamono, _f, juliamono)
    juliamono.appendSFNTName(0x411, 0, COPYRIGHT)
    juliamono.appendSFNTName(0x411, 1, _f.get("family"))
    juliamono.appendSFNTName(0x411, 2, _f.get("style_name"))
    # juliamono.appendSFNTName(0x411,3, "")
    juliamono.appendSFNTName(0x411, 4, _f.get("name"))
    juliamono.appendSFNTName(0x411, 5, "Version " + VERSION)
    juliamono.appendSFNTName(0x411, 6, _f.get("family") + "-" + _f.get("weight_name"))
    # juliamono.appendSFNTName(0x411,7, "")
    # juliamono.appendSFNTName(0x411,8, "")
    # juliamono.appendSFNTName(0x411,9, "")
    # juliamono.appendSFNTName(0x411,10, "")
    # juliamono.appendSFNTName(0x411,11, "")
    # juliamono.appendSFNTName(0x411,12, "")
    juliamono.appendSFNTName(0x411, 13, LICENSE)
    # juliamono.appendSFNTName(0x411,14, "")
    # juliamono.appendSFNTName(0x411,15, "")
    juliamono.appendSFNTName(0x411, 16, _f.get("family"))
    juliamono.appendSFNTName(0x411, 17, _f.get("style_name"))
    juliamono.appendSFNTName(0x409, 0, COPYRIGHT)
    juliamono.appendSFNTName(0x409, 1, _f.get("family"))
    juliamono.appendSFNTName(0x409, 2, _f.get("style_name"))
    juliamono.appendSFNTName(
        0x409, 3, VERSION + ";" + _f.get("family") + "-" + _f.get("style_name")
    )
    juliamono.appendSFNTName(0x409, 4, _f.get("name"))
    juliamono.appendSFNTName(0x409, 5, "Version " + VERSION)
    juliamono.appendSFNTName(0x409, 6, _f.get("name"))
    # juliamono.appendSFNTName(0x409,7, "")
    # juliamono.appendSFNTName(0x409,8, "")
    # juliamono.appendSFNTName(0x409,9, "")
    # juliamono.appendSFNTName(0x409,10, "")
    # juliamono.appendSFNTName(0x409,11, "")
    # juliamono.appendSFNTName(0x409,12, "")
    juliamono.appendSFNTName(0x409, 13, LICENSE)
    # juliamono.appendSFNTName(0x409,14, "")
    # juliamono.appendSFNTName(0x409,15, "")
    juliamono.appendSFNTName(0x409, 16, _f.get("family"))
    juliamono.appendSFNTName(0x409, 17, _f.get("style_name"))
    fontpath = "./dist/%s" % _f.get("filename")

    juliamono.generate(fontpath)

    mgenplus.close()
    juliamono.close()


def main():
    check_files()
    for _f in fonts:
        log("Started: dist/" + _f["filename"])
        build_font(_f)
        log("Finished: dist/" + _f["filename"])
        log("")


if __name__ == "__main__":
    main()
