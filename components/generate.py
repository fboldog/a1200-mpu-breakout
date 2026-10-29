#!/usr/bin/env python3
"""Generate KiCad 9/10 library parts for Amiga 1200 chips fitted in
surface-mount PLCC sockets.

Parts:
  U13  keyboard MCU, Commodore 391508-01/-02 = Motorola MC68HC05C4A / C12, PLCC-44
  U4   Lisa AGA display controller, Commodore 391227-01, PLCC-84

Outputs (relative to this script):
  Amiga_Sockets.kicad_sym                     symbol library (all parts)
  Amiga_Sockets.pretty/<footprint>.kicad_mod  one footprint per part
  Amiga_Sockets.3dshapes/PLCC-84_SMD-Socket.step  (only if CadQuery is importable)
  The PLCC-44 uses the vendor model Amiga_Sockets.3dshapes/69802-144LF.STEP
  (Amphenol/FCI 69802-144LF from DigiKey/SnapMagic, see 69802-144LF.License.txt).

Pinout sources:
  MC68HC05C4A General Release Specification Rev 4.0, Figure 1-4
  Commodore Lisa (391227) IC specification 08/15/91, section 1.2 / 2.2,
  cross-checked with the Aminet docs/hard/pinouts "aa-lisa-plcc" diagram.
"""
import os
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = "Amiga_Sockets"

BI, IN, OUT, PWR, NC = "bidirectional", "input", "output", "power_in", "no_connect"

# ---------------------------------------------------------------- U13 68HC05
HC05_PINS = {
    1: ("~{RESET}", BI), 2: ("~{IRQ}", IN), 3: ("NC", NC),
    4: ("NC", NC),  # tie to VDD if an MC68HC705C4A OTP is fitted
    5: ("PA7", BI), 6: ("PA6", BI), 7: ("PA5", BI), 8: ("PA4", BI),
    9: ("PA3", BI), 10: ("PA2", BI), 11: ("PA1", BI), 12: ("PA0", BI),
    13: ("PB0", BI), 14: ("PB1", BI), 15: ("PB2", BI), 16: ("PB3", BI),
    17: ("PB4", BI), 18: ("NC", NC), 19: ("PB5", BI), 20: ("PB6", BI),
    21: ("PB7", BI), 22: ("VSS", PWR), 23: ("NC", NC), 24: ("PC7", BI),
    25: ("PC6", BI), 26: ("PC5", BI), 27: ("PC4", BI), 28: ("PC3", BI),
    29: ("PC2", BI), 30: ("PC1", BI), 31: ("PC0", BI), 32: ("PD0/RDI", BI),
    33: ("PD1/TDO", BI), 34: ("PD2/MISO", BI), 35: ("PD3/MOSI", BI),
    36: ("PD4/SCK", BI), 37: ("PD5/~{SS}", BI), 38: ("TCMP", OUT),
    39: ("PD7", IN), 40: ("NC", NC), 41: ("TCAP", IN), 42: ("OSC2", OUT),
    43: ("OSC1", IN), 44: ("VDD", PWR),
}

# ---------------------------------------------------------------- U4 Lisa
LISA_PINS = {
    1: ("VSS", PWR), 9: ("~{CAS}", IN), 10: ("CCK", IN), 11: ("WIDE", OUT),
    20: ("MDAT", IN), 21: ("~{MLD}", OUT), 22: ("SCLK", OUT), 23: ("C14O", OUT),
    24: ("~{RST}", IN), 25: ("C28M", IN), 26: ("SOG", OUT), 27: ("BLANK", OUT),
    28: ("ZD", OUT), 29: ("B0", OUT), 30: ("VDD", PWR), 31: ("B1", OUT),
    32: ("B2", OUT), 33: ("VSS", PWR), 34: ("B3", OUT), 35: ("B4", OUT),
    36: ("B5", OUT), 37: ("B6", OUT), 38: ("B7", OUT), 39: ("G0", OUT),
    40: ("G1", OUT), 41: ("G2", OUT), 42: ("G3", OUT), 43: ("C28OUT", OUT),
    44: ("G4", OUT), 45: ("G5", OUT), 46: ("G6", OUT), 47: ("G7", OUT),
    48: ("R0", OUT), 49: ("R1", OUT), 50: ("R2", OUT), 51: ("R3", OUT),
    52: ("R4", OUT), 53: ("VSS", PWR), 54: ("R5", OUT), 55: ("R6", OUT),
    56: ("VDD", PWR), 57: ("R7", OUT), 58: ("~{BRST}", OUT), 83: ("VDD", PWR),
}
for i in range(7):                       # pins 2..8 = D6..D0
    LISA_PINS[2 + i] = (f"D{6 - i}", BI)
