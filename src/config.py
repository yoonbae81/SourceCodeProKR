import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

download_path = 'assets'
out_path = 'out'

d2_coding_version = '1.3.2'
d2_coding_date = '20180524'

# Hangul glyph bearing adjustment (spacing)
# The value is divided by 2 for left and right bearings.
# Use 0 for standard double-width (1200 units if Latin is 600).
# Example: -60 makes Hangul narrower (1140 units), 40 makes it wider (1240 units).
hangul_bearing_adjustment = int(os.getenv('HANGUL_BEARING_ADJUSTMENT', 0))

# Source Code Pro font variants to include in build
# Available variants: Regular, It, Light, LightIt, ExtraLight, ExtraLightIt,
#                     Medium, MediumIt, Semibold, SemiboldIt, Bold, BoldIt, Black, BlackIt
env_variants = os.getenv('FONT_VARIANTS')
if env_variants:
    font_variants = [v.strip() for v in env_variants.split(',')]
else:
    font_variants = [
        'Regular',     # SourceCodeProKR-Regular.ttf
        'Bold',        # SourceCodeProKR-Bold.ttf
    ]
