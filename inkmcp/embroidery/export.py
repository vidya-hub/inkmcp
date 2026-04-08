"""
Embroidery Export Module

Handles exporting embroidery designs to machine-readable formats using Ink/Stitch.
Supports DST, PES, JEF, EXP, VIP, XXX, and many other embroidery formats.

This module provides two approaches:
1. Direct CLI invocation of Ink/Stitch extensions (cross-platform)
2. Integration with InkMCP for Inkscape-based export (via D-Bus on Linux)
"""

import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import common utilities
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from inkmcpops.common import create_success_response, create_error_response


# ══════════════════════════════════════════════════════════════════════════════
# EMBROIDERY FORMAT DEFINITIONS
# ══════════════════════════════════════════════════════════════════════════════


class EmbroideryFormat(Enum):
    """Supported embroidery machine formats"""

    # Brother/Babylock
    PES = "pes"  # Brother/Babylock (most popular home format)
    PEC = "pec"  # Brother/Babylock (legacy)
    PHB = "phb"  # Brother
    PHC = "phc"  # Brother

    # Tajima
    DST = "dst"  # Tajima (most popular commercial format)
    DSB = "dsb"  # Barudan
    DSZ = "dsz"  # Tajima (with thread colors)

    # Janome
    JEF = "jef"  # Janome
    SEW = "sew"  # Janome

    # Singer
    XXX = "xxx"  # Singer

    # Pfaff
    VIP = "vip"  # Pfaff/Viking
    VP3 = "vp3"  # Pfaff (newer)

    # Husqvarna Viking
    HUS = "hus"  # Husqvarna
    SHV = "shv"  # Husqvarna

    # Melco
    EXP = "exp"  # Melco

    # Toyota
    T01 = "t01"  # Toyota

    # Bernina
    ART = "art"  # Bernina

    # Generic/Universal
    CSV = "csv"  # CSV stitch data
    JSON = "json"  # JSON stitch data

    # Simulation/Preview
    SVG = "svg"  # SVG with stitch simulation
    PNG = "png"  # PNG stitch preview image


@dataclass
class FormatInfo:
    """Information about an embroidery format"""

    format: EmbroideryFormat
    extension: str
    name: str
    description: str
    manufacturer: str
    max_colors: Optional[int]  # None = unlimited
    max_width_mm: Optional[float]  # None = unlimited
    max_height_mm: Optional[float]
    supports_trim: bool
    supports_jump: bool


# Format specifications
FORMAT_INFO: Dict[EmbroideryFormat, FormatInfo] = {
    EmbroideryFormat.PES: FormatInfo(
        format=EmbroideryFormat.PES,
        extension=".pes",
        name="Brother PES",
        description="Brother/Babylock embroidery format. Most common home embroidery format.",
        manufacturer="Brother",
        max_colors=255,
        max_width_mm=360,
        max_height_mm=350,
        supports_trim=True,
        supports_jump=True,
    ),
    EmbroideryFormat.DST: FormatInfo(
        format=EmbroideryFormat.DST,
        extension=".dst",
        name="Tajima DST",
        description="Tajima/Commercial format. Industry standard for commercial machines.",
        manufacturer="Tajima",
        max_colors=None,  # Colors stored separately
        max_width_mm=None,
        max_height_mm=None,
        supports_trim=True,
        supports_jump=True,
    ),
    EmbroideryFormat.JEF: FormatInfo(
        format=EmbroideryFormat.JEF,
        extension=".jef",
        name="Janome JEF",
        description="Janome embroidery format with embedded thread colors.",
        manufacturer="Janome",
        max_colors=127,
        max_width_mm=500,
        max_height_mm=500,
        supports_trim=True,
        supports_jump=True,
    ),
    EmbroideryFormat.EXP: FormatInfo(
        format=EmbroideryFormat.EXP,
        extension=".exp",
        name="Melco EXP",
        description="Melco expanded format. Good for commercial machines.",
        manufacturer="Melco",
        max_colors=None,
        max_width_mm=None,
        max_height_mm=None,
        supports_trim=True,
        supports_jump=True,
    ),
    EmbroideryFormat.VP3: FormatInfo(
        format=EmbroideryFormat.VP3,
        extension=".vp3",
        name="Pfaff VP3",
        description="Pfaff/Viking newer format with extended features.",
        manufacturer="Pfaff",
        max_colors=255,
        max_width_mm=None,
        max_height_mm=None,
        supports_trim=True,
        supports_jump=True,
    ),
    EmbroideryFormat.HUS: FormatInfo(
        format=EmbroideryFormat.HUS,
        extension=".hus",
        name="Husqvarna HUS",
        description="Husqvarna Viking embroidery format.",
        manufacturer="Husqvarna",
        max_colors=255,
        max_width_mm=None,
        max_height_mm=None,
        supports_trim=True,
        supports_jump=True,
    ),
    EmbroideryFormat.XXX: FormatInfo(
        format=EmbroideryFormat.XXX,
        extension=".xxx",
        name="Singer XXX",
        description="Singer embroidery format.",
        manufacturer="Singer",
        max_colors=255,
        max_width_mm=None,
        max_height_mm=None,
        supports_trim=True,
        supports_jump=True,
    ),
    EmbroideryFormat.SVG: FormatInfo(
        format=EmbroideryFormat.SVG,
        extension=".svg",
        name="SVG Simulation",
        description="SVG with realistic stitch simulation for preview.",
        manufacturer="Ink/Stitch",
        max_colors=None,
        max_width_mm=None,
        max_height_mm=None,
        supports_trim=True,
        supports_jump=True,
    ),
    EmbroideryFormat.PNG: FormatInfo(
        format=EmbroideryFormat.PNG,
        extension=".png",
        name="PNG Preview",
        description="PNG image preview of the embroidery design.",
        manufacturer="Ink/Stitch",
        max_colors=None,
        max_width_mm=None,
        max_height_mm=None,
        supports_trim=True,
        supports_jump=True,
    ),
}


