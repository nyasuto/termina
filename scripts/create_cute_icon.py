#!/usr/bin/env python3
"""
Create a cute microphone icon for Termina app
Uses Python PIL to generate a kawaii-style microphone icon
"""

import math

from PIL import Image, ImageDraw


def create_cute_animal_icon(size=512):
    """Create a cute animal (cat) icon representing voice/audio"""
    # Create image with transparent background
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Colors (kawaii pastels)
    cat_body = (255, 218, 185)  # Cream/peach
    cat_highlight = (255, 235, 210)  # Light cream
    cat_shadow = (245, 200, 165)  # Darker cream
    ear_inside = (255, 192, 203)  # Pink
    nose_color = (255, 160, 180)  # Pink nose
    sparkle_color = (255, 255, 255)  # White

    center_x, center_y = size // 2, size // 2

    # Cat head (main circle)
    head_radius = size * 0.25
    head_bbox = [
        center_x - head_radius,
        center_y - head_radius * 0.8,
        center_x + head_radius,
        center_y + head_radius * 1.2,
    ]

    # Draw cat head
    draw.ellipse(head_bbox, fill=cat_body, outline=cat_shadow, width=3)

    # Cat ears (triangles)
    left_ear_points = [
        (center_x - size * 0.15, center_y - head_radius * 0.6),  # Bottom left
        (center_x - size * 0.05, center_y - head_radius * 0.6),  # Bottom right
        (center_x - size * 0.1, center_y - head_radius * 0.9),  # Top
    ]
    right_ear_points = [
        (center_x + size * 0.05, center_y - head_radius * 0.6),  # Bottom left
        (center_x + size * 0.15, center_y - head_radius * 0.6),  # Bottom right
        (center_x + size * 0.1, center_y - head_radius * 0.9),  # Top
    ]

    # Draw ears
    draw.polygon(left_ear_points, fill=cat_body, outline=cat_shadow)
    draw.polygon(right_ear_points, fill=cat_body, outline=cat_shadow)

    # Inner ears (pink)
    left_inner_ear = [
        (center_x - size * 0.12, center_y - head_radius * 0.65),
        (center_x - size * 0.08, center_y - head_radius * 0.65),
        (center_x - size * 0.1, center_y - head_radius * 0.8),
    ]
    right_inner_ear = [
        (center_x + size * 0.08, center_y - head_radius * 0.65),
        (center_x + size * 0.12, center_y - head_radius * 0.65),
        (center_x + size * 0.1, center_y - head_radius * 0.8),
    ]

    draw.polygon(left_inner_ear, fill=ear_inside)
    draw.polygon(right_inner_ear, fill=ear_inside)

    # Add highlight to head
    highlight_radius = head_radius * 0.6
    highlight_bbox = [
        center_x - highlight_radius * 0.7,
        center_y - head_radius * 0.5,
        center_x + highlight_radius * 0.3,
        center_y - head_radius * 0.1,
    ]
    draw.ellipse(highlight_bbox, fill=cat_highlight)

    # Cat face
    face_y = center_y - size * 0.05

    # Eyes (big kawaii eyes)
    eye_size = size * 0.06
    left_eye_x = center_x - size * 0.08
    right_eye_x = center_x + size * 0.08

    # Draw eyes (closed happy style ^_^)
    for eye_x in [left_eye_x, right_eye_x]:
        # Draw arc for closed eye
        eye_bbox = [
            eye_x - eye_size,
            face_y - eye_size // 2,
            eye_x + eye_size,
            face_y + eye_size // 2,
        ]
        draw.arc(eye_bbox, 0, 180, fill=(80, 80, 100), width=4)

    # Nose (small triangle)
    nose_y = face_y + size * 0.03
    nose_points = [
        (center_x - size * 0.015, nose_y - size * 0.01),
        (center_x + size * 0.015, nose_y - size * 0.01),
        (center_x, nose_y + size * 0.015),
    ]
    draw.polygon(nose_points, fill=nose_color)

    # Mouth (cat smile)
    mouth_y = nose_y + size * 0.02
    # Left side of mouth
    draw.arc(
        [
            center_x - size * 0.03,
            mouth_y - size * 0.01,
            center_x,
            mouth_y + size * 0.02,
        ],
        0,
        90,
        fill=(80, 80, 100),
        width=3,
    )
    # Right side of mouth
    draw.arc(
        [
            center_x,
            mouth_y - size * 0.01,
            center_x + size * 0.03,
            mouth_y + size * 0.02,
        ],
        90,
        180,
        fill=(80, 80, 100),
        width=3,
    )

    # Whiskers
    whisker_length = size * 0.08
    whisker_y = face_y + size * 0.01
    # Left whiskers
    draw.line(
        [
            center_x - size * 0.12,
            whisker_y - size * 0.01,
            center_x - size * 0.12 - whisker_length,
            whisker_y - size * 0.01,
        ],
        fill=(80, 80, 100),
        width=2,
    )
    draw.line(
        [
            center_x - size * 0.12,
            whisker_y + size * 0.01,
            center_x - size * 0.12 - whisker_length,
            whisker_y + size * 0.01,
        ],
        fill=(80, 80, 100),
        width=2,
    )
    # Right whiskers
    draw.line(
        [
            center_x + size * 0.12,
            whisker_y - size * 0.01,
            center_x + size * 0.12 + whisker_length,
            whisker_y - size * 0.01,
        ],
        fill=(80, 80, 100),
        width=2,
    )
    draw.line(
        [
            center_x + size * 0.12,
            whisker_y + size * 0.01,
            center_x + size * 0.12 + whisker_length,
            whisker_y + size * 0.01,
        ],
        fill=(80, 80, 100),
        width=2,
    )

    # Add cute sparkles around the cat
    sparkles = [
        (center_x - size * 0.25, center_y - size * 0.25),
        (center_x + size * 0.25, center_y - size * 0.3),
        (center_x - size * 0.3, center_y + size * 0.1),
        (center_x + size * 0.28, center_y + size * 0.15),
    ]

    for sparkle_x, sparkle_y in sparkles:
        # Draw 4-pointed star
        points = []
        for i in range(8):
            angle = i * math.pi / 4
            r = size * 0.025 if i % 2 == 0 else size * 0.012  # Outer/inner points

            x = sparkle_x + r * math.cos(angle)
            y = sparkle_y + r * math.sin(angle)
            points.append((x, y))

        draw.polygon(points, fill=sparkle_color, outline=(220, 220, 240))

    # Add sound waves (representing voice/audio functionality)
    wave_color = (180, 180, 200, 100)  # Semi-transparent
    for i in range(3):
        wave_radius = size * (0.18 + i * 0.08)
        wave_bbox = [
            center_x + size * 0.2 - wave_radius,
            center_y - wave_radius,
            center_x + size * 0.2 + wave_radius,
            center_y + wave_radius,
        ]
        draw.arc(wave_bbox, -45, 45, fill=wave_color, width=3)

    return img


