import fontforge
import shutil
import os
import sys
import contextlib

@contextlib.contextmanager
def suppress_stderr():
    """Suppress C-level stderr output."""
    with open(os.devnull, 'w') as devnull:
        # Save original stderr fd
        stderr_fd = 2
        old_stderr = os.dup(stderr_fd)
        try:
            # Redirect stderr to devnull
            os.dup2(devnull.fileno(), stderr_fd)
            yield
        finally:
            # Restore stderr
            os.dup2(old_stderr, stderr_fd)
            os.close(old_stderr)

from config import *

# Get project root directory (parent of src/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Width values for bearing adjustment
# Source Code Pro Latin width is 600. Hangul should be 1200 (double width).
sourcecodepro_latin_width = 600
target_hangul_width = sourcecodepro_latin_width * 2  # 1200
d2coding_width = 1000

# Get adjustment from config if available, otherwise default to 0
# hangul_bearing_adjustment: positive adds space, negative removes space
bearing_adj = hangul_bearing_adjustment
addition = (target_hangul_width - d2coding_width) + bearing_adj

def add_bearing(glyph, addition):
    glyph.left_side_bearing = addition // 2 + int(glyph.left_side_bearing)
    glyph.right_side_bearing = (addition - (addition // 2)) + int(glyph.right_side_bearing)
    return glyph

def replace_name(string):
    return string.replace("SourceCodePro", "Source Code Pro KR") \
            .replace("Source Code Pro", "Source Code Pro KR")

def get_d2_font(variant):
    """Get the appropriate D2Coding font for the given variant."""
    # Use Bold for Bold, Black, and Semibold variants
    if any(w in variant for w in ['Bold', 'Black', 'Semibold']):
        filename = f'D2CodingBold-Ver{d2_coding_version}-{d2_coding_date}-ligature.ttf'
    else:
        filename = f'D2Coding-Ver{d2_coding_version}-{d2_coding_date}-ligature.ttf'
    
    # Try multiple possible paths to handle different unzip behaviors
    search_paths = [
        os.path.join(download_path, filename),
        os.path.join(download_path, "D2CodingLigature", filename),
        os.path.join(download_path, "D2CodingLigature", "D2CodingLigature", filename),
        os.path.join(download_path, "D2Coding", "D2CodingLigature", filename),
    ]

    for path in search_paths:
        if os.path.exists(path):
            print(f"[INFO] Using Korean font: {path} for variant: {variant}")
            return path

    print(f"[WARN] Korean font not found for variant {variant}, using fallback")
    return os.path.join(download_path, "D2CodingLigature", filename)

def build_font():
    # Change to project root
    os.chdir(PROJECT_ROOT)

    if not os.path.exists(out_path):
        print(f'[INFO] Make \'{out_path}\' directory')
        os.makedirs(out_path)

    print("[INFO] Merge fonts and output")
    for name in os.listdir(f'{download_path}/TTF'):
        # Extract variant from filename (e.g., "SourceCodePro-Regular.ttf" -> "Regular")
        base_name = name.replace('SourceCodePro-', '').replace('.ttf', '')

        # Skip if this variant is not in the filter list
        if base_name not in font_variants:
            print(f"[INFO] Skipping {name} (not in font_variants)")
            continue

        # Get the appropriate D2Coding font for this variant
        d2_font_path = get_d2_font(base_name)
        with suppress_stderr():
            d2 = fontforge.open(d2_font_path)

        # Select hangul glyphs and adjust their bearing
        hangul = d2.selection.select(("unicode", "ranges"), 0x3131, 0x318E) \
                .select(("unicode", "ranges", "more"), 0xAC00, 0xD7A3)
        
        print(f"[INFO] Adjusting bearings for {base_name} (addition: {addition})")
        for i in hangul:
            glyph = d2[i]
            if not glyph.references:
                add_bearing(glyph, addition)
            else:
                for j in glyph.references:
                    refglyph = d2[j[0]]
                    # Only adjust if not already adjusted (width should be d2coding_width or close)
                    if int(refglyph.width) > d2coding_width:
                        continue
                    else:
                        add_bearing(refglyph, addition)
        d2.copy()

        scp_file_path = f"{download_path}/TTF/{name}"
        with suppress_stderr():
            scp = fontforge.open(scp_file_path)

        # Debug: Check for nested table access
        if base_name == 'Regular':
            print("[DEBUG] Checking for nested table access...")
            # Check if we can access tables via nested attributes
            for table_name in ['OS2', 'OS/2', 'post', 'POST', 'head', 'cvt']:
                if hasattr(scp, table_name):
                    print(f"  - scp.{table_name} exists: {getattr(scp, table_name)}")
            # Check for lowercase versions
            for table_name in ['os2', 'post']:
                if hasattr(scp, table_name):
                    table = getattr(scp, table_name)
                    print(f"  - scp.{table_name} exists: {type(table)}")
                    if hasattr(table, '__dict__'):
                        print(f"    Attributes: {sorted(table.__dict__.keys())}")

        scp.selection.select(("unicode", "ranges"), 0x3131, 0x318E) \
            .select(("unicode", "ranges", "more"), 0xAC00, 0xD7A3)
        scp.paste()

        # Generate filename: SourceCodePro-Regular.ttf -> SourceCodeProKR-Regular.ttf
        output_name = name.replace('SourceCodePro-', 'SourceCodeProKR-')
        namel = output_name.split(".")

        # Set basic font properties
        family_name = "Source Code Pro KR"
        subfamily_name = base_name  # Regular, Bold, etc.
        full_name = f"{family_name} {subfamily_name}"
        postscript_name = f"SourceCodeProKR-{base_name}"

        scp.familyname = family_name
        scp.fontname = postscript_name
        scp.fullname = full_name

        # Set weight and style properties
        # This is crucial for OS/2 table and macStyle bits to be correct
        if 'Bold' in base_name:
            scp.weight = 'Bold'
            scp.os2_weight = 700
            scp.macstyle = 1 # Bold
        elif 'Black' in base_name:
            scp.weight = 'Black'
            scp.os2_weight = 900
            scp.macstyle = 1 # Bold (closest macStyle)
        elif 'Semibold' in base_name:
            scp.weight = 'Demi Bold'
            scp.os2_weight = 600
        elif 'Medium' in base_name:
            scp.weight = 'Medium'
            scp.os2_weight = 500
        elif 'Light' in base_name:
            scp.weight = 'Light'
            scp.os2_weight = 300
        elif 'ExtraLight' in base_name:
            scp.weight = 'Extra Light'
            scp.os2_weight = 200
        else:
            scp.weight = 'Regular'
            scp.os2_weight = 400
            scp.macstyle = 0

        if 'It' in base_name:
            scp.macstyle |= 2 # Italic
            # Handle italic naming for subfamily
            if base_name == 'It': 
                subfamily_name = 'Italic'
            elif 'It' in base_name and 'Italic' not in base_name:
                subfamily_name = base_name.replace('It', ' Italic')

        # OS/2 StyleMap: 0x01=Italic, 0x20=Bold, 0x40=Regular
        if 'Bold' in base_name or 'Black' in base_name:
            if 'It' in base_name:
                scp.os2_stylemap = 0x21 # Bold + Italic
            else:
                scp.os2_stylemap = 0x20 # Bold
        elif 'It' in base_name:
            scp.os2_stylemap = 0x01 # Italic
        else:
            scp.os2_stylemap = 0x40 # Regular

        # Update full name with corrected subfamily
        full_name = f"{family_name} {subfamily_name}"
        scp.fullname = full_name
        try:
            scp.subfamilyname = subfamily_name
        except AttributeError:
            pass  # Not all FontForge versions have this attribute

        # For Linux/Windows monospaced detection and correct cell width
        # Try multiple possible attribute names for fixed pitch flag
        fixed_pitch_set = False
        fixed_pitch_attrs = [
            'is_fixed_pitch',
            'postscript_is_fixed_pitch',
            'postscript_isfixedpitch',
            'postscript_fixed_pitch',
        ]

        for attr in fixed_pitch_attrs:
            if not fixed_pitch_set:
                try:
                    setattr(scp, attr, True)
                    fixed_pitch_set = True
                    print(f"[DEBUG] {attr} set to True")
                    break
                except AttributeError:
                    continue

        if not fixed_pitch_set:
            print("[WARN] Could not set fixed pitch flag (tried all attributes)")
        
        # OS/2 table PANOSE: 4th digit (index 3) is 9 for monospaced
        if scp.os2_panose:
            panose = list(scp.os2_panose)
            if len(panose) > 3:
                panose[3] = 9
                scp.os2_panose = tuple(panose)
                print(f"[DEBUG] PANOSE set to: {scp.os2_panose}")
        else:
            print("[WARN] os2_panose not available")
        
        # OS/2 table xAvgCharWidth: force to Latin width (600)
        # This prevents some systems (especially on Linux) from using the Hangul width
        # as the default cell width for all characters.
        xavg_set = False
        xavg_attrs = [
            'os2_xavgcharwidth',
            'os2_avgcharwidth',
            'os2_x_avg_char_width',
            'os2xAvgCharWidth',
            'os2_avg_char_width',
        ]

        for attr in xavg_attrs:
            if not xavg_set:
                try:
                    setattr(scp, attr, sourcecodepro_latin_width)
                    xavg_set = True
                    print(f"[DEBUG] {attr} set to: {sourcecodepro_latin_width}")
                    break
                except AttributeError:
                    continue

        if not xavg_set:
            print("[WARN] Could not set OS/2 average character width (tried all attributes)")

        # Verify the setting was applied
        for attr in xavg_attrs:
            try:
                actual_xavg = getattr(scp, attr)
                print(f"[DEBUG] Verified {attr}: {actual_xavg}")
                break
            except AttributeError:
                continue

        # Clean up and rebuild sfnt_names
        # 0x409: English (US)
        # 1=Family, 2=Subfamily, 4=Fullname, 6=PostScript, 16=Preferred Family, 17=Preferred Subfamily
        scp.appendSFNTName('English (US)', 1, family_name)
        scp.appendSFNTName('English (US)', 2, subfamily_name)
        scp.appendSFNTName('English (US)', 4, full_name)
        scp.appendSFNTName('English (US)', 6, postscript_name)
        scp.appendSFNTName('English (US)', 16, family_name)
        scp.appendSFNTName('English (US)', 17, subfamily_name)

        # Clear Korean name entries if they exist to prevent platform mismatch warnings
        # and ensure consistent names across all platforms
        # Language ID 0x412 is Korean
        new_names = []
        for name_record in scp.sfnt_names:
            if name_record[2] == 0x412 or name_record[2] == 1042: # Korean
                continue
            new_names.append(name_record)
        scp.sfnt_names = tuple(new_names)

        # Recalculate bounding box and suppress warnings during generation
        with suppress_stderr():
            scp.generate(".".join(namel))
        
        # Close font objects to free resources
        d2.close()
        scp.close()
        
        shutil.move(".".join(namel), out_path+"/"+".".join(namel))
        print("[INFO] Exported "+ ".".join(namel))

if __name__ == "__main__":
    build_font()