# ══════════════════════════════════════════════════════════════════════════════
# INK/STITCH CLI INTERFACE
# ══════════════════════════════════════════════════════════════════════════════


def find_inkstitch_cli() -> Optional[Path]:
    """
    Find the Ink/Stitch CLI executable.

    Ink/Stitch is typically installed as an Inkscape extension, but can also
    be invoked via its bundled Python scripts.

    Returns:
        Path to inkstitch CLI or None if not found
    """
    # Common Ink/Stitch installation locations
    possible_paths = [
        # macOS
        Path.home() / ".config/inkscape/extensions/inkstitch",
        Path(
            "/Applications/Inkscape.app/Contents/Resources/share/inkscape/extensions/inkstitch"
        ),
        # Linux
        Path.home() / ".config/inkscape/extensions/inkstitch",
        Path("/usr/share/inkscape/extensions/inkstitch"),
        # Windows
        Path.home() / "AppData/Roaming/inkscape/extensions/inkstitch",
        Path("C:/Program Files/Inkscape/share/inkscape/extensions/inkstitch"),
    ]

    for base_path in possible_paths:
        if base_path.exists():
            # Look for the main inkstitch module
            cli_path = base_path / "bin" / "inkstitch"
            if cli_path.exists():
                return cli_path

            # Alternative: Python module invocation
            init_path = base_path / "__init__.py"
            if init_path.exists():
                return base_path

    return None


def find_inkscape_executable() -> Optional[Path]:
    """
    Find the Inkscape executable.

    Returns:
        Path to Inkscape or None if not found
    """
    # Check PATH first
    inkscape_cmd = shutil.which("inkscape")
    if inkscape_cmd:
        return Path(inkscape_cmd)

    # Check common locations
    possible_paths = [
        # macOS
        Path("/Applications/Inkscape.app/Contents/MacOS/inkscape"),
        # Linux
        Path("/usr/bin/inkscape"),
        Path("/usr/local/bin/inkscape"),
        # Windows
        Path("C:/Program Files/Inkscape/bin/inkscape.exe"),
        Path("C:/Program Files (x86)/Inkscape/bin/inkscape.exe"),
    ]

    for path in possible_paths:
        if path.exists():
            return path

    return None


def get_inkstitch_extension_path() -> Optional[Path]:
    """
    Get the path to Ink/Stitch extension directory.

    Returns:
        Path to Ink/Stitch extension or None if not found
    """
    # Common extension locations
    possible_paths = [
        # macOS user extensions
        Path.home() / ".config/inkscape/extensions/inkstitch",
        # macOS system (bundled with Inkscape)
        Path(
            "/Applications/Inkscape.app/Contents/Resources/share/inkscape/extensions/inkstitch"
        ),
        # Linux user extensions
        Path.home() / ".config/inkscape/extensions/inkstitch",
        # Linux system
        Path("/usr/share/inkscape/extensions/inkstitch"),
        # Windows user extensions
        Path.home() / "AppData/Roaming/inkscape/extensions/inkstitch",
        # Windows system
        Path("C:/Program Files/Inkscape/share/inkscape/extensions/inkstitch"),
    ]

    for path in possible_paths:
        if path.exists() and (path / "__init__.py").exists():
            return path

    return None


