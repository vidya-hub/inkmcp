"""
Embroidery Operations Module

Provides embroidery-specific operations for InkMCP integration with Ink/Stitch.
These operations generate SVG elements and attributes compatible with Ink/Stitch
for AI-assisted embroidery design creation.

This module focuses on generating the correct SVG structure and attributes;
actual stitch generation is handled by Ink/Stitch when the design is processed.
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from .stitch_types import (
    StitchType,
    StitchCategory,
    STITCH_TYPES,
    get_stitch_type,
    get_stitch_info,
)
from .parameters import (
    INKSTITCH_NAMESPACE,
    INKSCAPE_NAMESPACE,
    EmbroideryParams,
    PARAM_SPECS,
    validate_params,
)

# Import common utilities from inkmcpops
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from inkmcpops.common import create_success_response, create_error_response


# ══════════════════════════════════════════════════════════════════════════════
# SVG PATH UTILITIES
# ══════════════════════════════════════════════════════════════════════════════


def create_satin_path(
    rail1_points: List[Tuple[float, float]],
    rail2_points: List[Tuple[float, float]],
) -> str:
    """
    Create an SVG path string for a satin column (two-rail path).

    Satin columns in Ink/Stitch require a path with exactly two subpaths
    (the "rails") that define the width and direction of the satin stitch.

    Args:
        rail1_points: List of (x, y) tuples for the first rail
        rail2_points: List of (x, y) tuples for the second rail

    Returns:
        SVG path d attribute string with two subpaths
    """
    if len(rail1_points) < 2 or len(rail2_points) < 2:
        raise ValueError("Each rail must have at least 2 points")

    def points_to_path(points: List[Tuple[float, float]]) -> str:
        """Convert points to SVG path commands"""
        if not points:
            return ""

        # Start with move command
        path_parts = [f"M {points[0][0]},{points[0][1]}"]

        # Add line commands for remaining points
        for x, y in points[1:]:
            path_parts.append(f"L {x},{y}")

        return " ".join(path_parts)

    # Combine two rails into a single path with two subpaths
    rail1_path = points_to_path(rail1_points)
    rail2_path = points_to_path(rail2_points)

    return f"{rail1_path} {rail2_path}"


def create_closed_path(points: List[Tuple[float, float]]) -> str:
    """
    Create a closed SVG path from a list of points.

    Args:
        points: List of (x, y) tuples defining the shape boundary

    Returns:
        SVG path d attribute string with Z (close) command
    """
    if len(points) < 3:
        raise ValueError("Closed path requires at least 3 points")

    # Start with move command
    path_parts = [f"M {points[0][0]},{points[0][1]}"]

    # Add line commands for remaining points
    for x, y in points[1:]:
        path_parts.append(f"L {x},{y}")

    # Close the path
    path_parts.append("Z")

    return " ".join(path_parts)


def create_stroke_path(points: List[Tuple[float, float]]) -> str:
    """
    Create an open SVG path from a list of points.

    Args:
        points: List of (x, y) tuples defining the stroke

    Returns:
        SVG path d attribute string (open path)
    """
    if len(points) < 2:
        raise ValueError("Stroke path requires at least 2 points")

    # Start with move command
    path_parts = [f"M {points[0][0]},{points[0][1]}"]

    # Add line commands for remaining points
    for x, y in points[1:]:
        path_parts.append(f"L {x},{y}")

    return " ".join(path_parts)


def create_bezier_path(
    points: List[Tuple[float, float, float, float, float, float]],
    start: Tuple[float, float],
) -> str:
    """
    Create a cubic Bezier SVG path.

    Args:
        points: List of (c1x, c1y, c2x, c2y, x, y) tuples for cubic Bezier curves
        start: Starting point (x, y)

    Returns:
        SVG path d attribute string with C (cubic Bezier) commands
    """
    path_parts = [f"M {start[0]},{start[1]}"]

    for c1x, c1y, c2x, c2y, x, y in points:
        path_parts.append(f"C {c1x},{c1y} {c2x},{c2y} {x},{y}")

    return " ".join(path_parts)


# ══════════════════════════════════════════════════════════════════════════════
# SHAPE GENERATORS
# ══════════════════════════════════════════════════════════════════════════════


def create_rectangle_path(
    x: float, y: float, width: float, height: float, closed: bool = True
) -> str:
    """Create a rectangular path"""
    points = [
        (x, y),
        (x + width, y),
        (x + width, y + height),
        (x, y + height),
    ]
    return (
        create_closed_path(points) if closed else create_stroke_path(points + [(x, y)])
    )


def create_circle_path(cx: float, cy: float, r: float, segments: int = 32) -> str:
    """
    Create a circular path approximated with line segments.

    For embroidery, approximating circles with many line segments
    is often preferred over true SVG arcs for predictable stitch placement.
    """
    import math

    points = []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append((x, y))

    return create_closed_path(points)


def create_ellipse_path(
    cx: float, cy: float, rx: float, ry: float, segments: int = 32
) -> str:
    """Create an elliptical path"""
    import math

    points = []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = cx + rx * math.cos(angle)
        y = cy + ry * math.sin(angle)
        points.append((x, y))

    return create_closed_path(points)


def create_satin_rectangle(
    x: float, y: float, width: float, height: float, satin_width: float
) -> str:
    """
    Create a satin column path for a rectangular outline.

    This creates two rails offset by satin_width for a rectangular satin border.
    """
    # Outer rail (clockwise)
    outer = [
        (x, y),
        (x + width, y),
        (x + width, y + height),
        (x, y + height),
        (x, y),  # Close the rectangle
    ]

    # Inner rail (also clockwise, offset inward)
    inset = satin_width
    inner = [
        (x + inset, y + inset),
        (x + width - inset, y + inset),
        (x + width - inset, y + height - inset),
        (x + inset, y + height - inset),
        (x + inset, y + inset),  # Close
    ]

    return create_satin_path(outer, inner)


# ══════════════════════════════════════════════════════════════════════════════
# EMBROIDERY ELEMENT CREATION
# ══════════════════════════════════════════════════════════════════════════════


def build_embroidery_element(
    element_id: str,
    path_d: str,
    stitch_type: StitchType,
    thread_color: str = "#000000",
    params: Optional[Dict[str, Any]] = None,
    label: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build a complete embroidery element specification.

    This generates the element data structure that can be used to create
    SVG elements with proper Ink/Stitch attributes via InkMCP.

    Args:
        element_id: Unique ID for the element
        path_d: SVG path d attribute
        stitch_type: StitchType enum value
        thread_color: Thread/stroke color in hex format
        params: Optional dictionary of stitch parameters
        label: Optional descriptive label for the element

    Returns:
        Dictionary with element specification for InkMCP
    """
    info = get_stitch_info(stitch_type)

    # Validate and merge parameters
    all_params = {**info.default_params}
    if params:
        validated_params = validate_params(params)
        all_params.update(validated_params)

    # Build base attributes
    attrs = {
        "id": element_id,
        "d": path_d,
    }

    # Set stroke/fill based on stitch type requirements
    if info.requires_stroke:
        attrs["stroke"] = thread_color
        attrs["fill"] = "none"
        attrs["stroke-width"] = "1"  # Visual only
    elif info.requires_fill:
        attrs["fill"] = thread_color
        attrs["stroke"] = "none"

    # Add Inkscape label if provided
    if label:
        attrs[f"{{{INKSCAPE_NAMESPACE}}}label"] = label

    # Add Ink/Stitch parameters
    for param_name, param_value in all_params.items():
        if isinstance(param_value, bool):
            param_value = "true" if param_value else "false"
        attrs[f"{{{INKSTITCH_NAMESPACE}}}{param_name}"] = str(param_value)

    return {
        "tag": "path",
        "attributes": attrs,
        "stitch_type": stitch_type.value,
        "category": info.category.value,
    }


