"""
Embroidery Presets Module

Pre-configured embroidery templates and common design patterns for quick creation.
These presets combine shape generation with optimized stitch parameters for
common embroidery use cases.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

from .stitch_types import StitchType
from .parameters import UnderlayType
from .embroidery_operations import (
    create_embroidery_shape,
    build_embroidery_element,
    elements_to_group_command,
    create_rectangle_path,
    create_circle_path,
    create_ellipse_path,
)

# Import common utilities
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from inkmcpops.common import create_success_response, create_error_response


# ══════════════════════════════════════════════════════════════════════════════
# PRESET DEFINITIONS
# ══════════════════════════════════════════════════════════════════════════════


class PresetCategory(Enum):
    """Categories of embroidery presets"""

    BASIC = "basic"  # Simple shapes
    TEXT = "text"  # Text and lettering
    BORDERS = "borders"  # Decorative borders
    PATCHES = "patches"  # Patch/badge designs
    APPLIQUE = "applique"  # Applique techniques
    QUILTING = "quilting"  # Quilting patterns


@dataclass
class EmbroideryPreset:
    """Definition of an embroidery preset"""

    name: str
    display_name: str
    category: PresetCategory
    description: str
    stitch_type: StitchType
    default_params: Dict[str, Any] = field(default_factory=dict)
    shape_type: str = "rectangle"
    recommended_sizes: List[Tuple[float, float]] = field(
        default_factory=list
    )  # (width, height)
    thread_colors: List[str] = field(default_factory=list)  # Suggested colors
    notes: str = ""


# ══════════════════════════════════════════════════════════════════════════════
# BASIC SHAPE PRESETS
# ══════════════════════════════════════════════════════════════════════════════

BASIC_PRESETS = {
    "filled_rectangle": EmbroideryPreset(
        name="filled_rectangle",
        display_name="Filled Rectangle",
        category=PresetCategory.BASIC,
        description="Simple filled rectangle with auto-fill stitches",
        stitch_type=StitchType.AUTO_FILL,
        default_params={
            "fill_angle": 45,
            "row_spacing": 0.25,
            "stitch_length": 3.0,
            "fill_underlay": True,
            "fill_underlay_angle": 135,  # Perpendicular
        },
        shape_type="rectangle",
        recommended_sizes=[(50, 30), (100, 60), (150, 100)],
        thread_colors=["#FF0000", "#0000FF", "#00FF00", "#FFD700"],
        notes="Good for solid color patches and labels",
    ),
    "filled_circle": EmbroideryPreset(
        name="filled_circle",
        display_name="Filled Circle",
        category=PresetCategory.BASIC,
        description="Circular fill with optimized stitch angles",
        stitch_type=StitchType.AUTO_FILL,
        default_params={
            "fill_angle": 0,
            "row_spacing": 0.25,
            "stitch_length": 2.5,
            "fill_underlay": True,
            "fill_underlay_angle": 90,
        },
        shape_type="circle",
        recommended_sizes=[(40, 40), (60, 60), (100, 100)],
        thread_colors=["#FF0000", "#FFD700", "#FFFFFF"],
        notes="Use for dots, badges, and circular elements",
    ),
    "contour_circle": EmbroideryPreset(
        name="contour_circle",
        display_name="Contour Circle",
        category=PresetCategory.BASIC,
        description="Circle with concentric contour fill stitches",
        stitch_type=StitchType.CONTOUR_FILL,
        default_params={
            "row_spacing": 0.4,
            "stitch_length": 2.5,
            "contour_strategy": "inner_to_outer",
        },
        shape_type="circle",
        recommended_sizes=[(50, 50), (80, 80)],
        notes="Creates interesting concentric ring effect",
    ),
    "running_outline": EmbroideryPreset(
        name="running_outline",
        display_name="Running Stitch Outline",
        category=PresetCategory.BASIC,
        description="Simple running stitch outline for any shape",
        stitch_type=StitchType.RUNNING_STITCH,
        default_params={
            "stitch_length": 2.0,
            "running_stitch_tolerance": 0.2,
        },
        shape_type="rectangle",
        recommended_sizes=[(50, 30), (100, 60)],
        thread_colors=["#000000", "#FFFFFF", "#C0C0C0"],
        notes="Quick outline, minimal thread usage",
    ),
    "bean_outline": EmbroideryPreset(
        name="bean_outline",
        display_name="Bean Stitch Outline",
        category=PresetCategory.BASIC,
        description="Triple-reinforced outline using bean stitch",
        stitch_type=StitchType.BEAN_STITCH,
        default_params={
            "stitch_length": 2.5,
            "bean_stitch_repeats": 2,  # Triple stitch
        },
        shape_type="rectangle",
        recommended_sizes=[(50, 30), (100, 60)],
        notes="Bolder outline than running stitch, good for emphasis",
    ),
}


# ══════════════════════════════════════════════════════════════════════════════
# BORDER PRESETS
# ══════════════════════════════════════════════════════════════════════════════

BORDER_PRESETS = {
    "satin_border": EmbroideryPreset(
        name="satin_border",
        display_name="Satin Border",
        category=PresetCategory.BORDERS,
        description="Smooth satin column border for professional edges",
        stitch_type=StitchType.SATIN_COLUMN,
        default_params={
            "satin_column_width": 3.0,  # mm
            "zigzag_spacing": 0.4,
            "pull_compensation": 0.3,
            "center_walk_underlay": True,
            "contour_underlay": True,
        },
        shape_type="rectangle",
        recommended_sizes=[(60, 40), (100, 60), (150, 100)],
        notes="Requires two-rail path. Best for 2-5mm width borders.",
    ),
    "zigzag_border": EmbroideryPreset(
        name="zigzag_border",
        display_name="Zigzag Border",
        category=PresetCategory.BORDERS,
        description="Decorative zigzag border pattern",
        stitch_type=StitchType.ZIGZAG_STITCH,
        default_params={
            "stitch_length": 2.0,
            "zigzag_width": 2.5,
        },
        shape_type="rectangle",
        notes="Good for decorative edges and vintage style",
    ),
    "ripple_border": EmbroideryPreset(
        name="ripple_border",
        display_name="Ripple Border",
        category=PresetCategory.BORDERS,
        description="Wavy ripple stitch border effect",
        stitch_type=StitchType.RIPPLE_STITCH,
        default_params={
            "stitch_length": 2.5,
            "ripple_spacing": 3.0,
            "ripple_line_count": 3,
        },
        shape_type="rectangle",
        notes="Creates organic, flowing border effect",
    ),
}


# ══════════════════════════════════════════════════════════════════════════════
# PATCH & BADGE PRESETS
# ══════════════════════════════════════════════════════════════════════════════

PATCH_PRESETS = {
    "simple_patch": EmbroideryPreset(
        name="simple_patch",
        display_name="Simple Patch",
        category=PresetCategory.PATCHES,
        description="Basic embroidered patch with fill and satin border",
        stitch_type=StitchType.AUTO_FILL,
        default_params={
            "fill_angle": 45,
            "row_spacing": 0.25,
            "fill_underlay": True,
            "fill_underlay_angle": 135,
        },
        shape_type="rectangle",
        recommended_sizes=[(50, 50), (75, 50), (100, 75)],
        notes="Combine with satin_border preset for complete patch",
    ),
    "circular_badge": EmbroideryPreset(
        name="circular_badge",
        display_name="Circular Badge",
        category=PresetCategory.PATCHES,
        description="Round badge/patch design",
        stitch_type=StitchType.AUTO_FILL,
        default_params={
            "fill_angle": 0,
            "row_spacing": 0.25,
            "stitch_length": 2.5,
            "fill_underlay": True,
        },
        shape_type="circle",
        recommended_sizes=[(50, 50), (75, 75), (100, 100)],
        notes="Classic badge shape. Add satin border for finished look.",
    ),
    "oval_badge": EmbroideryPreset(
        name="oval_badge",
        display_name="Oval Badge",
        category=PresetCategory.PATCHES,
        description="Oval/elliptical badge design",
        stitch_type=StitchType.AUTO_FILL,
        default_params={
            "fill_angle": 0,
            "row_spacing": 0.25,
            "fill_underlay": True,
        },
        shape_type="ellipse",
        recommended_sizes=[(80, 50), (100, 60), (120, 80)],
        notes="Good for name badges and labels",
    ),
}


# ══════════════════════════════════════════════════════════════════════════════
# QUILTING PRESETS
# ══════════════════════════════════════════════════════════════════════════════

QUILTING_PRESETS = {
    "meander_fill": EmbroideryPreset(
        name="meander_fill",
        display_name="Meander/Stipple Fill",
        category=PresetCategory.QUILTING,
        description="Free-motion style meandering fill pattern",
        stitch_type=StitchType.MEANDER_FILL,
        default_params={
            "stitch_length": 2.5,
            "meander_scale": 5.0,
            "meander_pattern": "stipple",
        },
        shape_type="rectangle",
        recommended_sizes=[(100, 100), (150, 150)],
        notes="Classic quilting fill. Adjustable density via meander_scale.",
    ),
    "circular_fill": EmbroideryPreset(
        name="circular_fill",
        display_name="Circular Fill",
        category=PresetCategory.QUILTING,
        description="Concentric circular fill pattern",
        stitch_type=StitchType.CIRCULAR_FILL,
        default_params={
            "row_spacing": 3.0,
            "stitch_length": 2.5,
        },
        shape_type="rectangle",
        recommended_sizes=[(100, 100), (150, 150)],
        notes="Creates spiral/bullseye effect from center",
    ),
    "linear_gradient": EmbroideryPreset(
        name="linear_gradient",
        display_name="Linear Gradient Fill",
        category=PresetCategory.QUILTING,
        description="Gradient density fill pattern",
        stitch_type=StitchType.LINEAR_GRADIENT_FILL,
        default_params={
            "fill_angle": 0,
            "row_spacing": 0.25,
        },
        shape_type="rectangle",
        notes="Creates shading effect with varying density",
    ),
}


# ══════════════════════════════════════════════════════════════════════════════
# APPLIQUE PRESETS
# ══════════════════════════════════════════════════════════════════════════════

APPLIQUE_PRESETS = {
    "applique_placement": EmbroideryPreset(
        name="applique_placement",
        display_name="Applique Placement Line",
        category=PresetCategory.APPLIQUE,
        description="Running stitch to mark fabric placement",
        stitch_type=StitchType.RUNNING_STITCH,
        default_params={
            "stitch_length": 3.0,
        },
        shape_type="rectangle",
        notes="First step: marks where to place applique fabric",
    ),
    "applique_tack": EmbroideryPreset(
        name="applique_tack",
        display_name="Applique Tack Down",
        category=PresetCategory.APPLIQUE,
        description="Zigzag stitch to tack fabric in place",
        stitch_type=StitchType.ZIGZAG_STITCH,
        default_params={
            "stitch_length": 1.5,
            "zigzag_width": 1.5,
        },
        shape_type="rectangle",
        notes="Second step: secures fabric before final border",
    ),
    "applique_border": EmbroideryPreset(
        name="applique_border",
        display_name="Applique Satin Border",
        category=PresetCategory.APPLIQUE,
        description="Satin border to finish applique edge",
        stitch_type=StitchType.SATIN_COLUMN,
        default_params={
            "satin_column_width": 3.5,
            "zigzag_spacing": 0.35,
            "pull_compensation": 0.4,
            "center_walk_underlay": True,
        },
        shape_type="rectangle",
        notes="Final step: covers raw edge with smooth satin",
    ),
}


# ══════════════════════════════════════════════════════════════════════════════
# COMBINED PRESET DICTIONARY
# ══════════════════════════════════════════════════════════════════════════════

ALL_PRESETS: Dict[str, EmbroideryPreset] = {
    **BASIC_PRESETS,
    **BORDER_PRESETS,
    **PATCH_PRESETS,
    **QUILTING_PRESETS,
    **APPLIQUE_PRESETS,
}


# ══════════════════════════════════════════════════════════════════════════════
# PRESET OPERATIONS
# ══════════════════════════════════════════════════════════════════════════════


def list_presets(category: Optional[str] = None) -> Dict[str, Any]:
    """
    List available embroidery presets.

    Args:
        category: Optional filter by category

    Returns:
        Success response with preset list
    """
    presets = []

    for name, preset in ALL_PRESETS.items():
        if category and preset.category.value != category.lower():
            continue

        presets.append(
            {
                "name": preset.name,
                "display_name": preset.display_name,
                "category": preset.category.value,
                "description": preset.description,
                "stitch_type": preset.stitch_type.value,
                "shape_type": preset.shape_type,
            }
        )

    # Group by category
    by_category = {}
    for p in presets:
        cat = p["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(p)

    return create_success_response(
        f"Found {len(presets)} presets",
        presets=presets,
        by_category=by_category,
        categories=list(by_category.keys()),
    )


def get_preset(preset_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a preset.

    Args:
        preset_name: Name of the preset

    Returns:
        Preset details
    """
    preset = ALL_PRESETS.get(preset_name)
    if not preset:
        return create_error_response(
            f"Unknown preset: {preset_name}. Available: {list(ALL_PRESETS.keys())}"
        )

    return create_success_response(
        f"Preset: {preset.display_name}",
        name=preset.name,
        display_name=preset.display_name,
        category=preset.category.value,
        description=preset.description,
        stitch_type=preset.stitch_type.value,
        shape_type=preset.shape_type,
        default_params=preset.default_params,
        recommended_sizes=preset.recommended_sizes,
        thread_colors=preset.thread_colors,
        notes=preset.notes,
    )


