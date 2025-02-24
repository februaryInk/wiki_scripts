'''
Draw labeled maps of Sandrock.
'''

from PIL import Image, ImageDraw, ImageFont

from sandrock import *

map_x = 1612
map_y = 1612

font_sizes = {
    1.0: 80,
    1.5: 20,
    2.0: 10
}

label_substitutions = {
    'Back Street': 'Back\nStreet',
    'Church of the Light': 'Church of the\nLight',
    'End of the Road Graveyard': 'End of the Road\nGraveyard',
    'Grand Mesa': 'Grand\nMesa',
    'Highwind Pass': 'Highwind\nPass',
    'Main Street': 'Main\nStreet',
    'Martle\'s Square': 'Martle\'s\nSquare',
    'Sandrock Station': 'Sandrock\nStation',
    'Valley of Whispers': 'Valley of\nWhispers',
}

manual_points = {
    1001: {
        'buildingPos': {'x': 920, 'z': 720.0},
        'text': 90114, # Highwind Pass
        'scale': 1.0,
    },
}

def main():
    base_map = Image.open(config.assets_root / "map.png").convert("RGBA")
    for zoom, size in font_sizes.items():
        draw_map(zoom, size, base_map)

def draw_map(zoom: float, font_size: int, base_map: Image.Image):
    map = base_map.copy()
    draw = ImageDraw.Draw(map)

    try:
        font = ImageFont.truetype("ebrima.ttf", font_size) 
    except IOError:
        print("Font not found, using default font")
        font = ImageFont.load_default(font_size)

    map_words = DesignerConfig.MapWords
    for id, point in (map_words._data | manual_points).items():
        if (point['scale'] != zoom and zoom != 1.0 and id not in [1, 17]) or (zoom == 1.0 and point['scale'] != zoom and id != 44): continue
        # Research Center and Gecko Station, not needed for the district map.
        if zoom == 1.5 and id in [30, 32]: continue
        # Catori World, in the middle of town. ???
        if id == 22: continue

        label = text(point['text'])
        label = label_substitutions.get(label, label)
        position = scale_point((point['buildingPos']['x'], point['buildingPos']['z']), map.size)

        print(f"Drawing {label} at {position} for zoom {zoom}")

        lines = label.split("\n")
        line_padding = -5

        # Measure text box for centering.
        text_widths, text_heights = zip(*(draw.textbbox((0, 0), line, font=font)[2:] for line in lines))
        max_text_width = max(text_widths)
        total_text_height = sum(text_heights) + (len(lines) - 1) * line_padding

        label_x = position[0] - max_text_width // 2
        label_y = position[1] - total_text_height // 2
        
        for i, line in enumerate(lines):
            text_width = text_widths[i]
            x = label_x + (max_text_width - text_width) // 2
            y = label_y + i * (text_heights[i] + line_padding)
            draw.text((x, y), line, font=font, fill="#fae3cb", stroke_fill="#4b3013", stroke_width=3)
    
    (config.output_dir / "maps").mkdir(parents=True, exist_ok=True)
    map.save(config.output_dir / f'map/labeled_map_{str(zoom).replace('.', '_')}.png')

def scale_point(point: tuple[float, float], image_size: tuple[int, int]) -> tuple[float, float]:
    x, y = point
    x = (x + map_x) / (map_x * 2) * image_size[0]
    y = image_size[1] - (y + map_y) / (map_y * 2) * image_size[1]
    return x, y

main()
