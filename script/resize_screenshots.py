'''
New laptop, and my screen is not the intended ratio for the game. Strip some of
the height off the top and bottom of the screenshots to make them consistent 
with other wiki screenshots.
'''

from sandrock import *

from PIL import Image

def main() -> None:
    screenshot_dir = config.assets_root / 'screenshots'

    # Crop the screenshots to 16:9 ratio.
    for screenshot in screenshot_dir.glob('*.jpg'):
        img = Image.open(screenshot)
        w, h = img.size

        # Calculate the new height to maintain 16:9 ratio.
        new_height = int(w * 9 / 16)
        if new_height == h: continue
        top = (h - new_height) // 2
        bottom = h - top

        # Crop the image.
        img_cropped = img.crop((0, top, w, bottom))
        img_cropped.save(screenshot, quality=100)

if __name__ == '__main__':
    main()