for i in range(8):                       # pins 12..19 = RGA8..RGA1
    LISA_PINS[12 + i] = (f"RGA{8 - i}", IN)
for i in range(24):                      # pins 59..82 = D31..D8
    LISA_PINS[59 + i] = (f"D{31 - i}", BI)
LISA_PINS[84] = ("D7", BI)
assert sorted(LISA_PINS) == list(range(1, 85))


def by_name(pins, *names):
    rev = {}
    for n, (name, _) in pins.items():
        rev.setdefault(name, []).append(n)
    return [rev[x][0] if x else None for x in names]


PARTS = [
    dict(
        pins=HC05_PINS, n=44,
        sym="A1200_U13_MC68HC05C4A_PLCC44", value="MC68HC05C4A",
        fp="PLCC-44_SMD-Socket_A1200_U13", # Vendor STEP (SnapMagic via DigiKey), Y-up -> KiCad rotate -90 about X
        model="69802-144LF.STEP", model_rotate=(-90, 0, 0), vendor_model=True,
        socket="amphenol_69802",
        half_w=12.7,
        left=by_name(HC05_PINS, "~{RESET}", "~{IRQ}", "OSC1", "OSC2", "TCAP", "TCMP", None,
                     *[f"PA{i}" for i in range(8)]),
        right=by_name(HC05_PINS, *[f"PB{i}" for i in range(8)], None,
                      *[f"PC{i}" for i in range(8)], None,
                      "PD0/RDI", "PD1/TDO", "PD2/MISO", "PD3/MOSI", "PD4/SCK", "PD5/~{SS}", "PD7"),
        datasheet="https://archive.retro.co.za/CDROMs/Motorola/CDMCU-D-RevA-Vol1/pdf/DATABOOK/05C4AGRS.pdf",
        desc="Amiga 1200 U13 keyboard MCU, Commodore 391508-01/-02 "
             "(Motorola MC68HC05C4A / MC68HC05C12), 44-lead PLCC in SMD socket",
        keywords="Amiga 1200 A1200 U13 keyboard 68HC05 391508 MCU PLCC44 socket",
        fp_descr="PLCC-44 surface mount socket Amphenol/FCI 69802-144LF (LCSC C3170578), Amiga 1200 U13 keyboard MCU (MC68HC05C4A / 391508-01), https://www.lcsc.com/datasheet/C3170578.pdf",
        fp_tags="plcc smt socket amiga a1200 u13 68hc05",
    ),
    dict(
        pins=LISA_PINS, n=84,
        sym="A1200_U4_Lisa_391227_PLCC84", value="Lisa_391227-01",
        fp="PLCC-84_SMD-Socket_A1200_U4",
        # Vendor STEP (Assmann WSW via TraceParts), Y-up -> KiCad rotate -90 about X
        model="A-CCS_084-Z-SM.stp", model_rotate=(-90, 0, 0), vendor_model=True,
        socket="assmann_accs",
        half_w=12.7,
        left=by_name(LISA_PINS, *[f"RGA{i}" for i in range(1, 9)], None,
                     "CCK", "~{CAS}", "C28M", "~{RST}", "MDAT", None,
                     *[f"D{i}" for i in range(32)]),
        right=by_name(LISA_PINS, "C28OUT", "C14O", "SCLK", "~{MLD}", "WIDE", None,
                      *[f"R{i}" for i in range(8)], None,
                      *[f"G{i}" for i in range(8)], None,
                      *[f"B{i}" for i in range(8)], None,
                      "BLANK", "SOG", "ZD", "~{BRST}"),
        datasheet="https://oldcrap.org/wp-content/uploads/2023/04/amiga-all-spec-lisa-391227.pdf",
        desc="Amiga 1200 U4 Lisa AGA display controller, Commodore 391227-01, "
             "84-lead PLCC in SMD socket",
        keywords="Amiga 1200 A1200 U4 Lisa AGA video denise 391227 PLCC84 socket",
        fp_descr="PLCC-84 surface mount socket Assmann WSW A-CCS 084-Z-SM (no location peg), Amiga 1200 U4 Lisa (391227-01), "
                 "https://www.assmann-wsw.com/uploads/datasheets/ASS_0142_CO.pdf",
        fp_tags="plcc smt socket amiga a1200 u4 lisa aga",
    ),
]


