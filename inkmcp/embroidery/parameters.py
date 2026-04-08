"""
Ink/Stitch Parameters Module

Defines embroidery parameters, namespaces, and validation for Ink/Stitch integration.
Based on Ink/Stitch documentation: https://inkstitch.org/docs/params/
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

# ══════════════════════════════════════════════════════════════════════════════
# NAMESPACE DEFINITIONS
# ══════════════════════════════════════════════════════════════════════════════

# Ink/Stitch XML namespace
INKSTITCH_NAMESPACE = "http://inkstitch.org/namespace"

# Inkscape namespace (for labels and Inkscape-specific attributes)
INKSCAPE_NAMESPACE = "http://www.inkscape.org/namespaces/inkscape"

# SVG namespace
SVG_NAMESPACE = "http://www.w3.org/2000/svg"

# Common namespace prefixes for use in SVG files
INKSTITCH_NSMAP = {
    "inkstitch": INKSTITCH_NAMESPACE,
    "inkscape": INKSCAPE_NAMESPACE,
    "svg": SVG_NAMESPACE,
}


# ══════════════════════════════════════════════════════════════════════════════
# PARAMETER ENUMS
# ══════════════════════════════════════════════════════════════════════════════


class UnderlayType(Enum):
    """Types of underlay stitches for better embroidery coverage"""

    NONE = "none"
    CENTER_WALK = "center_walk"
    CONTOUR = "contour"
    ZIGZAG = "zigzag"


class SatinSplitMethod(Enum):
    """Methods for splitting long satin stitches"""

    SIMPLE = "simple"  # Basic split at midpoint
    RANDOM = "random"  # Random split positions
    STAGGER = "stagger"  # Staggered splits for natural look


class MeanderPattern(Enum):
    """Patterns for meander fill stitch"""

    SQUARE = "square"
    TRIANGLE = "triangle"
    CUBIC = "cubic"
    CROSS = "cross"


class LineCapType(Enum):
    """Line cap types for strokes"""

    BUTT = "butt"
    ROUND = "round"
    SQUARE = "square"


class LineJoinType(Enum):
    """Line join types for strokes"""

    MITER = "miter"
    ROUND = "round"
    BEVEL = "bevel"


# ══════════════════════════════════════════════════════════════════════════════
# PARAMETER DEFINITIONS
# ══════════════════════════════════════════════════════════════════════════════


@dataclass
class ParamSpec:
    """Specification for a single embroidery parameter"""

    name: str
    display_name: str
    description: str
    param_type: type  # int, float, bool, str
    default_value: Any
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    unit: str = ""  # mm, degrees, percent, etc.
    enum_values: Optional[List[str]] = None  # For enum-type params


# Complete parameter specifications for Ink/Stitch
PARAM_SPECS: Dict[str, ParamSpec] = {
    # ══════════════════════════════════════════════════════════════
    # RUNNING STITCH PARAMETERS
    # ══════════════════════════════════════════════════════════════
    "running_stitch_length_mm": ParamSpec(
        name="running_stitch_length_mm",
        display_name="Stitch Length",
        description="Length of each running stitch",
        param_type=float,
        default_value=2.5,
        min_value=0.5,
        max_value=10.0,
        unit="mm",
    ),
    "running_stitch_tolerance_mm": ParamSpec(
        name="running_stitch_tolerance_mm",
        display_name="Stitch Tolerance",
        description="How much to simplify the path",
        param_type=float,
        default_value=0.2,
        min_value=0.0,
        max_value=5.0,
        unit="mm",
    ),
    "repeats": ParamSpec(
        name="repeats",
        display_name="Repeats",
        description="Number of times to stitch the path",
        param_type=int,
        default_value=1,
        min_value=1,
        max_value=10,
    ),
    "bean_stitch_repeats": ParamSpec(
        name="bean_stitch_repeats",
        display_name="Bean Stitch Repeats",
        description="Number of back-and-forth passes (1=triple stitch)",
        param_type=int,
        default_value=1,
        min_value=0,
        max_value=5,
    ),
    # ══════════════════════════════════════════════════════════════
    # SATIN COLUMN PARAMETERS
    # ══════════════════════════════════════════════════════════════
    "zigzag_spacing_mm": ParamSpec(
        name="zigzag_spacing_mm",
        display_name="Zigzag Spacing",
        description="Distance between zigzag stitches",
        param_type=float,
        default_value=0.4,
        min_value=0.1,
        max_value=2.0,
        unit="mm",
    ),
    "pull_compensation_mm": ParamSpec(
        name="pull_compensation_mm",
        display_name="Pull Compensation",
        description="Extra width to compensate for thread pull",
        param_type=float,
        default_value=0.0,
        min_value=-1.0,
        max_value=2.0,
        unit="mm",
    ),
    "pull_compensation_percent": ParamSpec(
        name="pull_compensation_percent",
        display_name="Pull Compensation %",
        description="Extra width as percentage",
        param_type=int,
        default_value=0,
        min_value=-20,
        max_value=50,
        unit="%",
    ),
    "short_stitch_distance_mm": ParamSpec(
        name="short_stitch_distance_mm",
        display_name="Short Stitch Distance",
        description="Distance from edge for short stitches on curves",
        param_type=float,
        default_value=0.75,
        min_value=0.0,
        max_value=3.0,
        unit="mm",
    ),
    "short_stitch_inset": ParamSpec(
        name="short_stitch_inset",
        display_name="Short Stitch Inset",
        description="How far short stitches are inset",
        param_type=float,
        default_value=15.0,
        min_value=0.0,
        max_value=50.0,
        unit="%",
    ),
    "random_width_decrease_percent": ParamSpec(
        name="random_width_decrease_percent",
        display_name="Random Width Decrease",
        description="Maximum random width decrease",
        param_type=int,
        default_value=0,
        min_value=0,
        max_value=50,
        unit="%",
    ),
    "random_width_increase_percent": ParamSpec(
        name="random_width_increase_percent",
        display_name="Random Width Increase",
        description="Maximum random width increase",
        param_type=int,
        default_value=0,
        min_value=0,
        max_value=50,
        unit="%",
    ),
    "random_zigzag_spacing_percent": ParamSpec(
        name="random_zigzag_spacing_percent",
        display_name="Random Spacing",
        description="Randomize zigzag spacing",
        param_type=int,
        default_value=0,
        min_value=0,
        max_value=100,
        unit="%",
    ),
    "split_method": ParamSpec(
        name="split_method",
        display_name="Split Method",
        description="How to split long stitches",
        param_type=str,
        default_value="simple",
        enum_values=["simple", "random", "stagger"],
    ),
    "min_random_split_length_mm": ParamSpec(
        name="min_random_split_length_mm",
        display_name="Min Split Length",
        description="Minimum stitch length for random splits",
        param_type=float,
        default_value=1.5,
        min_value=0.5,
        max_value=5.0,
        unit="mm",
    ),
    "random_split_jitter_percent": ParamSpec(
        name="random_split_jitter_percent",
        display_name="Split Jitter",
        description="Random variation in split position",
        param_type=int,
        default_value=0,
        min_value=0,
        max_value=100,
        unit="%",
    ),
    # ══════════════════════════════════════════════════════════════
    # UNDERLAY PARAMETERS
    # ══════════════════════════════════════════════════════════════
    "center_walk_underlay": ParamSpec(
        name="center_walk_underlay",
        display_name="Center Walk Underlay",
        description="Add center-line underlay for stability",
        param_type=bool,
        default_value=False,
    ),
    "center_walk_underlay_stitch_length_mm": ParamSpec(
        name="center_walk_underlay_stitch_length_mm",
        display_name="Center Walk Length",
        description="Stitch length for center walk underlay",
        param_type=float,
        default_value=2.0,
        min_value=0.5,
        max_value=5.0,
        unit="mm",
    ),
    "contour_underlay": ParamSpec(
        name="contour_underlay",
        display_name="Contour Underlay",
        description="Add contour underlay along edges",
        param_type=bool,
        default_value=False,
    ),
    "contour_underlay_stitch_length_mm": ParamSpec(
        name="contour_underlay_stitch_length_mm",
        display_name="Contour Length",
        description="Stitch length for contour underlay",
        param_type=float,
        default_value=2.0,
        min_value=0.5,
        max_value=5.0,
        unit="mm",
    ),
    "contour_underlay_inset_mm": ParamSpec(
        name="contour_underlay_inset_mm",
        display_name="Contour Inset",
        description="How far inside edge for contour underlay",
        param_type=float,
        default_value=0.4,
        min_value=0.0,
        max_value=2.0,
        unit="mm",
    ),
    "contour_underlay_inset_percent": ParamSpec(
        name="contour_underlay_inset_percent",
        display_name="Contour Inset %",
        description="Contour inset as percentage of width",
        param_type=int,
        default_value=0,
        min_value=0,
        max_value=50,
        unit="%",
    ),
    "zigzag_underlay": ParamSpec(
        name="zigzag_underlay",
        display_name="Zigzag Underlay",
        description="Add zigzag underlay for density",
        param_type=bool,
        default_value=False,
    ),
    "zigzag_underlay_spacing_mm": ParamSpec(
        name="zigzag_underlay_spacing_mm",
        display_name="Zigzag Underlay Spacing",
        description="Spacing for zigzag underlay",
        param_type=float,
        default_value=1.0,
        min_value=0.3,
        max_value=3.0,
        unit="mm",
    ),
    "zigzag_underlay_inset_mm": ParamSpec(
        name="zigzag_underlay_inset_mm",
        display_name="Zigzag Underlay Inset",
        description="Inset for zigzag underlay",
        param_type=float,
        default_value=0.4,
        min_value=0.0,
        max_value=2.0,
        unit="mm",
    ),
    "zigzag_underlay_inset_percent": ParamSpec(
        name="zigzag_underlay_inset_percent",
        display_name="Zigzag Underlay Inset %",
        description="Zigzag underlay inset as percentage",
        param_type=int,
        default_value=0,
        min_value=0,
        max_value=50,
        unit="%",
    ),
    # ══════════════════════════════════════════════════════════════
    # FILL PARAMETERS
    # ══════════════════════════════════════════════════════════════
    "fill_angle": ParamSpec(
        name="fill_angle",
        display_name="Fill Angle",
        description="Angle of fill stitch rows",
        param_type=float,
        default_value=0.0,
        min_value=-180.0,
        max_value=180.0,
        unit="°",
    ),
    "row_spacing_mm": ParamSpec(
        name="row_spacing_mm",
        display_name="Row Spacing",
        description="Distance between fill rows",
        param_type=float,
        default_value=0.25,
        min_value=0.1,
        max_value=2.0,
        unit="mm",
    ),
    "stagger_rows": ParamSpec(
        name="stagger_rows",
        display_name="Stagger Rows",
        description="Number of rows before pattern repeats",
        param_type=int,
        default_value=4,
        min_value=1,
        max_value=16,
    ),
    "max_stitch_length_mm": ParamSpec(
        name="max_stitch_length_mm",
        display_name="Max Stitch Length",
        description="Maximum length of a single stitch",
        param_type=float,
        default_value=3.0,
        min_value=1.0,
        max_value=12.7,  # Half inch max for most machines
        unit="mm",
    ),
    "fill_underlay": ParamSpec(
        name="fill_underlay",
        display_name="Fill Underlay",
        description="Add underlay beneath fill",
        param_type=bool,
        default_value=False,
    ),
    "fill_underlay_angle": ParamSpec(
        name="fill_underlay_angle",
        display_name="Underlay Angle",
        description="Angle for fill underlay (usually perpendicular to fill)",
        param_type=float,
        default_value=90.0,
        min_value=-180.0,
        max_value=180.0,
        unit="°",
    ),
    "fill_underlay_row_spacing_mm": ParamSpec(
        name="fill_underlay_row_spacing_mm",
        display_name="Underlay Row Spacing",
        description="Row spacing for underlay (usually larger)",
        param_type=float,
        default_value=0.5,
        min_value=0.2,
        max_value=3.0,
        unit="mm",
    ),
    "fill_underlay_max_stitch_length_mm": ParamSpec(
        name="fill_underlay_max_stitch_length_mm",
        display_name="Underlay Max Stitch",
        description="Max stitch length for underlay",
        param_type=float,
        default_value=6.0,
        min_value=1.0,
        max_value=12.7,
        unit="mm",
    ),
    "fill_underlay_inset_mm": ParamSpec(
        name="fill_underlay_inset_mm",
        display_name="Underlay Inset",
        description="How far inside shape edge for underlay",
        param_type=float,
        default_value=0.3,
        min_value=0.0,
        max_value=2.0,
        unit="mm",
    ),
    "fill_underlay_skip_last": ParamSpec(
        name="fill_underlay_skip_last",
        display_name="Skip Last Underlay",
        description="Skip underlay on last row",
        param_type=bool,
        default_value=True,
    ),
    "expand_mm": ParamSpec(
        name="expand_mm",
        display_name="Expand/Contract",
        description="Expand (positive) or contract (negative) shape",
        param_type=float,
        default_value=0.0,
        min_value=-5.0,
        max_value=5.0,
        unit="mm",
    ),
    "underpath": ParamSpec(
        name="underpath",
        display_name="Underpath",
        description="Allow traveling under filled areas",
        param_type=bool,
        default_value=True,
    ),
    "underpath_length_mm": ParamSpec(
        name="underpath_length_mm",
        display_name="Underpath Length",
        description="Max length for underpath stitches",
        param_type=float,
        default_value=12.0,
        min_value=1.0,
        max_value=50.0,
        unit="mm",
    ),
    "staggers": ParamSpec(
        name="staggers",
        display_name="Staggers",
        description="Alternative to stagger_rows for auto-fill",
        param_type=int,
        default_value=4,
        min_value=1,
        max_value=16,
    ),
    # ══════════════════════════════════════════════════════════════
    # RIPPLE PARAMETERS
    # ══════════════════════════════════════════════════════════════
    "line_count": ParamSpec(
        name="line_count",
        display_name="Line Count",
        description="Number of ripple lines",
        param_type=int,
        default_value=10,
        min_value=2,
        max_value=100,
    ),
    "skip_start": ParamSpec(
        name="skip_start",
        display_name="Skip Start",
        description="Lines to skip at start",
        param_type=int,
        default_value=0,
        min_value=0,
        max_value=50,
    ),
    "skip_end": ParamSpec(
        name="skip_end",
        display_name="Skip End",
        description="Lines to skip at end",
        param_type=int,
        default_value=0,
        min_value=0,
        max_value=50,
    ),
    "exponent": ParamSpec(
        name="exponent",
        display_name="Exponent",
        description="Controls ripple spacing distribution",
        param_type=float,
        default_value=1.0,
        min_value=0.1,
        max_value=5.0,
    ),
    "flip_exponent": ParamSpec(
        name="flip_exponent",
        display_name="Flip Exponent",
        description="Reverse exponent effect direction",
        param_type=bool,
        default_value=False,
    ),
    "reverse": ParamSpec(
        name="reverse",
        display_name="Reverse",
        description="Reverse ripple direction",
        param_type=bool,
        default_value=False,
    ),
    # ══════════════════════════════════════════════════════════════
    # CONTOUR FILL PARAMETERS
    # ══════════════════════════════════════════════════════════════
    "clockwise": ParamSpec(
        name="clockwise",
        display_name="Clockwise",
        description="Stitch in clockwise direction",
        param_type=bool,
        default_value=True,
    ),
    # ══════════════════════════════════════════════════════════════
    # MEANDER FILL PARAMETERS
    # ══════════════════════════════════════════════════════════════
    "meander_pattern": ParamSpec(
        name="meander_pattern",
        display_name="Meander Pattern",
        description="Pattern type for meander fill",
        param_type=str,
        default_value="square",
        enum_values=["square", "triangle", "cubic", "cross"],
    ),
    "meander_scale_percent": ParamSpec(
        name="meander_scale_percent",
        display_name="Meander Scale",
        description="Scale of meander pattern",
        param_type=int,
        default_value=100,
        min_value=10,
        max_value=500,
        unit="%",
    ),
    # ══════════════════════════════════════════════════════════════
    # GRADIENT FILL PARAMETERS
    # ══════════════════════════════════════════════════════════════
    "gradient_start_percent": ParamSpec(
        name="gradient_start_percent",
        display_name="Gradient Start",
        description="Density at gradient start",
        param_type=int,
        default_value=0,
        min_value=0,
        max_value=100,
        unit="%",
    ),
    "gradient_end_percent": ParamSpec(
        name="gradient_end_percent",
        display_name="Gradient End",
        description="Density at gradient end",
        param_type=int,
        default_value=100,
        min_value=0,
        max_value=100,
        unit="%",
    ),
    # ══════════════════════════════════════════════════════════════
    # TARTAN FILL PARAMETERS
    # ══════════════════════════════════════════════════════════════
    "tartan_angle": ParamSpec(
        name="tartan_angle",
        display_name="Tartan Angle",
        description="Angle for tartan pattern",
        param_type=float,
        default_value=45.0,
        min_value=0.0,
        max_value=90.0,
        unit="°",
    ),
    # ══════════════════════════════════════════════════════════════
    # CROSS STITCH PARAMETERS
    # ══════════════════════════════════════════════════════════════
    "cross_stitch_size_mm": ParamSpec(
        name="cross_stitch_size_mm",
        display_name="Cross Size",
        description="Size of each cross stitch",
        param_type=float,
        default_value=2.0,
        min_value=0.5,
        max_value=10.0,
        unit="mm",
    ),
    # ══════════════════════════════════════════════════════════════
    # MACHINE/OUTPUT PARAMETERS
    # ══════════════════════════════════════════════════════════════
    "trim_after": ParamSpec(
        name="trim_after",
        display_name="Trim After",
        description="Add trim command after this element",
        param_type=bool,
        default_value=False,
    ),
    "stop_after": ParamSpec(
        name="stop_after",
        display_name="Stop After",
        description="Add stop/color change after this element",
        param_type=bool,
        default_value=False,
    ),
    "force_lock_stitches": ParamSpec(
        name="force_lock_stitches",
        display_name="Force Lock Stitches",
        description="Force lock stitches at start and end",
        param_type=bool,
        default_value=False,
    ),
}


@dataclass
class EmbroideryParams:
    """
    Container for embroidery parameters with validation.

    Use this class to build and validate parameter sets for stitch types.
    """

    params: Dict[str, Any] = field(default_factory=dict)

    def set(self, name: str, value: Any) -> "EmbroideryParams":
        """
        Set a parameter value with validation.

        Args:
            name: Parameter name
            value: Parameter value

        Returns:
            Self for chaining

        Raises:
            ValueError: If parameter is invalid
        """
        if name not in PARAM_SPECS:
            raise ValueError(f"Unknown parameter: {name}")

        spec = PARAM_SPECS[name]
        validated_value = self._validate_value(spec, value)
        self.params[name] = validated_value
        return self

    def _validate_value(self, spec: ParamSpec, value: Any) -> Any:
        """Validate and convert a parameter value"""
        # Type conversion
        try:
            if spec.param_type == bool:
                if isinstance(value, str):
                    value = value.lower() in ("true", "1", "yes", "on")
                else:
                    value = bool(value)
            elif spec.param_type == int:
                value = int(float(value))
            elif spec.param_type == float:
                value = float(value)
            elif spec.param_type == str:
                value = str(value)
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Cannot convert '{value}' to {spec.param_type.__name__} "
                f"for parameter '{spec.name}'"
            ) from e

        # Range validation for numeric types
        if spec.param_type in (int, float):
            if spec.min_value is not None and value < spec.min_value:
                raise ValueError(
                    f"Parameter '{spec.name}' value {value} is below minimum {spec.min_value}"
                )
            if spec.max_value is not None and value > spec.max_value:
                raise ValueError(
                    f"Parameter '{spec.name}' value {value} is above maximum {spec.max_value}"
                )

        # Enum validation
        if spec.enum_values is not None and value not in spec.enum_values:
            raise ValueError(
                f"Parameter '{spec.name}' value '{value}' must be one of: {spec.enum_values}"
            )

        return value

    def get(self, name: str, default: Any = None) -> Any:
        """Get a parameter value"""
        return self.params.get(name, default)

    def to_dict(self) -> Dict[str, Any]:
        """Get all parameters as a dictionary"""
        return dict(self.params)

    def to_svg_attrs(self) -> Dict[str, str]:
        """
        Convert parameters to SVG attribute format with Ink/Stitch namespace.

        Returns:
            Dictionary of namespaced attribute names to string values
        """
        attrs = {}
        for name, value in self.params.items():
            # Convert booleans to lowercase strings
            if isinstance(value, bool):
                value = "true" if value else "false"

            # Use Ink/Stitch namespace prefix
            attr_name = f"{{{INKSTITCH_NAMESPACE}}}{name}"
            attrs[attr_name] = str(value)

        return attrs


def get_default_params(param_names: List[str]) -> Dict[str, Any]:
    """
    Get default values for a list of parameters.

    Args:
        param_names: List of parameter names

    Returns:
        Dictionary of parameter names to default values
    """
    return {
        name: PARAM_SPECS[name].default_value
        for name in param_names
        if name in PARAM_SPECS
    }


def validate_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate a dictionary of parameters.

    Args:
        params: Dictionary of parameter names to values

    Returns:
        Dictionary with validated and type-converted values

    Raises:
        ValueError: If any parameter is invalid
    """
    ep = EmbroideryParams()
    for name, value in params.items():
        ep.set(name, value)
    return ep.to_dict()


def get_param_info(name: str) -> Optional[ParamSpec]:
    """
    Get information about a parameter.

    Args:
        name: Parameter name

    Returns:
        ParamSpec or None if not found
    """
    return PARAM_SPECS.get(name)


def list_all_params() -> List[Dict[str, Any]]:
    """
    Get a summary of all available parameters.

    Returns:
        List of dicts with parameter information for display
    """
    return [
        {
            "name": spec.name,
            "display_name": spec.display_name,
            "description": spec.description,
            "type": spec.param_type.__name__,
            "default": spec.default_value,
            "unit": spec.unit,
            "min": spec.min_value,
            "max": spec.max_value,
            "enum_values": spec.enum_values,
        }
        for spec in PARAM_SPECS.values()
    ]