def create_icns_file(base_name="termina_cute"):
    """Create .icns file with multiple sizes"""
    import os

    # Common macOS icon sizes
    sizes = [16, 32, 64, 128, 256, 512, 1024]

    # Create iconset directory
    iconset_dir = f"icons/{base_name}.iconset"
    os.makedirs(iconset_dir, exist_ok=True)

    for size in sizes:
        img = create_cute_animal_icon(size)

        # Save normal resolution
        img.save(f"{iconset_dir}/icon_{size}x{size}.png")

        # Save @2x version for retina
        if size <= 512:
            img_2x = create_cute_animal_icon(size * 2)
            img_2x.save(f"{iconset_dir}/icon_{size}x{size}@2x.png")

    print(f"✅ Icon set created in {iconset_dir}")
    print("📝 To create .icns file, run:")
    print(f"iconutil -c icns {iconset_dir}")

    return iconset_dir


if __name__ == "__main__":
    print("🎨 Creating cute animal (cat) icon for Termina...")

    try:
        # Create single large icon for preview
        icon = create_cute_animal_icon(512)
        icon.save("icons/termina_cute_preview.png")
        print("✅ Preview icon saved: icons/termina_cute_preview.png")

        # Create complete icon set
        iconset_dir = create_icns_file()

        print("🎉 Cute animal icon creation complete!")

    except ImportError:
        print("❌ PIL (Pillow) not found. Install with: uv add pillow")
    except Exception as e:
        print(f"❌ Error creating icon: {e}")