UPSIDE_DOWN_SUFFIX = "_UpsideDown"
UPSIDE_DOWN_ROTZ = 90  # extra model turn that puts the socket key over the chip's bevel


def uid():
    return str(uuid.uuid4())


# --------------------------------------------------------------------------
# Symbol
# --------------------------------------------------------------------------
def sym_pin(pins, num, x, y, rot, length=2.54, hide=False):
    name, etype = pins[num]
    return (
        f'\t\t\t(pin {etype} line\n'
        f'\t\t\t\t(at {x:g} {y:g} {rot})\n'
        f'\t\t\t\t(length {length:g})\n'
        + ('\t\t\t\t(hide yes)\n' if hide else '')
        + f'\t\t\t\t(name "{name}"\n\t\t\t\t\t(effects\n\t\t\t\t\t\t(font\n\t\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t\t)\n\t\t\t\t\t)\n\t\t\t\t)\n'
        f'\t\t\t\t(number "{num}"\n\t\t\t\t\t(effects\n\t\t\t\t\t\t(font\n\t\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t\t)\n\t\t\t\t\t)\n\t\t\t\t)\n'
        f'\t\t\t)\n'
    )


def prop(name, value, x, y, hide=False, justify=None):
    eff = '\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n'
    if justify:
        eff += f'\t\t\t\t(justify {justify})\n'
    if hide:
        eff += '\t\t\t\t(hide yes)\n'
    value = value.replace('"', '\\"')
    return (
        f'\t\t(property "{name}" "{value}"\n'
        f'\t\t\t(at {x:g} {y:g} 0)\n'
        f'\t\t\t(effects\n{eff}\t\t\t)\n'
        f'\t\t)\n'
    )


def make_symbol(part):
    P = 2.54
    W = part["half_w"]
    pins_def = part["pins"]
    name = part["sym"]
    left, right = part["left"], part["right"]
    n = max(len(left), len(right))
    top_y = round(((n - 1) * P / 2) / P) * P
    body_top = top_y + P
    body_bot = top_y - (n - 1) * P - P

    pins = ""
    for i, num in enumerate(left):
        if num:
            pins += sym_pin(pins_def, num, -W - 5.08, top_y - i * P, 0, 5.08)
    for i, num in enumerate(right):
        if num:
            pins += sym_pin(pins_def, num, W + 5.08, top_y - i * P, 180, 5.08)
    # Power pins: VDD on top, VSS at the bottom, one stub per physical pin
    vdd = sorted(k for k, v in pins_def.items() if v[0] == "VDD")
    vss = sorted(k for k, v in pins_def.items() if v[0] == "VSS")
    for group, y, rot in ((vdd, body_top + 5.08, 270), (vss, body_bot - 5.08, 90)):
        x0 = -(len(group) - 1) * P / 2
        for i, num in enumerate(group):
            pins += sym_pin(pins_def, num, x0 + i * P, y, rot, 5.08)
    placed = set(left) | set(right) | set(vdd) | set(vss)
    for num in sorted(k for k, v in pins_def.items() if v[1] == NC):
        pins += sym_pin(pins_def, num, -W, body_bot + P, 0, 0, hide=True)
        placed.add(num)
    assert placed - {None} == set(pins_def), f"{name}: unplaced pins"

    vdd_w = (len(vdd) - 1) * P / 2 + 2.54
    return (
        f'\t(symbol "{name}"\n'
        '\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n'
        + prop("Reference", "U", -W, body_top + 1.27, justify="left bottom")
        + prop("Value", part["value"], vdd_w, body_top + 1.27, justify="left bottom")
        # The adapter presses the socket face-down onto the chip, so default to that variant
        + prop("Footprint", f'{LIB}:{part["fp"]}{UPSIDE_DOWN_SUFFIX}', 0, body_bot - 7.62, hide=True)
        + prop("Datasheet", part["datasheet"], 0, body_bot - 10.16, hide=True)
        + prop("Description", part["desc"], 0, body_bot - 12.7, hide=True)
        + prop("ki_keywords", part["keywords"], 0, 0, hide=True)
        + prop("ki_fp_filters", f'PLCC*{part["n"]}*', 0, 0, hide=True)
        + f'\t\t(symbol "{name}_0_1"\n'
        f'\t\t\t(rectangle\n\t\t\t\t(start {-W:g} {body_top:g})\n\t\t\t\t(end {W:g} {body_bot:g})\n'
        '\t\t\t\t(stroke\n\t\t\t\t\t(width 0.254)\n\t\t\t\t\t(type default)\n\t\t\t\t)\n'
        '\t\t\t\t(fill\n\t\t\t\t\t(type background)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n'
        f'\t\t(symbol "{name}_1_1"\n{pins}\t\t)\n'
        '\t\t(embedded_fonts no)\n'
        '\t)\n'
    )