# ══════════════════════════════════════════════════════════════════════════════
# EXPORT OPERATIONS
# ══════════════════════════════════════════════════════════════════════════════


def export_embroidery_via_inkscape(
    svg_path: str,
    output_path: str,
    format: EmbroideryFormat,
    options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Export an SVG file to embroidery format using Inkscape with Ink/Stitch.

    This method invokes Inkscape's command-line interface to run the Ink/Stitch
    export extension.

    Args:
        svg_path: Path to input SVG file (must contain Ink/Stitch-compatible elements)
        output_path: Path for output embroidery file
        format: Target embroidery format
        options: Optional export options

    Returns:
        Success or error response dictionary
    """
    inkscape = find_inkscape_executable()
    if not inkscape:
        return create_error_response(
            "Inkscape not found. Please install Inkscape from https://inkscape.org"
        )

    inkstitch_path = get_inkstitch_extension_path()
    if not inkstitch_path:
        return create_error_response(
            "Ink/Stitch not found. Please install Ink/Stitch from https://inkstitch.org"
        )

    # Ensure paths are absolute
    svg_path = str(Path(svg_path).resolve())
    output_path = str(Path(output_path).resolve())

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Build Inkscape command to run Ink/Stitch output extension
    # Format: inkscape --export-type=<format> --export-filename=<output> <input>
    # For embroidery, we need to use the Ink/Stitch export action

    format_info = FORMAT_INFO.get(format)
    if not format_info:
        return create_error_response(f"Unsupported format: {format.value}")

    # Ink/Stitch extension ID for output
    extension_id = f"org.inkstitch.output.{format.value}"

    cmd = [
        str(inkscape),
        svg_path,
        f"--actions=org.inkstitch.output_{format.value};export-filename:{output_path}",
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout
        )

        if result.returncode != 0:
            return create_error_response(
                f"Inkscape export failed: {result.stderr or result.stdout}"
            )

        # Verify output file was created
        if not Path(output_path).exists():
            return create_error_response(
                f"Export completed but output file not found: {output_path}"
            )

        # Get file size
        file_size = Path(output_path).stat().st_size

        return create_success_response(
            f"Exported embroidery to {format.value.upper()} format",
            output_path=output_path,
            format=format.value,
            format_name=format_info.name,
            file_size=file_size,
            file_size_kb=round(file_size / 1024, 2),
        )

    except subprocess.TimeoutExpired:
        return create_error_response("Export timed out after 120 seconds")
    except Exception as e:
        return create_error_response(f"Export failed: {e}")


def export_embroidery_via_python(
    svg_path: str,
    output_path: str,
    format: EmbroideryFormat,
) -> Dict[str, Any]:
    """
    Export embroidery using Ink/Stitch's Python API directly.

    This is an alternative to Inkscape CLI that may be faster but
    requires Ink/Stitch's Python environment.

    Args:
        svg_path: Path to input SVG file
        output_path: Path for output file
        format: Target format

    Returns:
        Success or error response dictionary
    """
    inkstitch_path = get_inkstitch_extension_path()
    if not inkstitch_path:
        return create_error_response(
            "Ink/Stitch not found. Please install from https://inkstitch.org"
        )

    # Try to invoke Ink/Stitch's bundled Python
    # This is platform-specific and may not always work

    try:
        # Add Ink/Stitch to Python path and import
        sys.path.insert(0, str(inkstitch_path.parent))

        # Attempt to use pyembroidery directly if available
        try:
            import pyembroidery

            # Read SVG and convert to embroidery
            # Note: This requires parsing the SVG and generating stitches,
            # which is complex. For now, fall back to Inkscape method.
            return create_error_response(
                "Direct Python export not yet implemented. Use export_embroidery_via_inkscape."
            )

        except ImportError:
            return create_error_response(
                "pyembroidery not available. Install with: pip install pyembroidery"
            )

    except Exception as e:
        return create_error_response(f"Python export failed: {e}")


def generate_stitch_simulation(
    svg_path: str,
    output_path: Optional[str] = None,
    realistic: bool = True,
) -> Dict[str, Any]:
    """
    Generate a stitch simulation preview of an embroidery design.

    This creates a visual preview showing how the embroidery will look
    when stitched out.

    Args:
        svg_path: Path to input SVG file
        output_path: Path for output SVG (default: adds _simulation suffix)
        realistic: Use realistic thread rendering

    Returns:
        Success or error response with simulation path
    """
    inkscape = find_inkscape_executable()
    if not inkscape:
        return create_error_response("Inkscape not found")

    svg_path = Path(svg_path).resolve()

    if output_path is None:
        output_path = svg_path.parent / f"{svg_path.stem}_simulation.svg"
    else:
        output_path = Path(output_path).resolve()

    # Ink/Stitch simulation extension
    extension_id = "org.inkstitch.simulate" if realistic else "org.inkstitch.print_pdf"

    cmd = [
        str(inkscape),
        str(svg_path),
        f"--actions={extension_id};export-filename:{output_path}",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            return create_error_response(f"Simulation failed: {result.stderr}")

        return create_success_response(
            "Generated stitch simulation",
            output_path=str(output_path),
            realistic=realistic,
        )

    except Exception as e:
        return create_error_response(f"Simulation failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# HIGH-LEVEL EXPORT FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════


def export_embroidery(
    svg_path: str,
    output_path: str,
    format: str = "dst",
) -> Dict[str, Any]:
    """
    Export an SVG embroidery design to machine-readable format.

    Main entry point for embroidery export. Automatically selects the
    best available export method.

    Args:
        svg_path: Path to input SVG file with Ink/Stitch elements
        output_path: Path for output embroidery file
        format: Target format (dst, pes, jef, exp, etc.)

    Returns:
        Success or error response dictionary
    """
    # Parse format
    try:
        emb_format = EmbroideryFormat(format.lower())
    except ValueError:
        valid_formats = [f.value for f in EmbroideryFormat]
        return create_error_response(
            f"Unknown format: {format}. Valid formats: {valid_formats}"
        )

    # Ensure output has correct extension
    format_info = FORMAT_INFO.get(emb_format)
    if format_info:
        output_path = str(Path(output_path).with_suffix(format_info.extension))

    # Try Inkscape-based export (most reliable)
    result = export_embroidery_via_inkscape(svg_path, output_path, emb_format)

    if result["status"] == "error":
        # Fall back to Python export if Inkscape failed
        result = export_embroidery_via_python(svg_path, output_path, emb_format)

    return result


def get_format_info(format: str) -> Dict[str, Any]:
    """
    Get information about an embroidery format.

    Args:
        format: Format name (dst, pes, jef, etc.)

    Returns:
        Format information dictionary
    """
    try:
        emb_format = EmbroideryFormat(format.lower())
    except ValueError:
        return create_error_response(f"Unknown format: {format}")

    info = FORMAT_INFO.get(emb_format)
    if not info:
        return create_error_response(f"No info available for format: {format}")

    return create_success_response(
        f"Format info: {info.name}",
        format=info.format.value,
        extension=info.extension,
        name=info.name,
        description=info.description,
        manufacturer=info.manufacturer,
        max_colors=info.max_colors,
        max_width_mm=info.max_width_mm,
        max_height_mm=info.max_height_mm,
        supports_trim=info.supports_trim,
        supports_jump=info.supports_jump,
    )


def list_export_formats() -> Dict[str, Any]:
    """
    List all available embroidery export formats.

    Returns:
        Dictionary with format list
    """
    formats = []
    for fmt, info in FORMAT_INFO.items():
        formats.append(
            {
                "format": fmt.value,
                "extension": info.extension,
                "name": info.name,
                "manufacturer": info.manufacturer,
            }
        )

    return create_success_response(
        f"Available formats: {len(formats)}",
        formats=formats,
        popular=["dst", "pes", "jef", "exp"],
    )


def check_inkstitch_installation() -> Dict[str, Any]:
    """
    Check if Ink/Stitch is properly installed.

    Returns:
        Installation status and paths
    """
    inkscape = find_inkscape_executable()
    inkstitch = get_inkstitch_extension_path()

    status = {
        "inkscape_found": inkscape is not None,
        "inkscape_path": str(inkscape) if inkscape else None,
        "inkstitch_found": inkstitch is not None,
        "inkstitch_path": str(inkstitch) if inkstitch else None,
        "ready": inkscape is not None and inkstitch is not None,
    }

    if status["ready"]:
        return create_success_response(
            "Ink/Stitch is installed and ready",
            **status,
        )
    else:
        missing = []
        if not inkscape:
            missing.append("Inkscape (https://inkscape.org)")
        if not inkstitch:
            missing.append("Ink/Stitch (https://inkstitch.org)")

        return create_error_response(
            f"Missing components: {', '.join(missing)}",
            **status,
            install_instructions={
                "inkscape": "Download from https://inkscape.org/release/",
                "inkstitch": "Download from https://inkstitch.org/docs/install/",
            },
        )
