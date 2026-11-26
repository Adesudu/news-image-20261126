"""Draw a one-page newspaper front page for Thursday 26 November 2026.

Pure Python standard library only: the page is rasterised into an RGB
buffer and encoded as a PNG by hand (zlib + struct), so the entry runs
with no network and no third-party packages. All news copy is baked
into this file; the render is fully deterministic.
"""

import binascii
import math
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

PAPER = (246, 241, 227)
INK = (20, 20, 20)
RED = (176, 30, 36)
NAVY = (31, 52, 84)
GREY = (110, 105, 92)
LIGHT = (255, 255, 255)
GOLD = (198, 156, 48)

# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is 7 rows of 5 bits, most significant bit left.
# ---------------------------------------------------------------------------

FONT = {
    "A": (0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "B": (0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    "C": (0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110),
    "D": (0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110),
    "E": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    "F": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    "G": (0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111),
    "H": (0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "I": (0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "J": (0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    "K": (0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    "L": (0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    "M": (0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    "N": (0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001),
    "O": (0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "P": (0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    "Q": (0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    "R": (0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    "S": (0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    "T": (0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "U": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "V": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "W": (0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b10101, 0b01010),
    "X": (0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001),
    "Y": (0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100),
    "Z": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
    "0": (0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    "1": (0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "2": (0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111),
    "3": (0b11111, 0b00010, 0b00100, 0b00010, 0b00001, 0b10001, 0b01110),
    "4": (0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    "5": (0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110),
    "6": (0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110),
    "7": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000),
    "8": (0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110),
    "9": (0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0b01100, 0b01100),
    ",": (0, 0, 0, 0, 0b01100, 0b00100, 0b01000),
    ":": (0, 0b01100, 0b01100, 0, 0b01100, 0b01100, 0),
    ";": (0, 0b01100, 0b01100, 0, 0b01100, 0b00100, 0b01000),
    "!": (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0, 0b00100),
    "?": (0b01110, 0b10001, 0b00001, 0b00110, 0b00100, 0, 0b00100),
    "'": (0b00100, 0b00100, 0b01000, 0, 0, 0, 0),
    '"': (0b01010, 0b01010, 0, 0, 0, 0, 0),
    "-": (0, 0, 0, 0b01110, 0, 0, 0),
    "/": (0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000),
    "(": (0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010),
    ")": (0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000),
    "%": (0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011),
    "&": (0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101),
    "$": (0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100),
    "#": (0b01010, 0b01010, 0b11111, 0b01010, 0b11111, 0b01010, 0b01010),
    "@": (0b01110, 0b10001, 0b10111, 0b10101, 0b10110, 0b10000, 0b01110),
    "+": (0, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0),
    "=": (0, 0, 0b11111, 0, 0b11111, 0, 0),
    "_": (0, 0, 0, 0, 0, 0, 0b11111),
    "*": (0, 0b01010, 0b00100, 0b11111, 0b00100, 0b01010, 0),
    "<": (0b00010, 0b00100, 0b01000, 0b10000, 0b01000, 0b00100, 0b00010),
    ">": (0b01000, 0b00100, 0b00010, 0b00001, 0b00010, 0b00100, 0b01000),
    "\u2022": (0, 0, 0b01100, 0b01100, 0b01100, 0, 0),
}

CHAR_ADVANCE = 6  # 5 px glyph + 1 px gap, in font units


def text_width(text, scale):
    """Width in pixels of `text` rendered at `scale`."""
    return len(text) * CHAR_ADVANCE * scale - scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines fitting max_width px."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------------------
# Canvas: an RGB pixel buffer with tiny drawing primitives.
# ---------------------------------------------------------------------------

class Page:
    def __init__(self, width=WIDTH, height=HEIGHT):
        self.width = width
        self.height = height
        self.pixels = bytearray(PAPER * (width * height))

    def _offset(self, x, y):
        return (y * self.width + x) * 3

    def set_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            off = self._offset(x, y)
            self.pixels[off:off + 3] = bytes(color)

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            off = self._offset(x0, yy)
            self.pixels[off:off + len(row)] = row

    def hline(self, x, y, w, color, thickness=1):
        self.fill_rect(x, y, w, thickness, color)

    def vline(self, x, y, h, color, thickness=1):
        self.fill_rect(x, y, thickness, h, color)

    def rect_outline(self, x, y, w, h, color, thickness=1):
        self.fill_rect(x, y, w, thickness, color)
        self.fill_rect(x, y + h - thickness, w, thickness, color)
        self.fill_rect(x, y, thickness, h, color)
        self.fill_rect(x + w - thickness, y, thickness, h, color)

    def filled_circle(self, cx, cy, radius, color):
        for dy in range(-radius, radius + 1):
            dx = int(math.sqrt(radius * radius - dy * dy))
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def circle_outline(self, cx, cy, radius, color, thickness=2):
        for dy in range(-radius, radius + 1):
            dx = int(math.sqrt(radius * radius - dy * dy))
            for t in range(thickness):
                self.set_pixel(cx - dx + t, cy + dy, color)
                self.set_pixel(cx + dx - t, cy + dy, color)

    def draw_char(self, x, y, char, scale, color):
        glyph = FONT.get(char.upper(), FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    self.fill_rect(
                        x + col * scale, y + row * scale, scale, scale, color
                    )

    def draw_text(self, x, y, text, scale, color):
        for i, char in enumerate(text):
            self.draw_char(x + i * CHAR_ADVANCE * scale, y, char, scale, color)

    def draw_text_centered(self, cx, y, text, scale, color):
        self.draw_text(cx - text_width(text, scale) // 2, y, text, scale, color)

    def draw_wrapped(self, x, y, text, max_width, scale, color, leading=None):
        """Draw wrapped text; returns the y just below the last line."""
        if leading is None:
            leading = 7 * scale + 4
        for line in wrap_text(text, max_width, scale):
            self.draw_text(x, y, line, scale, color)
            y += leading
        return y


# ---------------------------------------------------------------------------
# PNG encoding (pure stdlib).
# ---------------------------------------------------------------------------

def _chunk(tag, data):
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)
    )


def encode_png(page):
    raw = bytearray()
    stride = page.width * 3
    for y in range(page.height):
        raw.append(0)  # filter: none
        raw += page.pixels[y * stride:(y + 1) * stride]
    compressed = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack(">IIBBBBB", page.width, page.height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", compressed)
        + _chunk(b"IEND", b"")
    )


# ---------------------------------------------------------------------------
# The day's news (Thursday 26 November 2026), as reported that day.
# ---------------------------------------------------------------------------

LEAD_KICKER = "TECHNOLOGY - LEAD STORY"
LEAD_HEADLINE = ["HUANG QUITS AS", "NVIDIA CHIEF"]
LEAD_DECK = (
    "FOUNDER JENSEN HUANG STEPS DOWN AMID ESPIONAGE PROBES, THROWING THE "
    "WORLD'S TOP CHIPMAKER INTO A SUCCESSION SCRAMBLE. SHARES FELL 5%."
)

STORIES = [
    (
        "SPACE",
        "SPACEX CLEARED FOR A MILLION SATELLITES",
        "US REGULATORS APPROVE THE STARMIND NETWORK OF ORBITAL DATA "
        "CENTRES, THE LARGEST CONSTELLATION EVER AUTHORISED.",
    ),
    (
        "UKRAINE WAR",
        "RUSSIA'S OWN TALLY: NEARLY 500,000 DEAD",
        "MOSCOW'S FIGURES PUT ITS MILITARY DEATHS IN UKRAINE AT ALMOST "
        "HALF A MILLION SINCE THE WAR BEGAN.",
    ),
    (
        "AMERICA",
        "DEMOCRATS RETAKE CONGRESS",
        "THE OPPOSITION SWEEPS BACK TO POWER IN THE MIDTERMS, A RESURGENT "
        "VICTORY OVER THE REPUBLICANS.",
    ),
    (
        "SCIENCE",
        "BEPICOLOMBO REACHES MERCURY",
        "AFTER AN EIGHT-YEAR VOYAGE, THE EUROPEAN-JAPANESE PROBE ENTERS "
        "ORBIT AROUND THE SUN'S CLOSEST PLANET.",
    ),
]

BRIEFS = [
    "PAKISTAN'S FIRST ASTRONAUT RIDES TO CHINA'S TIANGONG STATION",
    "CAIRO TANKER FIRE KILLS AT LEAST 30",
    "DURAN DURAN GUITARIST ANDY TAYLOR DIES AT 65",
    "NORWAY COURT VOIDS DISPUTED OIL LICENCES",
    "KENYA'S LAST EBOLA PATIENT GOES HOME; DRC TOLL PASSES 5,300",
    "HUAWEI CONVICTED OF FRAUD IN US TRIAL",
    "COLOMBIAN POLICE FREE 20 HOSTAGES AFTER 17-HOUR SIEGE",
    "GUKESH AND SINDAROV DRAW GAME 2 OF CHESS TITLE MATCH",
    "EU HUNTS NEW ECB CHIEF AS LAGARDE RESIGNS",
    "INDIA MARKS CONSTITUTION DAY, URGES HUMAN CONTROL OF AI ARMS",
]


# ---------------------------------------------------------------------------
# Page layout.
# ---------------------------------------------------------------------------

MARGIN = 36
CONTENT_W = WIDTH - 2 * MARGIN


def draw_masthead(page):
    page.draw_text_centered(
        WIDTH // 2, 40, "THE WORLD TODAY", 7, INK
    )
    page.draw_text_centered(
        WIDTH // 2, 106, "THURSDAY, 26 NOVEMBER 2026", 2, RED
    )
    page.hline(MARGIN, 132, CONTENT_W, INK, 4)
    page.hline(MARGIN, 140, CONTENT_W, INK, 1)


def draw_lead_art(page, x, y, w, h):
    """A dark panel with a simple chip drawing for the lead story."""
    page.fill_rect(x, y, w, h, NAVY)
    page.draw_text_centered(x + w // 2, y + 12, "NVIDIA", 3, LIGHT)
    # Chip body with pins.
    chip_w, chip_h = 92, 92
    chip_x = x + (w - chip_w) // 2
    chip_y = y + 52
    page.fill_rect(chip_x, chip_y, chip_w, chip_h, LIGHT)
    page.rect_outline(chip_x, chip_y, chip_w, chip_h, GOLD, 3)
    page.fill_rect(chip_x + 26, chip_y + 26, 40, 40, NAVY)
    page.draw_text_centered(
        chip_x + chip_w // 2, chip_y + 38, "NV", 2, LIGHT
    )
    for i in range(5):
        pin_y = chip_y + 12 + i * 17
        page.fill_rect(chip_x - 12, pin_y, 12, 5, GOLD)
        page.fill_rect(chip_x + chip_w, pin_y, 12, 5, GOLD)
        pin_x = chip_x + 12 + i * 17
        page.fill_rect(pin_x, chip_y - 12, 5, 12, GOLD)
        page.fill_rect(pin_x, chip_y + chip_h, 5, 12, GOLD)
    page.draw_text_centered(
        x + w // 2, y + h - 26, "THE CHIP KING STEPS DOWN", 2, LIGHT
    )


def draw_lead(page):
    y = 156
    page.draw_text(MARGIN, y, LEAD_KICKER, 2, RED)
    head_y = y + 26
    for i, line in enumerate(LEAD_HEADLINE):
        page.draw_text(MARGIN, head_y + i * 42, line, 5, INK)
    deck_y = head_y + 2 * 42 + 14
    page.draw_wrapped(MARGIN, deck_y, LEAD_DECK, 600, 2, INK)
    draw_lead_art(page, 668, y, 320, 178)
    page.hline(MARGIN, 352, CONTENT_W, INK, 2)


def draw_story(page, x, y, w, kicker, headline, body):
    page.draw_text(x, y, kicker, 2, RED)
    y += 22
    for line in wrap_text(headline, w, 3):
        page.draw_text(x, y, line, 3, INK)
        y += 26
    y += 6
    page.draw_wrapped(x, y, body, w, 2, INK)
    return y


def draw_middle(page):
    col_w = (CONTENT_W - 24) // 2
    left_x = MARGIN
    right_x = MARGIN + col_w + 24
    y1 = 368
    draw_story(page, left_x, y1, col_w, *STORIES[0])
    draw_story(page, right_x, y1, col_w, *STORIES[1])
    page.hline(MARGIN, 506, CONTENT_W, GREY, 1)
    y2 = 522
    draw_story(page, left_x, y2, col_w, *STORIES[2])
    draw_story(page, right_x, y2, col_w, *STORIES[3])
    page.hline(MARGIN, 668, CONTENT_W, INK, 2)


def draw_briefs(page):
    y = 684
    page.draw_text(MARGIN, y, "ALSO TODAY", 3, INK)
    page.hline(MARGIN, y + 26, CONTENT_W, INK, 1)
    col_w = (CONTENT_W - 24) // 2
    left_x = MARGIN
    right_x = MARGIN + col_w + 24
    row_y = y + 40
    row_h = 44
    for i in range(0, len(BRIEFS), 2):
        for j, idx in enumerate((i, i + 1)):
            if idx >= len(BRIEFS):
                break
            x = left_x if j == 0 else right_x
            page.draw_text(x, row_y, "\u2022", 2, RED)
            page.draw_wrapped(x + 16, row_y, BRIEFS[idx], col_w - 16, 2, INK)
        row_y += row_h


def draw_footer(page):
    page.hline(MARGIN, 946, CONTENT_W, INK, 1)
    page.draw_text_centered(
        WIDTH // 2,
        960,
        "THE WORLD TODAY  \u2022  THURSDAY, 26 NOVEMBER 2026  \u2022  ONE PAGE, ALL THE NEWS",
        2,
        GREY,
    )


def render_page_png():
    """Render the front page and return the PNG bytes."""
    page = Page()
    page.rect_outline(14, 14, WIDTH - 28, HEIGHT - 28, INK, 3)
    draw_masthead(page)
    draw_lead(page)
    draw_middle(page)
    draw_briefs(page)
    draw_footer(page)
    return encode_png(page)