def make_symbol_lib():
    return ('(kicad_symbol_lib\n\t(version 20241209)\n\t(generator "amiga_sockets_gen")\n'
            '\t(generator_version "9.0")\n' + "".join(make_symbol(p) for p in PARTS) + ')\n')


# --------------------------------------------------------------------------
# Footprint
#   generic:        pad geometry of KiCad's Package_LCC:PLCC-<n>_SMD-Socket
#   amphenol_69802: Amphenol/FCI 69802 PLCC SMT socket, drawing 69802 rev AG
#                   (Fig. 1 recommended PCB layout, Table I dimensions)
# --------------------------------------------------------------------------
PITCH = 1.27


def geometry(part):
    """Socket dimensions for a part (half sizes from the package centre)."""
    n = part["n"]
    k = n // 4                        # pins per side
    if part["socket"] == "assmann_accs":
        # Assmann WSW A-CCS 0xx-Z-SM, drawing ASS 0142 CO rev12: pads 0.76 x 1.70,
        # row centre taken from the contact feet in the vendor STEP (13.55..15.35)
        assert n == 84, "only the 84-pin A-CCS is described here"
        return dict(
            k=k,
            pad_c=14.45,
            pad_l=1.70,
            pad_w=0.76,
            body=35.90 / 2,           # DIM A/B
            crt=35.90 / 2 + 0.25,
            cav=14.45 + 1.70 / 2,
            chamfer=1.0,
        )
    if part["socket"] == "amphenol_69802":
        assert n == 44, "only the 44-pin 69802 is described here"
        return dict(
            k=k,
            pad_c=16.10 / 2,          # DIM F/G: pad row centre-to-centre
            pad_l=1.91,
            pad_w=0.76,
            body=22.86 / 2,           # DIM B
            crt=22.86 / 2 + 0.25,
            cav=17.78 / 2,            # chip cavity incl. contact slots
            chamfer=2.50,             # pin-1 corner chamfer (vendor footprint)
            height=4.47,
        )
    grow = (k - 11) / 2 * PITCH       # growth vs. PLCC-44 per side
    pad_c = 7.8625 + grow             # pad centre distance from package centre
    return dict(
        k=k,
        pad_c=pad_c,
        pad_l=1.925,
        pad_w=0.7,
        body=11.64 + grow,            # socket body half size (44: 11.64, 84: 17.99)
        crt=12.1 + grow,              # courtyard half size
        cav=pad_c + 1.925 / 2,        # chip cavity half size
        chamfer=1.0,
        height=4.2,
    )


def pad_positions(part):
    """Yield (number, x, y, horizontal) in KiCad coordinates (y down)."""
    n = part["n"]
    g = geometry(part)
    k, c = g["k"], g["pad_c"]
    h = (k + 1) // 2                  # pads on the top-left half incl. pin 1
    m = (k + 1) // 2                  # index of the centre pad on a side
    for p in range(1, n + 1):
        if p <= h:                    # top, centre -> left
            yield p, -(p - 1) * PITCH, -c, False
        elif p <= h + k:              # left, top -> bottom
            yield p, -c, (p - h - m) * PITCH, True
        elif p <= h + 2 * k:          # bottom, left -> right
            yield p, (p - h - k - m) * PITCH, c, False
        elif p <= h + 3 * k:          # right, bottom -> top
            yield p, c, -(p - h - 2 * k - m) * PITCH, True
        else:                         # top, right -> centre
            yield p, (n + 1 - p) * PITCH, -c, False


