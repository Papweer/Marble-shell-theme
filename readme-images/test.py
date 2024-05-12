import colorsys

def adjust_lightness(hexColor, factor=1.1):
    r, g, b = float(int(hexColor[1:3], 16)), float(int(hexColor[3:5], 16)), float(int(hexColor[5:], 16))
    print(r, g, b)
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    l = max(min(l * factor, 1.0), 0.0)
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return "#%02x%02x%02x" % (r,g,b)

print(adjust_lightness("#74c7ec"))