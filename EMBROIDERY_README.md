# InkMCP Embroidery Integration

AI-assisted embroidery design creation through Ink/Stitch integration.

## Overview

This module extends InkMCP with embroidery-specific functionality, enabling AI assistants to create machine-ready embroidery designs through natural language commands. The integration leverages [Ink/Stitch](https://inkstitch.org), the powerful open-source embroidery extension for Inkscape.

## Quick Start

### 1. Prerequisites

**Required Software:**
- **Inkscape** (1.2+): https://inkscape.org/release/
- **Ink/Stitch**: https://inkstitch.org/docs/install/

**Verify Installation:**
```
# Use the MCP tool to check setup
embroidery_check_setup
```

### 2. Create Your First Embroidery Element

```python
# Create a filled rectangle with auto-fill stitches
embroidery_create_element(
    shape_type="rectangle",
    element_id="my_patch",
    stitch_type="auto_fill",
    thread_color="#FF0000",
    x=100, y=100,
    width=200, height=150
)
```

### 3. Export to Machine Format

```python
# Export to DST (Tajima - most universal commercial format)
embroidery_export(
    svg_path="/path/to/design.svg",
    output_path="/path/to/output.dst",
    format="dst"
)
```

## MCP Tools Reference

### Element Creation

#### `embroidery_create_element`
Create embroidery elements with Ink/Stitch parameters.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `shape_type` | str | "rectangle", "circle", "ellipse", or "path" |
| `element_id` | str | Unique ID for the element |
| `stitch_type` | str | Stitch type (see Stitch Types below) |
| `thread_color` | str | Hex color code (e.g., "#FF0000") |
| `x`, `y` | float | Position coordinates |
| `width`, `height` | float | Size for rectangles |
| `cx`, `cy`, `r` | float | Center and radius for circles |
| `stitch_length` | float | Length of each stitch in mm |
| `fill_angle` | float | Angle of fill stitches in degrees |
| `row_spacing` | float | Spacing between fill rows in mm |
| `underlay` | bool | Add underlay stitches for stability |

### Stitch Information

#### `embroidery_list_stitches`
List all available stitch types with descriptions.

```python
embroidery_list_stitches()  # All stitches
embroidery_list_stitches(category="fill")  # Fill stitches only
```

#### `embroidery_get_stitch_params`
Get detailed parameters for a specific stitch type.

```python
embroidery_get_stitch_params(stitch_type="satin_column")
```

### Export & Preview

#### `embroidery_export`
Export SVG to machine-readable embroidery format.

```python
embroidery_export(
    svg_path="/path/to/design.svg",
    output_path="/path/to/output.pes",
    format="pes"
)
```

#### `embroidery_list_formats`
List all supported embroidery formats.

#### `embroidery_simulate`
Generate a stitch simulation preview.

```python
embroidery_simulate(
    svg_path="/path/to/design.svg",
    output_path="/path/to/preview.svg",
    realistic=True
)
```

### Setup & Diagnostics

#### `embroidery_check_setup`
Verify Ink/Stitch installation status.

#### `embroidery_format_info`
Get detailed information about a specific format.

```python
embroidery_format_info(format="pes")
```

## Stitch Types

### Fill Stitches (Area Coverage)

| Stitch Type | Description | Best For |
|-------------|-------------|----------|
| `fill` | Basic fill stitch | Simple areas |
| `auto_fill` | Intelligent auto-fill | Most fill areas |
| `contour_fill` | Concentric contours | Circular designs |
| `guided_fill` | Custom path-guided | Complex shapes |
| `meander_fill` | Stipple/quilting | Background texture |
| `circular_fill` | Spiral from center | Radial designs |
| `linear_gradient_fill` | Density gradient | Shading effects |
| `tartan_fill` | Plaid pattern | Decorative fills |

### Stroke Stitches (Lines & Outlines)

| Stitch Type | Description | Best For |
|-------------|-------------|----------|
| `running_stitch` | Basic line | Outlines, quilting |
| `bean_stitch` | Triple reinforced | Bold outlines |
| `manual_stitch` | Point-to-point | Custom paths |
| `ripple_stitch` | Wavy lines | Decorative |
| `zigzag_stitch` | Zigzag pattern | Edges, applique |

### Satin Stitches (Smooth Columns)

| Stitch Type | Description | Best For |
|-------------|-------------|----------|
| `satin_column` | Two-rail satin | Borders, lettering |
| `e_stitch` | E-pattern satin | Wide satin |
| `s_stitch` | S-pattern satin | Very wide satin |
| `zigzag_satin` | Zigzag satin | Decorative borders |

## Export Formats

### Popular Formats

| Format | Extension | Manufacturer | Use Case |
|--------|-----------|--------------|----------|
| `dst` | .dst | Tajima | Commercial machines |
| `pes` | .pes | Brother | Home machines |
| `jef` | .jef | Janome | Janome machines |
| `exp` | .exp | Melco | Commercial |
| `vp3` | .vp3 | Pfaff | Pfaff machines |
| `hus` | .hus | Husqvarna | Viking machines |

### All Supported Formats

DST, PES, PEC, JEF, EXP, VP3, HUS, VIP, SHV, XXX, T01, ART, CSV, JSON, SVG (simulation), PNG (preview)

## Presets

Pre-configured templates for common designs:

### Basic Shapes
- `filled_rectangle` - Solid filled rectangle
- `filled_circle` - Filled circle
- `running_outline` - Running stitch outline
- `bean_outline` - Bold bean stitch outline

### Borders
- `satin_border` - Smooth satin column border
- `zigzag_border` - Decorative zigzag border
- `ripple_border` - Wavy ripple border

### Patches & Badges
- `simple_patch` - Basic patch with fill
- `circular_badge` - Round badge design
- `oval_badge` - Oval/elliptical badge

### Quilting
- `meander_fill` - Stipple/free-motion fill
- `circular_fill` - Concentric circular fill
- `linear_gradient` - Gradient density fill

### Applique
- `applique_placement` - Placement line
- `applique_tack` - Tack down stitches
- `applique_border` - Satin border finish

## Parameter Reference

### Common Fill Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `fill_angle` | Stitch direction (degrees) | 0 | 0-360 |
| `row_spacing` | Space between rows (mm) | 0.25 | 0.1-3.0 |
| `stitch_length` | Stitch length (mm) | 2.5 | 0.5-10.0 |
| `fill_underlay` | Add underlay | true | true/false |
| `fill_underlay_angle` | Underlay angle | 90 | 0-360 |

### Common Stroke Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `stitch_length` | Stitch length (mm) | 2.5 | 0.5-10.0 |
| `bean_stitch_repeats` | Stitch repetitions | 1 | 1-10 |
| `running_stitch_tolerance` | Curve tolerance | 0.2 | 0.1-1.0 |

### Satin Column Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `satin_column_width` | Column width (mm) | 3.0 | 0.5-12.0 |
| `zigzag_spacing` | Stitch spacing (mm) | 0.4 | 0.1-1.0 |
| `pull_compensation` | Fabric pull adjustment | 0.3 | 0-2.0 |
| `center_walk_underlay` | Center underlay | true | true/false |
| `contour_underlay` | Edge underlay | false | true/false |

## Best Practices

### Design Guidelines

1. **Always specify element IDs** - Enables later modification
2. **Use underlay** - Improves stitch quality and prevents puckering
3. **Choose appropriate stitch types**:
   - Large areas → `auto_fill`
   - Borders/lettering → `satin_column`
   - Outlines → `running_stitch` or `bean_stitch`

### Stitch Quality Tips

1. **Fill Direction**: Vary fill angle between adjacent areas to reduce stretching
2. **Underlay**: Always use for fills larger than 1cm²
3. **Pull Compensation**: Increase for stretchy fabrics
4. **Satin Width**: Keep between 2-5mm for best quality

### Machine-Specific Settings

| Machine Type | Stitch Length | Row Spacing | Pull Comp |
|--------------|---------------|-------------|-----------|
| Home | 2.5mm | 0.30mm | 0.2mm |
| Commercial | 3.0mm | 0.25mm | 0.3mm |
| Industrial | 3.5mm | 0.20mm | 0.4mm |

## Workflow Example

### Creating a Complete Patch

```python
# 1. Create the fill
embroidery_create_element(
    shape_type="rectangle",
    element_id="patch_fill",
    stitch_type="auto_fill",
    thread_color="#FF0000",
    x=100, y=100,
    width=80, height=50,
    fill_angle=45,
    underlay=True
)

# 2. Add a satin border (requires manual satin path creation in Inkscape)
# Or use bean stitch for quick outline:
embroidery_create_element(
    shape_type="rectangle",
    element_id="patch_border",
    stitch_type="bean_stitch",
    thread_color="#000000",
    x=100, y=100,
    width=80, height=50,
    stitch_length=2.5
)

# 3. Export to machine format
embroidery_export(
    svg_path="/path/to/patch.svg",
    output_path="/path/to/patch.pes",
    format="pes"
)
```

## Troubleshooting

### Common Issues

**"Ink/Stitch not found"**
- Install Ink/Stitch from https://inkstitch.org/docs/install/
- Restart Inkscape after installation
- Run `embroidery_check_setup` to verify

**"Export failed"**
- Ensure SVG has Ink/Stitch embroidery attributes
- Check that design fits within format size limits
- Verify Inkscape is accessible from command line

**"Stitches look wrong in simulation"**
- Check stitch type matches your path type (stroke vs fill)
- Verify parameters are within valid ranges
- Satin columns require two-rail paths

### Getting Help

- **Ink/Stitch Documentation**: https://inkstitch.org/docs/
- **InkMCP Issues**: https://github.com/Shriinivas/inkmcp/issues
- **Embroidery Forums**: https://inkstitch.org/community/

## Architecture

```
inkmcp/embroidery/
├── __init__.py           # Package exports
├── stitch_types.py       # Stitch type definitions (18 types)
├── parameters.py         # Parameter specifications (60+ params)
├── embroidery_operations.py  # Core element creation
├── export.py             # Format export handlers
└── presets.py            # Pre-configured templates
```

## License

Same as InkMCP - see main repository LICENSE file.