def fp_line(x1, y1, x2, y2, layer, w):
    return (f'\t(fp_line\n\t\t(start {x1:g} {y1:g})\n\t\t(end {x2:g} {y2:g})\n'
            f'\t\t(stroke\n\t\t\t(width {w:g})\n\t\t\t(type solid)\n\t\t)\n'
            f'\t\t(layer "{layer}")\n\t\t(uuid "{uid()}")\n\t)\n')


def fp_poly(pts, layer, w):
    s = ""
    for a, b in zip(pts, pts[1:] + pts[:1]):
        s += fp_line(*a, *b, layer, w)
    return s


def fp_text_prop(name, value, x, y, layer, hide=False):
    return (f'\t(property "{name}" "{value}"\n\t\t(at {x:g} {y:g} 0)\n'
            + ('\t\t(unlocked yes)\n' if name not in ("Reference", "Value") else '')
            + f'\t\t(layer "{layer}")\n'
            + ('\t\t(hide yes)\n' if hide else '')
            + f'\t\t(uuid "{uid()}")\n'
            '\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1 1)\n\t\t\t\t(thickness 0.15)\n\t\t\t)\n\t\t)\n\t)\n')


def make_footprint(part, upside_down=False):
    """Normal socket footprint, or the upside-down variant.

    Upside-down: the socket is soldered to the bottom (B.Cu) of an adapter and
    pressed face-down over the chip soldered on the Amiga board.  Seen from
    above, the socket's own contacts then run clockwise while the chip's pins
    run counter-clockwise, so pad numbers here are chip pin numbers: the pad
    pattern is the mirror of the normal one (KiCad's flip to B.Cu mirrors it
    back), and the model is turned so its key lands over the chip's bevel.
    """
    n = part["n"]
    g = geometry(part)
    m = -1 if upside_down else 1      # x mirror for the upside-down variant
    name = part["fp"] + (UPSIDE_DOWN_SUFFIX if upside_down else "")
    descr = part["fp_descr"]
    if upside_down:
        descr = ("UPSIDE-DOWN: place on B.Cu, socket pressed over the soldered chip; "
                 "pad numbers are chip pins. " + descr)

    def line(x1, y1, x2, y2, layer, w):
        return fp_line(m * x1, y1, m * x2, y2, layer, w)

    def poly(pts, layer, w):
        return fp_poly([(m * x, y) for x, y in pts], layer, w)

    b, crt, ch = round(g["body"], 4), round(g["crt"], 4), g["chamfer"]
    # Relative paths resolve against the footprint library dir, so this works from any project
    model_path = "../" + LIB + ".3dshapes/" + part["model"]
    s = (f'(footprint "{name}"\n\t(version 20241229)\n\t(generator "amiga_sockets_gen")\n'
         '\t(generator_version "9.0")\n\t(layer "F.Cu")\n'
         f'\t(descr "{descr}")\n'
         f'\t(tags "{part["fp_tags"]}")\n')
    s += fp_text_prop("Reference", "REF**", 0, -crt - 1.0, "F.SilkS")
    s += fp_text_prop("Value", name, 0, crt + 1.0, "F.Fab")
    s += fp_text_prop("Datasheet", "", 0, 0, "F.Fab", hide=True)
    s += fp_text_prop("Description", "", 0, 0, "F.Fab", hide=True)
    s += '\t(attr smd)\n\t(duplicate_pad_numbers_are_jumpers no)\n'

    # Fab: socket outline with chamfered pin-1 corner (top-left), chip cavity
    s += poly([(-b + ch, -b), (b, -b), (b, b), (-b, b), (-b, -b + ch)], "F.Fab", 0.1)
    c = round(g["cav"], 4)
    s += poly([(-c + 1, -c), (c, -c), (c, c), (-c, c), (-c, -c + 1)], "F.Fab", 0.1)
    s += line(-0.5, -b, 0, -b + 1, "F.Fab", 0.1)
    s += line(0, -b + 1, 0.5, -b, "F.Fab", 0.1)
    # Silkscreen: outline 0.15 outside body, chamfer and pin-1 arrow inside the outline
    o = round(b + 0.15, 4)
    s += line(-o + ch, -o, o, -o, "F.SilkS", 0.12)
    s += line(o, -o, o, o, "F.SilkS", 0.12)
    s += line(o, o, -o, o, "F.SilkS", 0.12)
    s += line(-o, o, -o, -o + ch, "F.SilkS", 0.12)
    s += line(-o, -o + ch, -o + ch, -o, "F.SilkS", 0.12)
    s += (f'\t(fp_poly\n\t\t(pts\n\t\t\t(xy 0 {-o + 0.9:g})\n\t\t\t(xy -0.4 {-o + 0.3:g})\n'
          f'\t\t\t(xy 0.4 {-o + 0.3:g})\n\t\t)\n\t\t(stroke\n\t\t\t(width 0.12)\n\t\t\t(type solid)\n\t\t)\n'
          f'\t\t(fill yes)\n\t\t(layer "F.SilkS")\n\t\t(uuid "{uid()}")\n\t)\n')
    # Courtyard
    s += poly([(-crt, -crt), (crt, -crt), (crt, crt), (-crt, crt)], "F.CrtYd", 0.05)
    s += (f'\t(fp_text user "${{REFERENCE}}"\n\t\t(at 0 0 0)\n\t\t(layer "F.Fab")\n'
          f'\t\t(uuid "{uid()}")\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1 1)\n'
          '\t\t\t\t(thickness 0.15)\n\t\t\t)\n\t\t)\n\t)\n')

    for p, x, y, horiz in pad_positions(part):
        w, h = (g["pad_l"], g["pad_w"]) if horiz else (g["pad_w"], g["pad_l"])
        pname, ptype = part["pins"][p]
        s += (f'\t(pad "{p}" smd rect\n\t\t(at {m * x + 0:g} {y:g})\n\t\t(size {w:g} {h:g})\n'
              '\t\t(layers "F.Cu" "F.Mask" "F.Paste")\n'
              f'\t\t(pinfunction "{pname}")\n\t\t(pintype "{ptype}")\n'
              f'\t\t(uuid "{uid()}")\n\t)\n')

    for hx, hy in g.get("holes", []):
        d = g["hole_d"]
        s += (f'\t(pad "" np_thru_hole circle\n\t\t(at {m * hx:g} {hy:g})\n\t\t(size {d:g} {d:g})\n'
              f'\t\t(drill {d:g})\n\t\t(layers "*.Cu" "*.Mask")\n\t\t(uuid "{uid()}")\n\t)\n')

    s += '\t(embedded_fonts no)\n'
    rx, ry, rz = part.get("model_rotate", (0, 0, 0))
    if upside_down:
        rz += UPSIDE_DOWN_ROTZ
    ox, oy, oz = part.get("model_offset", (0, 0, 0))
    s += (f'\t(model "{model_path}"\n\t\t(offset\n\t\t\t(xyz {ox:g} {oy:g} {oz:g})\n\t\t)\n'
          '\t\t(scale\n\t\t\t(xyz 1 1 1)\n\t\t)\n'
          f'\t\t(rotate\n\t\t\t(xyz {rx:g} {ry:g} {rz:g})\n\t\t)\n\t)\n')
    return s + ')\n'