def create_running_stitch_element(
    element_id: str,
    path_d: str,
    thread_color: str = "#000000",
    stitch_length_mm: float = 2.5,
    repeats: int = 1,
    bean_stitch_repeats: int = 0,
    label: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a running stitch element.

    Running stitch follows the path with a single line of stitches.
    Use bean_stitch_repeats > 0 for triple (bean) stitch effect.

    Args:
        element_id: Unique ID for the element
        path_d: SVG path d attribute
        thread_color: Thread color in hex
        stitch_length_mm: Length of each stitch
        repeats: Number of times to stitch the path
        bean_stitch_repeats: Triple stitch passes (0 = normal running)
        label: Optional label

    Returns:
        Element specification dictionary
    """
    stitch_type = (
        StitchType.BEAN_STITCH if bean_stitch_repeats > 0 else StitchType.RUNNING_STITCH
    )

    params = {
        "running_stitch_length_mm": stitch_length_mm,
        "repeats": repeats,
    }
    if bean_stitch_repeats > 0:
        params["bean_stitch_repeats"] = bean_stitch_repeats

    return build_embroidery_element(
        element_id=element_id,
        path_d=path_d,
        stitch_type=stitch_type,
        thread_color=thread_color,
        params=params,
        label=label,
    )


def create_satin_column_element(
    element_id: str,
    rail1_points: List[Tuple[float, float]],
    rail2_points: List[Tuple[float, float]],
    thread_color: str = "#000000",
    zigzag_spacing_mm: float = 0.4,
    pull_compensation_mm: float = 0.0,
    center_walk_underlay: bool = False,
    contour_underlay: bool = False,
    zigzag_underlay: bool = False,
    label: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a satin column element from two rails.

    Satin columns create smooth, dense stitching between two guide paths.
    Great for text, borders, and decorative elements.

    Args:
        element_id: Unique ID for the element
        rail1_points: First rail as list of (x, y) tuples
        rail2_points: Second rail as list of (x, y) tuples
        thread_color: Thread color in hex
        zigzag_spacing_mm: Distance between stitches
        pull_compensation_mm: Extra width for thread pull compensation
        center_walk_underlay: Add center-line underlay
        contour_underlay: Add edge contour underlay
        zigzag_underlay: Add zigzag underlay for density
        label: Optional label

    Returns:
        Element specification dictionary
    """
    path_d = create_satin_path(rail1_points, rail2_points)

    params = {
        "zigzag_spacing_mm": zigzag_spacing_mm,
        "pull_compensation_mm": pull_compensation_mm,
        "center_walk_underlay": center_walk_underlay,
        "contour_underlay": contour_underlay,
        "zigzag_underlay": zigzag_underlay,
    }

    return build_embroidery_element(
        element_id=element_id,
        path_d=path_d,
        stitch_type=StitchType.SATIN_COLUMN,
        thread_color=thread_color,
        params=params,
        label=label,
    )


def create_fill_stitch_element(
    element_id: str,
    path_d: str,
    thread_color: str = "#000000",
    fill_angle: float = 0.0,
    row_spacing_mm: float = 0.25,
    max_stitch_length_mm: float = 3.0,
    fill_underlay: bool = False,
    fill_underlay_angle: Optional[float] = None,
    expand_mm: float = 0.0,
    label: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a fill stitch element.

    Fill stitch covers closed areas with rows of stitches.

    Args:
        element_id: Unique ID for the element
        path_d: Closed SVG path d attribute
        thread_color: Thread color in hex
        fill_angle: Angle of fill rows in degrees
        row_spacing_mm: Distance between rows
        max_stitch_length_mm: Maximum stitch length
        fill_underlay: Add underlay for stability
        fill_underlay_angle: Angle for underlay (default: perpendicular)
        expand_mm: Expand (positive) or contract (negative) the shape
        label: Optional label

    Returns:
        Element specification dictionary
    """
    params = {
        "fill_angle": fill_angle,
        "row_spacing_mm": row_spacing_mm,
        "max_stitch_length_mm": max_stitch_length_mm,
        "fill_underlay": fill_underlay,
        "expand_mm": expand_mm,
    }

    if fill_underlay_angle is not None:
        params["fill_underlay_angle"] = fill_underlay_angle
    elif fill_underlay:
        # Default: perpendicular to fill angle
        params["fill_underlay_angle"] = fill_angle + 90

    return build_embroidery_element(
        element_id=element_id,
        path_d=path_d,
        stitch_type=StitchType.FILL_STITCH,
        thread_color=thread_color,
        params=params,
        label=label,
    )


def create_contour_fill_element(
    element_id: str,
    path_d: str,
    thread_color: str = "#000000",
    row_spacing_mm: float = 0.25,
    max_stitch_length_mm: float = 3.0,
    clockwise: bool = True,
    fill_underlay: bool = False,
    label: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a contour fill element.

    Contour fill follows the shape outline inward, creating concentric patterns.

    Args:
        element_id: Unique ID
        path_d: Closed SVG path
        thread_color: Thread color
        row_spacing_mm: Distance between contours
        max_stitch_length_mm: Maximum stitch length
        clockwise: Stitch direction
        fill_underlay: Add underlay
        label: Optional label

    Returns:
        Element specification dictionary
    """
    params = {
        "row_spacing_mm": row_spacing_mm,
        "max_stitch_length_mm": max_stitch_length_mm,
        "clockwise": clockwise,
        "fill_underlay": fill_underlay,
    }

    return build_embroidery_element(
        element_id=element_id,
        path_d=path_d,
        stitch_type=StitchType.CONTOUR_FILL,
        thread_color=thread_color,
        params=params,
        label=label,
    )


def create_ripple_stitch_element(
    element_id: str,
    path_d: str,
    thread_color: str = "#000000",
    line_count: int = 10,
    stitch_length_mm: float = 2.5,
    exponent: float = 1.0,
    label: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a ripple stitch element.

    Ripple stitch creates wave-like patterns emanating from a path.

    Args:
        element_id: Unique ID
        path_d: SVG path
        thread_color: Thread color
        line_count: Number of ripple lines
        stitch_length_mm: Stitch length
        exponent: Controls ripple spacing distribution
        label: Optional label

    Returns:
        Element specification dictionary
    """
    params = {
        "line_count": line_count,
        "running_stitch_length_mm": stitch_length_mm,
        "exponent": exponent,
    }

    return build_embroidery_element(
        element_id=element_id,
        path_d=path_d,
        stitch_type=StitchType.RIPPLE_STITCH,
        thread_color=thread_color,
        params=params,
        label=label,
    )


# ══════════════════════════════════════════════════════════════════════════════
# COMMAND GENERATION FOR INKMCP
# ══════════════════════════════════════════════════════════════════════════════


def element_to_inkmcp_command(element: Dict[str, Any]) -> str:
    """
    Convert an embroidery element specification to an InkMCP command string.

    This generates the command that can be passed to the inkscape_operation tool.

    Args:
        element: Element specification from create_*_element functions

    Returns:
        InkMCP command string
    """
    attrs = element["attributes"]

    # Build attribute string
    attr_parts = []
    for key, value in attrs.items():
        # Handle namespaced attributes
        if key.startswith("{"):
            # Extract namespace prefix
            ns_end = key.index("}")
            ns_uri = key[1:ns_end]
            local_name = key[ns_end + 1 :]

            # Map namespace to prefix
            if ns_uri == INKSTITCH_NAMESPACE:
                attr_name = f"inkstitch:{local_name}"
            elif ns_uri == INKSCAPE_NAMESPACE:
                attr_name = f"inkscape:{local_name}"
            else:
                attr_name = local_name
        else:
            attr_name = key

        # Quote values with spaces or special characters
        if " " in str(value) or "'" in str(value):
            value = f'"{value}"'
        elif '"' in str(value):
            value = f"'{value}'"

        attr_parts.append(f"{attr_name}={value}")

    return f"{element['tag']} {' '.join(attr_parts)}"


def elements_to_group_command(
    group_id: str,
    elements: List[Dict[str, Any]],
    group_label: Optional[str] = None,
) -> str:
    """
    Convert multiple embroidery elements to a grouped InkMCP command.

    Args:
        group_id: ID for the containing group
        elements: List of element specifications
        group_label: Optional label for the group

    Returns:
        InkMCP command string with nested children
    """
    children_parts = []
    for elem in elements:
        cmd = element_to_inkmcp_command(elem)
        # Convert to child syntax (remove tag, wrap in braces)
        parts = cmd.split(" ", 1)
        tag = parts[0]
        attrs = parts[1] if len(parts) > 1 else ""
        children_parts.append(f"{{{tag} {attrs}}}")

    children_str = ", ".join(children_parts)

    label_attr = f' inkscape:label="{group_label}"' if group_label else ""

    return f"g id={group_id}{label_attr} children=[{children_str}]"


# ══════════════════════════════════════════════════════════════════════════════
# HIGH-LEVEL EMBROIDERY OPERATIONS
# ══════════════════════════════════════════════════════════════════════════════


def create_embroidery_shape(
    shape_type: str,
    element_id: str,
    stitch_type: str,
    thread_color: str = "#000000",
    params: Optional[Dict[str, Any]] = None,
    **shape_params,
) -> Dict[str, Any]:
    """
    High-level function to create embroidered shapes.

    This is the main entry point for AI assistants to create embroidery elements.

    Args:
        shape_type: Type of shape ("rectangle", "circle", "ellipse", "path")
        element_id: Unique ID for the element
        stitch_type: Stitch type name (e.g., "fill", "satin", "running")
        thread_color: Thread color in hex
        params: Stitch parameters
        **shape_params: Shape-specific parameters (x, y, width, height, etc.)

    Returns:
        Result dictionary with element specification and InkMCP command
    """
    # Parse stitch type
    st = get_stitch_type(stitch_type)
    if st is None:
        return create_error_response(
            f"Unknown stitch type: {stitch_type}. "
            f"Valid types: {[s.value for s in StitchType]}"
        )

    # Generate path based on shape type
    try:
        if shape_type == "rectangle":
            x = float(shape_params.get("x", 0))
            y = float(shape_params.get("y", 0))
            width = float(shape_params.get("width", 100))
            height = float(shape_params.get("height", 100))
            path_d = create_rectangle_path(x, y, width, height)

        elif shape_type == "circle":
            cx = float(shape_params.get("cx", 50))
            cy = float(shape_params.get("cy", 50))
            r = float(shape_params.get("r", 50))
            path_d = create_circle_path(cx, cy, r)

        elif shape_type == "ellipse":
            cx = float(shape_params.get("cx", 50))
            cy = float(shape_params.get("cy", 50))
            rx = float(shape_params.get("rx", 50))
            ry = float(shape_params.get("ry", 30))
            path_d = create_ellipse_path(cx, cy, rx, ry)

        elif shape_type == "path":
            path_d = shape_params.get("d", "")
            if not path_d:
                return create_error_response("Path shape requires 'd' parameter")

        else:
            return create_error_response(
                f"Unknown shape type: {shape_type}. "
                f"Valid types: rectangle, circle, ellipse, path"
            )

    except (ValueError, KeyError) as e:
        return create_error_response(f"Invalid shape parameters: {e}")

    # Build element
    element = build_embroidery_element(
        element_id=element_id,
        path_d=path_d,
        stitch_type=st,
        thread_color=thread_color,
        params=params,
        label=shape_params.get("label"),
    )

    # Generate InkMCP command
    command = element_to_inkmcp_command(element)

    return create_success_response(
        f"Created {stitch_type} embroidery element: {element_id}",
        element=element,
        command=command,
        stitch_type=st.value,
        shape_type=shape_type,
    )


def list_available_stitch_types() -> Dict[str, Any]:
    """
    List all available stitch types with descriptions.

    Returns:
        Success response with stitch type information
    """
    from .stitch_types import list_all_stitch_types

    stitch_list = list_all_stitch_types()

    # Group by category
    by_category = {}
    for st in stitch_list:
        cat = st["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(st)

    return create_success_response(
        f"Found {len(stitch_list)} stitch types in {len(by_category)} categories",
        stitch_types=stitch_list,
        by_category=by_category,
        categories=list(by_category.keys()),
    )


def get_stitch_parameters(stitch_type_name: str) -> Dict[str, Any]:
    """
    Get available parameters for a stitch type.

    Args:
        stitch_type_name: Name of the stitch type

    Returns:
        Success response with parameter information
    """
    st = get_stitch_type(stitch_type_name)
    if st is None:
        return create_error_response(f"Unknown stitch type: {stitch_type_name}")

    info = get_stitch_info(st)

    # Get full parameter specs for supported params
    param_details = []
    for param_name in info.supported_params:
        if param_name in PARAM_SPECS:
            spec = PARAM_SPECS[param_name]
            param_details.append(
                {
                    "name": spec.name,
                    "display_name": spec.display_name,
                    "description": spec.description,
                    "type": spec.param_type.__name__,
                    "default": info.default_params.get(param_name, spec.default_value),
                    "min": spec.min_value,
                    "max": spec.max_value,
                    "unit": spec.unit,
                }
            )

    return create_success_response(
        f"Parameters for {info.display_name}",
        stitch_type=st.value,
        display_name=info.display_name,
        description=info.description,
        category=info.category.value,
        requires_fill=info.requires_fill,
        requires_stroke=info.requires_stroke,
        requires_satin_rails=info.requires_satin_rails,
        default_params=info.default_params,
        supported_params=param_details,
    )
