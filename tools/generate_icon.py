"""Generate raster application icons from the same simple medical mark."""

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

size = 512
image = Image.new("RGBA", (size, size), (239, 251, 246, 255))
draw = ImageDraw.Draw(image)
draw.ellipse((18, 18, 494, 494), fill="#effbf6", outline="#c7eadc", width=12)
draw.line((256, 100, 256, 418), fill="#154b3d", width=34)
draw.line((190, 148, 322, 148), fill="#154b3d", width=34)
points = [(306, 158), (204, 189), (302, 252), (207, 310), (291, 375)]
draw.line(points, fill="#20b67a", width=38, joint="curve")
for point in points:
    draw.ellipse((point[0] - 19, point[1] - 19, point[0] + 19, point[1] + 19), fill="#20b67a")
draw.polygon(((302, 142), (352, 129), (326, 171)), fill="#20b67a")
draw.ellipse((326, 143, 336, 153), fill="#103f32")

image.save(ASSETS / "icon.png")
image.save(ASSETS / "icon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