# --------------------------------------------------------------------------
# 3D model: SMD PLCC socket (housing + phosphor-bronze contacts)
# --------------------------------------------------------------------------
def save_step(housing, pins, name, path):
    import cadquery as cq
    asm = cq.Assembly(name=name)
    asm.add(housing, name="housing", color=cq.Color(0.12, 0.12, 0.13))
    asm.add(pins, name="contacts", color=cq.Color(0.85, 0.72, 0.35))
    asm.export(path) if hasattr(asm, "export") else asm.save(path)


def union_all(shapes):
    out = shapes[0]
    for sh in shapes[1:]:
        out = out.union(sh)
    return out


def make_step_generic(part, path):
    import cadquery as cq

    n = part["n"]
    g = geometry(part)
    H = 4.2          # housing height
    STANDOFF = 0.25  # housing raised above PCB (contacts' feet sit below)
    CAV = g["cav"]   # cavity half size (chip body + clearance)
    FLOOR = 1.4      # cavity floor height
    WIN = CAV - 3.8  # half size of the open window in the floor
    PAD_C, PAD_L = g["pad_c"], g["pad_l"]
    b = g["body"]

    # Housing: square block, chamfered pin-1 corner (KiCad top-left -> 3D -x,+y)
    housing = (cq.Workplane("XY").workplane(offset=STANDOFF)
               .rect(2 * b, 2 * b).extrude(H - STANDOFF)
               .edges("|Z").edges("<X and >Y").chamfer(1.0))
    # Chip cavity with chamfered key corner, floor window
    cav = (cq.Workplane("XY").workplane(offset=FLOOR)
           .rect(2 * CAV, 2 * CAV).extrude(H)
           .edges("|Z").edges("<X and >Y").chamfer(1.2))
    housing = housing.cut(cav)
    housing = housing.cut(cq.Workplane("XY").rect(2 * WIN, 2 * WIN).extrude(H))
    # Extraction-tool slots in two opposite corners of the cavity rim
    for sx, sy in ((1, 1), (-1, -1)):
        slot = (cq.Workplane("XY").workplane(offset=H - 1.6)
                .center(sx * (CAV + 0.6), sy * (CAV + 0.6)).rect(2.4, 2.4).extrude(2))
        housing = housing.cut(slot)
    # Contact slots in the cavity walls + contacts
    contacts = []
    for p, x, y, horiz in pad_positions(part):
        X, Y = x, -y  # KiCad y-down -> 3D y-up
        if horiz:
            sgn = 1 if X > 0 else -1
            slot = (cq.Workplane("XY").center(sgn * (CAV + 0.5), Y).rect(1.0, 0.8).extrude(H))
        else:
            sgn = 1 if Y > 0 else -1
            slot = (cq.Workplane("XY").center(X, sgn * (CAV + 0.5)).rect(0.8, 1.0).extrude(H))
        housing = housing.cut(slot)

        # Contact profile in the radial/Z plane (r = distance from centre)
        t, w = 0.2, 0.5
        r0, r1 = PAD_C - PAD_L / 2 + 0.15, PAD_C + PAD_L / 2 - 0.15
        foot = cq.Workplane("XY").box(r1 - r0, w, t, centered=(False, True, False)).translate((r0, 0, 0))
        riser = cq.Workplane("XY").box(t, w, FLOOR + 0.2, centered=(False, True, False)).translate((r1 - t, 0, t))
        spring = (cq.Workplane("XZ").polyline([(CAV + 0.05, FLOOR + 0.4), (CAV - 0.35, FLOOR + 1.4),
                                               (CAV + 0.05, H - 0.7), (CAV + 0.25, H - 0.7),
                                               (CAV - 0.15, FLOOR + 1.4), (CAV + 0.25, FLOOR + 0.4)])
                  .close().extrude(w / 2, both=True))
        bridge = cq.Workplane("XY").box(CAV + 0.25 - (r1 - t), w, t, centered=(False, True, False)).translate((r1 - t, 0, FLOOR + 0.2))
        c = foot.union(riser).union(spring).union(bridge)
        if horiz:
            c = c.rotate((0, 0, 0), (0, 0, 1), 0 if X > 0 else 180).translate((0, Y, 0))
        else:
            c = c.rotate((0, 0, 0), (0, 0, 1), 90 if Y > 0 else -90).translate((X, 0, 0))
        contacts.append(c)

    # Pin-1 dimple on the top face
    housing = housing.cut(cq.Workplane("XY").workplane(offset=H - 0.15)
                          .center(0, b - 1.2).circle(0.5).extrude(1))

    save_step(housing, union_all(contacts), f"PLCC-{n}_SMD-Socket", path)


def main():
    os.makedirs(os.path.join(HERE, LIB + ".pretty"), exist_ok=True)
    os.makedirs(os.path.join(HERE, LIB + ".3dshapes"), exist_ok=True)
    with open(os.path.join(HERE, LIB + ".kicad_sym"), "w") as f:
        f.write(make_symbol_lib())
    for part in PARTS:
        for upside_down in (False, True):
            name = part["fp"] + (UPSIDE_DOWN_SUFFIX if upside_down else "")
            with open(os.path.join(HERE, LIB + ".pretty", name + ".kicad_mod"), "w") as f:
                f.write(make_footprint(part, upside_down))
        if part.get("vendor_model"):
            continue
        try:
            make_step_generic(part, os.path.join(HERE, LIB + ".3dshapes", part["model"]))
        except ImportError:
            print("CadQuery not available: STEP models not regenerated")
            break


if __name__ == "__main__":
    main()