def create_from_preset(
    preset_name: str,
    element_id: str,
    thread_color: str = "#000000",
    x: float = 0,
    y: float = 0,
    width: float = 100,
    height: float = 100,
    param_overrides: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create an embroidery element using a preset configuration.

    Args:
        preset_name: Name of the preset to use
        element_id: Unique ID for the element
        thread_color: Thread color
        x, y: Position
        width, height: Size (or radius for circles)
        param_overrides: Optional parameter overrides

    Returns:
        Created element with InkMCP command
    """
    preset = ALL_PRESETS.get(preset_name)
    if not preset:
        return create_error_response(f"Unknown preset: {preset_name}")

    # Merge default params with overrides
    params = dict(preset.default_params)
    if param_overrides:
        params.update(param_overrides)

    # Build shape params
    shape_params = {}
    if preset.shape_type == "rectangle":
        shape_params = {"x": x, "y": y, "width": width, "height": height}
    elif preset.shape_type == "circle":
        # Use width as diameter
        r = width / 2
        shape_params = {"cx": x + r, "cy": y + r, "r": r}
    elif preset.shape_type == "ellipse":
        rx = width / 2
        ry = height / 2
        shape_params = {"cx": x + rx, "cy": y + ry, "rx": rx, "ry": ry}

    # Create element
    result = create_embroidery_shape(
        shape_type=preset.shape_type,
        element_id=element_id,
        stitch_type=preset.stitch_type.value,
        thread_color=thread_color,
        params=params,
        **shape_params,
    )

    # Add preset info to response
    if result.get("status") == "success":
        result["data"]["preset_name"] = preset_name
        result["data"]["preset_display_name"] = preset.display_name

    return result


def create_patch_design(
    element_id: str,
    x: float = 0,
    y: float = 0,
    width: float = 75,
    height: float = 50,
    fill_color: str = "#FF0000",
    border_color: str = "#000000",
    shape: str = "rectangle",
) -> Dict[str, Any]:
    """
    Create a complete patch design with fill and border.

    This is a high-level function that creates a typical embroidered patch
    with a filled interior and satin column border.

    Args:
        element_id: Base ID for elements (creates {id}_fill and {id}_border)
        x, y: Position
        width, height: Size
        fill_color: Fill stitch color
        border_color: Border stitch color
        shape: Shape type ("rectangle", "circle", "ellipse")

    Returns:
        Group element with fill and border
    """
    elements = []

    # Create fill element
    fill_result = create_from_preset(
        preset_name="simple_patch" if shape == "rectangle" else "circular_badge",
        element_id=f"{element_id}_fill",
        thread_color=fill_color,
        x=x,
        y=y,
        width=width,
        height=height,
    )

    if fill_result.get("status") != "success":
        return fill_result

    elements.append(fill_result["data"]["element"])

    # Note: Border would require satin column path generation
    # For now, return just the fill with a note about adding border manually

    # Generate group command
    group_cmd = elements_to_group_command(
        group_id=element_id,
        elements=elements,
        group_label=f"Patch: {element_id}",
    )

    return create_success_response(
        f"Created patch design: {element_id}",
        elements=elements,
        group_command=group_cmd,
        notes="Add satin column border manually for complete patch effect",
    )


def create_applique_sequence(
    element_id: str,
    x: float = 0,
    y: float = 0,
    width: float = 100,
    height: float = 75,
    placement_color: str = "#808080",
    tack_color: str = "#808080",
    border_color: str = "#000000",
) -> Dict[str, Any]:
    """
    Create a complete applique stitch sequence.

    Generates three elements in the correct order:
    1. Placement line (running stitch)
    2. Tack down (zigzag)
    3. Satin border (final cover)

    Args:
        element_id: Base ID for elements
        x, y: Position
        width, height: Size
        placement_color: Color for placement stitches
        tack_color: Color for tack down stitches
        border_color: Color for satin border

    Returns:
        Sequence of elements with commands
    """
    elements = []
    commands = []

    # Step 1: Placement
    placement = create_from_preset(
        preset_name="applique_placement",
        element_id=f"{element_id}_placement",
        thread_color=placement_color,
        x=x,
        y=y,
        width=width,
        height=height,
    )
    if placement.get("status") == "success":
        elements.append(placement["data"]["element"])
        commands.append(("1. Placement Line", placement["data"]["command"]))

    # Step 2: Tack down
    tack = create_from_preset(
        preset_name="applique_tack",
        element_id=f"{element_id}_tack",
        thread_color=tack_color,
        x=x,
        y=y,
        width=width,
        height=height,
    )
    if tack.get("status") == "success":
        elements.append(tack["data"]["element"])
        commands.append(("2. Tack Down", tack["data"]["command"]))

    # Step 3: Border (note: would need satin path for real applique)
    # For now, create a bean stitch outline as placeholder
    border = create_from_preset(
        preset_name="bean_outline",
        element_id=f"{element_id}_border",
        thread_color=border_color,
        x=x,
        y=y,
        width=width,
        height=height,
    )
    if border.get("status") == "success":
        elements.append(border["data"]["element"])
        commands.append(
            ("3. Border (use satin for production)", border["data"]["command"])
        )

    return create_success_response(
        f"Created applique sequence: {element_id}",
        elements=elements,
        steps=commands,
        notes="Execute steps in order. Add COLOR STOP between steps if supported by machine.",
    )


# ══════════════════════════════════════════════════════════════════════════════
# MACHINE-SPECIFIC PRESETS
# ══════════════════════════════════════════════════════════════════════════════


def get_machine_optimized_params(machine_type: str) -> Dict[str, Any]:
    """
    Get optimized parameters for specific embroidery machine types.

    Args:
        machine_type: Machine type ("home", "commercial", "industrial")

    Returns:
        Optimized parameter recommendations
    """
    machine_params = {
        "home": {
            "description": "Home embroidery machines (Brother, Janome, Singer)",
            "max_speed": "medium",
            "params": {
                "stitch_length": 2.5,
                "row_spacing": 0.3,
                "pull_compensation": 0.2,
                "underlay": True,
            },
            "notes": "Conservative settings for reliable home machine output",
        },
        "commercial": {
            "description": "Commercial machines (Tajima, Barudan, SWF)",
            "max_speed": "high",
            "params": {
                "stitch_length": 3.0,
                "row_spacing": 0.25,
                "pull_compensation": 0.3,
                "underlay": True,
            },
            "notes": "Optimized for speed and production quality",
        },
        "industrial": {
            "description": "Industrial multi-head machines",
            "max_speed": "very_high",
            "params": {
                "stitch_length": 3.5,
                "row_spacing": 0.2,
                "pull_compensation": 0.4,
                "underlay": True,
            },
            "notes": "Maximum production efficiency settings",
        },
    }

    if machine_type not in machine_params:
        return create_error_response(
            f"Unknown machine type: {machine_type}. "
            f"Options: {list(machine_params.keys())}"
        )

    params = machine_params[machine_type]
    return create_success_response(
        f"Parameters for {machine_type} machines",
        machine_type=machine_type,
        **params,
    )
