"""
Ink/Stitch Stitch Types Module

Defines all stitch types supported by Ink/Stitch with their SVG attribute mappings.
Based on Ink/Stitch documentation: https://inkstitch.org/docs/stitch-library/

Stitch types are categorized by:
- Stroke-based: Running stitch, bean stitch, manual stitch, ripple stitch, zigzag
- Satin-based: Satin column, E-stitch, S-stitch
- Fill-based: Fill stitch, contour fill, guided fill, meander fill, etc.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class StitchCategory(Enum):
    """Categories of embroidery stitches"""

    STROKE = "stroke"  # Line-based stitches (running, bean, zigzag)
    SATIN = "satin"  # Two-rail satin column stitches
    FILL = "fill"  # Area fill stitches


class StitchType(Enum):
    """
    All stitch types supported by Ink/Stitch.

    The value corresponds to the internal Ink/Stitch stitch type identifier
    used in SVG attributes.
    """

    # Stroke-based stitches
    RUNNING_STITCH = "running_stitch"
    BEAN_STITCH = "bean_stitch"
    MANUAL_STITCH = "manual_stitch"
    RIPPLE_STITCH = "ripple_stitch"
    ZIGZAG_STITCH = "zigzag_stitch"

    # Satin-based stitches
    SATIN_COLUMN = "satin_column"
    E_STITCH = "e_stitch"
    S_STITCH = "s_stitch"
    ZIGZAG_SATIN = "zigzag_satin"

    # Fill-based stitches
    FILL_STITCH = "fill_stitch"
    AUTO_FILL = "auto_fill"
    CONTOUR_FILL = "contour_fill"
    GUIDED_FILL = "guided_fill"
    MEANDER_FILL = "meander_fill"
    CIRCULAR_FILL = "circular_fill"
    LINEAR_GRADIENT_FILL = "linear_gradient_fill"
    TARTAN_FILL = "tartan_fill"
    CROSS_STITCH = "cross_stitch"


@dataclass
class StitchTypeInfo:
    """Complete information about a stitch type"""

    stitch_type: StitchType
    category: StitchCategory
    display_name: str
    description: str
    svg_element: str  # Required SVG element type (path, etc.)
    requires_fill: bool  # Requires fill attribute
    requires_stroke: bool  # Requires stroke attribute
    requires_satin_rails: bool  # Requires two subpaths for satin
    inkstitch_method: str  # Ink/Stitch method attribute value
    default_params: Dict[str, Any] = field(default_factory=dict)
    supported_params: List[str] = field(default_factory=list)


# Complete stitch type definitions with Ink/Stitch mappings
STITCH_TYPES: Dict[StitchType, StitchTypeInfo] = {
    # ══════════════════════════════════════════════════════════════
    # STROKE-BASED STITCHES
    # ══════════════════════════════════════════════════════════════
    StitchType.RUNNING_STITCH: StitchTypeInfo(
        stitch_type=StitchType.RUNNING_STITCH,
        category=StitchCategory.STROKE,
        display_name="Running Stitch",
        description="Basic single-line stitch following a path. Good for outlines and details.",
        svg_element="path",
        requires_fill=False,
        requires_stroke=True,
        requires_satin_rails=False,
        inkstitch_method="running_stitch",
        default_params={
            "running_stitch_length_mm": 2.5,
            "running_stitch_tolerance_mm": 0.2,
            "repeats": 1,
        },
        supported_params=[
            "running_stitch_length_mm",
            "running_stitch_tolerance_mm",
            "repeats",
            "bean_stitch_repeats",  # Can convert to bean
        ],
    ),
    StitchType.BEAN_STITCH: StitchTypeInfo(
        stitch_type=StitchType.BEAN_STITCH,
        category=StitchCategory.STROKE,
        display_name="Bean Stitch",
        description="Triple stitch (back and forth) for thicker, more visible lines.",
        svg_element="path",
        requires_fill=False,
        requires_stroke=True,
        requires_satin_rails=False,
        inkstitch_method="bean_stitch",
        default_params={
            "running_stitch_length_mm": 2.5,
            "bean_stitch_repeats": 1,  # 1 = triple stitch
        },
        supported_params=[
            "running_stitch_length_mm",
            "bean_stitch_repeats",
        ],
    ),
    StitchType.MANUAL_STITCH: StitchTypeInfo(
        stitch_type=StitchType.MANUAL_STITCH,
        category=StitchCategory.STROKE,
        display_name="Manual Stitch",
        description="Each node becomes a needle penetration point. Full control.",
        svg_element="path",
        requires_fill=False,
        requires_stroke=True,
        requires_satin_rails=False,
        inkstitch_method="manual_stitch",
        default_params={},
        supported_params=[],  # No parameters - pure manual control
    ),
    StitchType.RIPPLE_STITCH: StitchTypeInfo(
        stitch_type=StitchType.RIPPLE_STITCH,
        category=StitchCategory.STROKE,
        display_name="Ripple Stitch",
        description="Creates rippling/wave effect emanating from path. Decorative.",
        svg_element="path",
        requires_fill=False,
        requires_stroke=True,
        requires_satin_rails=False,
        inkstitch_method="ripple_stitch",
        default_params={
            "running_stitch_length_mm": 2.5,
            "line_count": 10,
            "skip_start": 0,
            "skip_end": 0,
        },
        supported_params=[
            "running_stitch_length_mm",
            "line_count",
            "skip_start",
            "skip_end",
            "exponent",
            "flip_exponent",
            "reverse",
        ],
    ),
    StitchType.ZIGZAG_STITCH: StitchTypeInfo(
        stitch_type=StitchType.ZIGZAG_STITCH,
        category=StitchCategory.STROKE,
        display_name="Zigzag Stitch",
        description="Simple zigzag along a path. Uses stroke-width for zigzag width.",
        svg_element="path",
        requires_fill=False,
        requires_stroke=True,
        requires_satin_rails=False,
        inkstitch_method="zigzag_stitch",
        default_params={
            "zigzag_spacing_mm": 0.4,
        },
        supported_params=[
            "zigzag_spacing_mm",
        ],
    ),
    # ══════════════════════════════════════════════════════════════
    # SATIN-BASED STITCHES
    # ══════════════════════════════════════════════════════════════
    StitchType.SATIN_COLUMN: StitchTypeInfo(
        stitch_type=StitchType.SATIN_COLUMN,
        category=StitchCategory.SATIN,
        display_name="Satin Column",
        description="Classic satin stitch between two rails. Great for text, borders, details.",
        svg_element="path",
        requires_fill=False,
        requires_stroke=True,
        requires_satin_rails=True,  # Needs two subpaths
        inkstitch_method="satin_column",
        default_params={
            "zigzag_spacing_mm": 0.4,
            "pull_compensation_mm": 0.0,
            "pull_compensation_percent": 0,
            "contour_underlay": False,
            "center_walk_underlay": False,
            "zigzag_underlay": False,
        },
        supported_params=[
            "zigzag_spacing_mm",
            "pull_compensation_mm",
            "pull_compensation_percent",
            "contour_underlay",
            "contour_underlay_stitch_length_mm",
            "contour_underlay_inset_mm",
            "contour_underlay_inset_percent",
            "center_walk_underlay",
            "center_walk_underlay_stitch_length_mm",
            "zigzag_underlay",
            "zigzag_underlay_spacing_mm",
            "zigzag_underlay_inset_mm",
            "zigzag_underlay_inset_percent",
            "random_width_decrease_percent",
            "random_width_increase_percent",
            "random_zigzag_spacing_percent",
            "split_method",
            "short_stitch_distance_mm",
            "short_stitch_inset",
            "min_random_split_length_mm",
            "random_split_jitter_percent",
        ],
    ),
    StitchType.E_STITCH: StitchTypeInfo(
        stitch_type=StitchType.E_STITCH,
        category=StitchCategory.SATIN,
        display_name="E-Stitch",
        description="Satin variant with E-shaped pattern. Good for stretchy fabrics.",
        svg_element="path",
        requires_fill=False,
        requires_stroke=True,
        requires_satin_rails=True,
        inkstitch_method="e_stitch",
        default_params={
            "zigzag_spacing_mm": 0.4,
        },
        supported_params=[
            "zigzag_spacing_mm",
            "pull_compensation_mm",
        ],
    ),
    StitchType.S_STITCH: StitchTypeInfo(
        stitch_type=StitchType.S_STITCH,
        category=StitchCategory.SATIN,
        display_name="S-Stitch",
        description="Satin variant with S-shaped pattern. Good for stretchy fabrics.",
        svg_element="path",
        requires_fill=False,
        requires_stroke=True,
        requires_satin_rails=True,
        inkstitch_method="s_stitch",
        default_params={
            "zigzag_spacing_mm": 0.4,
        },
        supported_params=[
            "zigzag_spacing_mm",
            "pull_compensation_mm",
        ],
    ),
    # ══════════════════════════════════════════════════════════════
    # FILL-BASED STITCHES
    # ══════════════════════════════════════════════════════════════
    StitchType.FILL_STITCH: StitchTypeInfo(
        stitch_type=StitchType.FILL_STITCH,
        category=StitchCategory.FILL,
        display_name="Fill Stitch",
        description="Standard fill with rows of stitches. Default for filled shapes.",
        svg_element="path",
        requires_fill=True,
        requires_stroke=False,
        requires_satin_rails=False,
        inkstitch_method="fill",
        default_params={
            "fill_angle": 0,
            "row_spacing_mm": 0.25,
            "stagger_rows": 4,
            "max_stitch_length_mm": 3.0,
            "fill_underlay": False,
        },
        supported_params=[
            "fill_angle",
            "row_spacing_mm",
            "stagger_rows",
            "max_stitch_length_mm",
            "fill_underlay",
            "fill_underlay_angle",
            "fill_underlay_row_spacing_mm",
            "fill_underlay_max_stitch_length_mm",
            "fill_underlay_inset_mm",
            "fill_underlay_skip_last",
            "underpath",
            "underpath_length_mm",
            "expand_mm",
        ],
    ),
    StitchType.AUTO_FILL: StitchTypeInfo(
        stitch_type=StitchType.AUTO_FILL,
        category=StitchCategory.FILL,
        display_name="Auto Fill",
        description="Automatic fill that handles complex shapes with holes.",
        svg_element="path",
        requires_fill=True,
        requires_stroke=False,
        requires_satin_rails=False,
        inkstitch_method="auto_fill",
        default_params={
            "fill_angle": 0,
            "row_spacing_mm": 0.25,
            "max_stitch_length_mm": 3.0,
            "running_stitch_length_mm": 1.5,
        },
        supported_params=[
            "fill_angle",
            "row_spacing_mm",
            "max_stitch_length_mm",
            "running_stitch_length_mm",
            "fill_underlay",
            "fill_underlay_angle",
            "fill_underlay_row_spacing_mm",
            "fill_underlay_max_stitch_length_mm",
            "underpath",
            "expand_mm",
            "staggers",
        ],
    ),
    StitchType.CONTOUR_FILL: StitchTypeInfo(
        stitch_type=StitchType.CONTOUR_FILL,
        category=StitchCategory.FILL,
        display_name="Contour Fill",
        description="Fill following shape contours inward. Creates concentric pattern.",
        svg_element="path",
        requires_fill=True,
        requires_stroke=False,
        requires_satin_rails=False,
        inkstitch_method="contour_fill",
        default_params={
            "row_spacing_mm": 0.25,
            "max_stitch_length_mm": 3.0,
            "clockwise": True,
        },
        supported_params=[
            "row_spacing_mm",
            "max_stitch_length_mm",
            "running_stitch_length_mm",
            "clockwise",
            "fill_underlay",
        ],
    ),
    StitchType.GUIDED_FILL: StitchTypeInfo(
        stitch_type=StitchType.GUIDED_FILL,
        category=StitchCategory.FILL,
        display_name="Guided Fill",
        description="Fill with direction guided by a separate line. Great for shading.",
        svg_element="path",
        requires_fill=True,
        requires_stroke=False,
        requires_satin_rails=False,
        inkstitch_method="guided_fill",
        default_params={
            "row_spacing_mm": 0.25,
            "max_stitch_length_mm": 3.0,
        },
        supported_params=[
            "row_spacing_mm",
            "max_stitch_length_mm",
            "running_stitch_length_mm",
            "guide",  # Reference to guide line element
        ],
    ),
    StitchType.MEANDER_FILL: StitchTypeInfo(
        stitch_type=StitchType.MEANDER_FILL,
        category=StitchCategory.FILL,
        display_name="Meander Fill",
        description="Space-filling curve pattern. Decorative quilting-style fill.",
        svg_element="path",
        requires_fill=True,
        requires_stroke=False,
        requires_satin_rails=False,
        inkstitch_method="meander_fill",
        default_params={
            "meander_pattern": "square",
            "meander_scale_percent": 100,
        },
        supported_params=[
            "meander_pattern",
            "meander_scale_percent",
            "running_stitch_length_mm",
            "fill_underlay",
        ],
    ),
    StitchType.CIRCULAR_FILL: StitchTypeInfo(
        stitch_type=StitchType.CIRCULAR_FILL,
        category=StitchCategory.FILL,
        display_name="Circular Fill",
        description="Spiral/circular fill pattern radiating from center.",
        svg_element="path",
        requires_fill=True,
        requires_stroke=False,
        requires_satin_rails=False,
        inkstitch_method="circular_fill",
        default_params={
            "row_spacing_mm": 0.25,
            "max_stitch_length_mm": 3.0,
        },
        supported_params=[
            "row_spacing_mm",
            "max_stitch_length_mm",
            "running_stitch_length_mm",
            "fill_underlay",
        ],
    ),
    StitchType.LINEAR_GRADIENT_FILL: StitchTypeInfo(
        stitch_type=StitchType.LINEAR_GRADIENT_FILL,
        category=StitchCategory.FILL,
        display_name="Linear Gradient Fill",
        description="Fill with varying density creating gradient effect.",
        svg_element="path",
        requires_fill=True,
        requires_stroke=False,
        requires_satin_rails=False,
        inkstitch_method="linear_gradient_fill",
        default_params={
            "row_spacing_mm": 0.25,
            "max_stitch_length_mm": 3.0,
        },
        supported_params=[
            "row_spacing_mm",
            "max_stitch_length_mm",
            "gradient_start_percent",
            "gradient_end_percent",
        ],
    ),
    StitchType.TARTAN_FILL: StitchTypeInfo(
        stitch_type=StitchType.TARTAN_FILL,
        category=StitchCategory.FILL,
        display_name="Tartan Fill",
        description="Plaid/tartan pattern fill. Overlapping perpendicular lines.",
        svg_element="path",
        requires_fill=True,
        requires_stroke=False,
        requires_satin_rails=False,
        inkstitch_method="tartan_fill",
        default_params={
            "row_spacing_mm": 0.5,
            "max_stitch_length_mm": 3.0,
        },
        supported_params=[
            "row_spacing_mm",
            "max_stitch_length_mm",
            "tartan_angle",
        ],
    ),
    StitchType.CROSS_STITCH: StitchTypeInfo(
        stitch_type=StitchType.CROSS_STITCH,
        category=StitchCategory.FILL,
        display_name="Cross Stitch",
        description="Traditional cross-stitch pattern. Grid of X stitches.",
        svg_element="path",
        requires_fill=True,
        requires_stroke=False,
        requires_satin_rails=False,
        inkstitch_method="cross_stitch",
        default_params={
            "cross_stitch_size_mm": 2.0,
        },
        supported_params=[
            "cross_stitch_size_mm",
        ],
    ),
}


def get_stitch_type(name: str) -> Optional[StitchType]:
    """
    Get a StitchType by name (case-insensitive).

    Args:
        name: Stitch type name (e.g., "running_stitch", "SATIN_COLUMN", "fill")

    Returns:
        StitchType enum value or None if not found
    """
    name_upper = name.upper().replace(" ", "_").replace("-", "_")

    # Direct enum lookup
    try:
        return StitchType[name_upper]
    except KeyError:
        pass

    # Try matching by value
    for st in StitchType:
        if st.value.upper() == name_upper:
            return st

    # Try partial matching for convenience
    aliases = {
        "RUNNING": StitchType.RUNNING_STITCH,
        "BEAN": StitchType.BEAN_STITCH,
        "MANUAL": StitchType.MANUAL_STITCH,
        "RIPPLE": StitchType.RIPPLE_STITCH,
        "ZIGZAG": StitchType.ZIGZAG_STITCH,
        "SATIN": StitchType.SATIN_COLUMN,
        "FILL": StitchType.FILL_STITCH,
        "AUTO": StitchType.AUTO_FILL,
        "AUTOFILL": StitchType.AUTO_FILL,
        "CONTOUR": StitchType.CONTOUR_FILL,
        "GUIDED": StitchType.GUIDED_FILL,
        "MEANDER": StitchType.MEANDER_FILL,
        "CIRCULAR": StitchType.CIRCULAR_FILL,
        "GRADIENT": StitchType.LINEAR_GRADIENT_FILL,
        "TARTAN": StitchType.TARTAN_FILL,
        "CROSS": StitchType.CROSS_STITCH,
        "CROSSSTITCH": StitchType.CROSS_STITCH,
    }

    return aliases.get(name_upper)


def get_stitch_info(stitch_type: StitchType) -> StitchTypeInfo:
    """
    Get complete information about a stitch type.

    Args:
        stitch_type: StitchType enum value

    Returns:
        StitchTypeInfo dataclass with all stitch information
    """
    return STITCH_TYPES[stitch_type]


def get_stitch_attributes(
    stitch_type: StitchType,
    thread_color: str = "#000000",
    custom_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, str]:
    """
    Generate SVG attributes for applying a stitch type to an element.

    This creates the Ink/Stitch-compatible attributes that should be
    added to an SVG element to make it embroider with the specified stitch.

    Args:
        stitch_type: The stitch type to apply
        thread_color: Thread color in hex format (default: black)
        custom_params: Optional parameter overrides

    Returns:
        Dictionary of SVG attribute names and values
    """
    info = STITCH_TYPES[stitch_type]
    params = {**info.default_params, **(custom_params or {})}

    # Base attributes
    attrs: Dict[str, str] = {}

    # Set stroke or fill based on stitch requirements
    if info.requires_stroke:
        attrs["stroke"] = thread_color
        attrs["fill"] = "none"
        attrs["stroke-width"] = "1"  # Visual only, not stitch width
    elif info.requires_fill:
        attrs["fill"] = thread_color
        attrs["stroke"] = "none"

    # Ink/Stitch namespace attributes
    # Note: Ink/Stitch uses inkstitch: prefix for its custom attributes
    inkstitch_prefix = "{http://inkstitch.org/namespace}"

    # Apply stitch-type specific parameters
    for param_name, param_value in params.items():
        # Convert Python booleans to lowercase strings
        if isinstance(param_value, bool):
            param_value = "true" if param_value else "false"

        # Ink/Stitch params use underscores, stored with inkstitch namespace
        attr_name = f"{inkstitch_prefix}{param_name}"
        attrs[attr_name] = str(param_value)

    return attrs


def get_stitch_types_by_category(category: StitchCategory) -> List[StitchType]:
    """
    Get all stitch types in a category.

    Args:
        category: StitchCategory (STROKE, SATIN, or FILL)

    Returns:
        List of StitchType enum values in that category
    """
    return [st for st, info in STITCH_TYPES.items() if info.category == category]


def list_all_stitch_types() -> List[Dict[str, Any]]:
    """
    Get a summary of all available stitch types.

    Returns:
        List of dicts with stitch type information for display/selection
    """
    return [
        {
            "name": st.value,
            "display_name": info.display_name,
            "category": info.category.value,
            "description": info.description,
            "requires_satin_rails": info.requires_satin_rails,
        }
        for st, info in STITCH_TYPES.items()
    ]
