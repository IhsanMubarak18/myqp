#!/bin/bash
# Script to convert PNG icon to different formats for multi-platform support

# Check if ImageMagick is installed
if ! command -v convert &> /dev/null; then
    echo "ImageMagick is not installed. Installing..."
    sudo apt-get update
    sudo apt-get install -y imagemagick
fi

# Check if icnsutils is installed (for macOS icons)
if ! command -v png2icns &> /dev/null; then
    echo "icnsutils is not installed. Installing..."
    sudo apt-get install -y icnsutils
fi

cd build-resources

echo "Converting icon.png to different formats..."

# Create Windows .ico (multiple sizes)
convert icon.png -resize 256x256 -define icon:auto-resize=256,128,96,64,48,32,16 icon.ico
echo "✓ Created icon.ico for Windows"

# Create macOS .icns
# First create different sizes
mkdir -p icon.iconset
convert icon.png -resize 16x16 icon.iconset/icon_16x16.png
convert icon.png -resize 32x32 icon.iconset/icon_16x16@2x.png
convert icon.png -resize 32x32 icon.iconset/icon_32x32.png
convert icon.png -resize 64x64 icon.iconset/icon_32x32@2x.png
convert icon.png -resize 128x128 icon.iconset/icon_128x128.png
convert icon.png -resize 256x256 icon.iconset/icon_128x128@2x.png
convert icon.png -resize 256x256 icon.iconset/icon_256x256.png
convert icon.png -resize 512x512 icon.iconset/icon_256x256@2x.png
convert icon.png -resize 512x512 icon.iconset/icon_512x512.png
convert icon.png -resize 1024x1024 icon.iconset/icon_512x512@2x.png

# Convert to .icns
png2icns icon.icns icon.iconset/*.png
echo "✓ Created icon.icns for macOS"

# Clean up
rm -rf icon.iconset

echo "✓ Icon conversion complete!"
echo "  - icon.png (Linux)"
echo "  - icon.ico (Windows)"
echo "  - icon.icns (macOS)"
