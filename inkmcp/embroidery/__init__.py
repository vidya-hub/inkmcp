# Ink/Stitch Embroidery Integration Module
"""
This module provides embroidery-specific functionality for InkMCP,
enabling AI-assisted embroidery design creation through Ink/Stitch.

Submodules:
- stitch_types: Stitch type definitions and mappings
- parameters: Ink/Stitch parameter specifications
- embroidery_operations: Core embroidery element creation
- export: Embroidery format export handlers
- presets: Pre-configured stitch templates
"""

from .stitch_types import (
    StitchType,
    StitchCategory,
    STITCH_TYPES,
    get_stitch_type,
    get_stitch_info,
    get_stitch_attributes,
    list_all_stitch_types,
)
from .parameters import (
    INKSTITCH_NAMESPACE,
    INKSTITCH_NSMAP,
    EmbroideryParams,
    UnderlayType,
    get_default_params,
    validate_params,
    get_param_info,
)
from .embroidery_operations import (
    create_embroidery_shape,
    build_embroidery_element,
    list_available_stitch_types,
    get_stitch_parameters,
)
from .export import (
    EmbroideryFormat,
    export_embroidery,
    list_export_formats,
    check_inkstitch_installation,
    get_format_info,
    generate_stitch_simulation,
)
from .presets import (
    PresetCategory,
    EmbroideryPreset,
    ALL_PRESETS,
    list_presets,
    get_preset,
    create_from_preset,
    create_patch_design,
    create_applique_sequence,
    get_machine_optimized_params,
)

__all__ = [
    # Stitch types
    "StitchType",
    "StitchCategory",
    "STITCH_TYPES",
    "get_stitch_type",
    "get_stitch_info",
    "get_stitch_attributes",
    "list_all_stitch_types",
    # Parameters
    "INKSTITCH_NAMESPACE",
    "INKSTITCH_NSMAP",
    "EmbroideryParams",
    "UnderlayType",
    "get_default_params",
    "validate_params",
    "get_param_info",
    # Operations
    "create_embroidery_shape",
    "build_embroidery_element",
    "list_available_stitch_types",
    "get_stitch_parameters",
    # Export
    "EmbroideryFormat",
    "export_embroidery",
    "list_export_formats",
    "check_inkstitch_installation",
    "get_format_info",
    "generate_stitch_simulation",
    # Presets
    "PresetCategory",
    "EmbroideryPreset",
    "ALL_PRESETS",
    "list_presets",
    "get_preset",
    "create_from_preset",
    "create_patch_design",
    "create_applique_sequence",
    "get_machine_optimized_params",
]
