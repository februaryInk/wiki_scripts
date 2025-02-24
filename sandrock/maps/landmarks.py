from PIL import Image, ImageDraw, ImageFont

from sandrock import *

scale_2_whitelist = [
    1, # My Home
    9, # The Breach
    17, # Eufaula Salvage
    44, # Eufaula Outback
    45, # Mole Cave Abandoned Ruins
    46, # Starship Abandoned Ruins
]

title_overrides = {
    9: 'The Breach',
    45: 'Mole Cave',
    46: 'Northern Starship Ruins',
    1001: 'Lab 7',
    1002: 'Greeno Factory',
}

manual_points = {
    1001: {
        'buildingPos': {'x': -874.63, 'z': -450.0},
        'text': 'Lab 7',
        'scale': 1.5,
    },
    1002: {
        'buildingPos': {'x': 1320, 'z': 320.0},
        'text': 'Greeno Factory',
        'scale': 1.5,
    },
}

def main():
    markers = []

    map_words = DesignerConfig.MapWords
    for id, point in (map_words._data | manual_points).items():
        # Skip the most zoomed-in points, which are individual buildings.
        if point['scale'] == 2.0 and id not in scale_2_whitelist: continue
        # Catori World, in the middle of town. ???
        if id == 22: continue

        x = point['buildingPos']['x']
        y = point['buildingPos']['z']
        title = title_overrides.get(id, text(point['text']))

        # Draw the title as an image.
        draw_title(title, point['scale'])

        # Some points have weird positions that need to be adjusted.
        if title == 'Eufaula Outback': y -= 75
        if title == 'Main Street': y -= 20
        # if title == 'The Bend': y += 150; x -= 50
        if title == 'The Dead Sea': y -= 500; x -= 100

        marker = {
            'id': id,
            'categoryId': 'default',
            'position': [x, y],
            'popup': {
                'title': title,
            },
        }

        markers.append(marker)

    categories = []
    categories.append({
        'id': 'default',
        'listId': 1,
        'name': 'Item',
        'color': '#a06a28',
    })

    map_data = {
        'mapImage': 'Sandrock map full release.png',
        'mapBounds': [[-1612, -1612], [1612, 1612]],
        'categories': categories,
        'markers': markers,
    }

    write_json('map/landmarks.json', map_data)

def draw_title(title: str, scale: float):
    width, height = 300, 100
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    # Get text bounding box (Pillow 10+)
    bbox = draw.textbbox((0, 0), title, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Calculate text position (centered)
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Draw text in white with full opacity
    draw.text((x, y), title, fill=(255, 255, 255, 255), font=font)

    (config.output_dir / "map_labels").mkdir(parents=True, exist_ok=True)
    image.save(config.output_dir / f'map_labels/{title}.png')

def draw_test():
    # Create a blank image
    width, height = 300, 100
    image = Image.new("RGB", (width, height), "white")

    # Get a drawing context
    draw = ImageDraw.Draw(image)

    # Define the text and font (default font if TTF is unavailable)
    text = "Hello, World!"
    font = ImageFont.load_default()  # Uses a basic font

    # Get text size and position
    text_width, text_height = draw.textsize(text, font=font)
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Draw the text on the image
    draw.text((x, y), text, fill="black", font=font)

    # Save or show the image
    image.show()  # Opens the image
    image.save("text_image.png")  # Saves the image


main()
