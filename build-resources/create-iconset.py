# Simple script to create macOS icon from PNG
# This creates a basic .icns file without requiring icnsutils

import os
from PIL import Image

icon_sizes = [
    (16, 'icon_16x16.png'),
    (32, 'icon_16x16@2x.png'),
    (32, 'icon_32x32.png'),
    (64, 'icon_32x32@2x.png'),
    (128, 'icon_128x128.png'),
    (256, 'icon_128x128@2x.png'),
    (256, 'icon_256x256.png'),
    (512, 'icon_256x256@2x.png'),
    (512, 'icon_512x512.png'),
    (1024, 'icon_512x512@2x.png'),
]

# Create iconset directory
iconset_dir = 'build-resources/icon.iconset'
os.makedirs(iconset_dir, exist_ok=True)

# Load source image
img = Image.open('build-resources/icon.png')

# Create all sizes
for size, filename in icon_sizes:
    resized = img.resize((size, size), Image.Resampling.LANCZOS)
    resized.save(os.path.join(iconset_dir, filename))
    print(f'Created {filename}')

print('\nIconset created successfully!')
print('To create .icns file on macOS, run:')
print('  iconutil -c icns build-resources/icon.iconset -o build-resources/icon.icns')
print('\nFor now, the PNG icon will work for Linux builds.')
