#!/usr/bin/env python3
"""
Inkscape MCP Server
Model Context Protocol server for controlling Inkscape via D-Bus extension

Provides access to Inkscape operations through a unified tool interface
for SVG element creation, document manipulation, and code execution.

Also includes embroidery-specific tools for AI-assisted embroidery design
creation through Ink/Stitch integration.

Supports multiple transport modes:
- stdio: Standard input/output (default, for local MCP clients)
- http: HTTP transport with Streamable HTTP (recommended for remote)
- sse: Server-Sent Events (legacy, for backward compatibility)

Usage:
    # Default stdio mode
    python inkscape_mcp_server.py

    # HTTP mode on default port 8000
    python inkscape_mcp_server.py --transport http

    # HTTP mode on custom host/port
    python inkscape_mcp_server.py --transport http --host 0.0.0.0 --port 9000

    # SSE mode (legacy)
    python inkscape_mcp_server.py --transport sse --port 8000
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Literal, Optional, Union

from mcp.server.fastmcp import FastMCP, Context
from mcp.types import ImageContent

# Import embroidery modules
from embroidery.embroidery_operations import (
    create_embroidery_shape,
    list_available_stitch_types,
    get_stitch_parameters,
)
from embroidery.export import (
    export_embroidery,
    list_export_formats,
    check_inkstitch_installation,
    get_format_info,
    generate_stitch_simulation,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("InkscapeMCP")

# Server configuration
DEFAULT_DBUS_SERVICE = "org.inkscape.Inkscape"
DEFAULT_DBUS_PATH = "/org/inkscape/Inkscape"
DEFAULT_DBUS_INTERFACE = "org.gtk.Actions"
DEFAULT_ACTION_NAME = "org.khema.inkscape.mcp"


class InkscapeConnection:
    """Manages D-Bus connection to Inkscape"""

    def __init__(self):
        self.dbus_service = DEFAULT_DBUS_SERVICE
        self.dbus_path = DEFAULT_DBUS_PATH
        self.dbus_interface = DEFAULT_DBUS_INTERFACE
        self.action_name = DEFAULT_ACTION_NAME
        self._client_path = Path(__file__).parent / "inkmcpcli.py"

    def is_available(self) -> bool:
        """Check if Inkscape is running and MCP extension is available"""
        try:
            cmd = [
                "gdbus",
                "call",
                "--session",
                "--dest",
                self.dbus_service,
                "--object-path",
                self.dbus_path,
                "--method",
                f"{self.dbus_interface}.List",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

            if result.returncode != 0:
                logger.warning("Inkscape D-Bus service not available")
                return False

            # Check if our generic MCP extension action is listed
            output = result.stdout
            return self.action_name in output

        except Exception as e:
            logger.error(f"Error checking Inkscape availability: {e}")
            return False

    def execute_operation(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute operation using CLI client"""
        try:
            # Write operation data to temporary file
            params_file = os.path.join(tempfile.gettempdir(), "mcp_params.json")

            with open(params_file, "w") as f:
                json.dump(operation_data, f)

            # Execute via D-Bus
            cmd = [
                "gdbus",
                "call",
                "--session",
                "--dest",
                self.dbus_service,
                "--object-path",
                self.dbus_path,
                "--method",
                f"{self.dbus_interface}.Activate",
                self.action_name,
                "[]",
                "{}",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                logger.error(f"D-Bus command failed: {result.stderr}")
                return {
                    "status": "error",
                    "data": {"error": f"D-Bus call failed: {result.stderr}"},
                }

            # Read response from response file
            response_file = operation_data.get("response_file")
            if response_file and os.path.exists(response_file):
                try:
                    with open(response_file, "r") as f:
                        response_data = json.load(f)
                    os.remove(response_file)  # Clean up
                    return response_data
                except Exception as e:
                    logger.error(f"Failed to read response file: {e}")
                    return {
                        "status": "error",
                        "data": {"error": f"Response file error: {e}"},
                    }
            else:
                # Assume success if no response file specified
                return {"status": "success", "data": {"message": "Operation completed"}}

        except subprocess.TimeoutExpired:
            logger.error("Operation timed out")
            return {"status": "error", "data": {"error": "Operation timed out"}}
        except Exception as e:
            logger.error(f"Operation execution error: {e}")
            return {"status": "error", "data": {"error": str(e)}}


# Global connection instance
_inkscape_connection: Optional[InkscapeConnection] = None


def get_inkscape_connection() -> InkscapeConnection:
    """Get or create Inkscape connection"""
    global _inkscape_connection

    if _inkscape_connection is None:
        _inkscape_connection = InkscapeConnection()

    if not _inkscape_connection.is_available():
        raise Exception(
            "Inkscape is not running or generic MCP extension is not available. "
            "Please start Inkscape and ensure the generic MCP extension is installed."
        )

    return _inkscape_connection


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage server startup and shutdown lifecycle"""
    logger.info("Inkscape MCP server starting up")

    try:
        # Test connection on startup
        try:
            get_inkscape_connection()
            logger.info("Successfully connected to Inkscape on startup")
        except Exception as e:
            logger.warning(f"Could not connect to Inkscape on startup: {e}")
            logger.warning(
                "Make sure Inkscape is running with the generic MCP extension before using tools"
            )

        yield {}
    finally:
        logger.info("Inkscape MCP server shut down")


# Create the MCP server
mcp = FastMCP("InkscapeMCP", lifespan=server_lifespan)


def format_response(result: Dict[str, Any]) -> str:
    """Format operation result for clean AI client display"""
    if result.get("status") == "success":
        data = result.get("data", {})
        message = data.get("message", "Operation completed successfully")

        # Add relevant details based on operation type
        details = []

        # Element creation details
        if "id" in data:
            details.append(f"**ID**: `{data['id']}`")
        if "tag" in data:
            details.append(f"**Type**: {data['tag']}")

        # Selection/info details
        if "count" in data:
            details.append(f"**Count**: {data['count']}")
        if "elements" in data:
            elements = data["elements"]
            if elements:
                details.append(f"**Elements**: {len(elements)} items")
                # Show first few elements
                for i, elem in enumerate(elements[:3]):
                    elem_desc = (
                        f"{elem.get('tag', 'unknown')} ({elem.get('id', 'no-id')})"
                    )
                    details.append(f"  {i + 1}. {elem_desc}")
                if len(elements) > 3:
                    details.append(f"  ... and {len(elements) - 3} more")

        # Export details
        if "export_path" in data:
            details.append(f"**File**: {data['export_path']}")
        if "file_size" in data:
            details.append(f"**Size**: {data['file_size']} bytes")

        # Code execution details
        if "execution_successful" in data:
            if data["execution_successful"]:
                details.append("**Execution**: ✅ Success")
            else:
                details.append("**Execution**: ❌ Failed")
        if "elements_created" in data and data["elements_created"]:
            details.append(f"**Created**: {len(data['elements_created'])} elements")

        # ID mapping (requested → actual)
        if "id_mapping" in data and data["id_mapping"]:
            details.append("**Element IDs** (requested → actual):")
            for requested_id, actual_id in data["id_mapping"].items():
                if requested_id == actual_id:
                    details.append(f"  {requested_id} ✓")
                else:
                    details.append(
                        f"  {requested_id} → {actual_id} (collision resolved)"
                    )

        # Warning for missing IDs
        if "generated_ids" in data and data["generated_ids"]:
            details.append("⚠️  **WARNING: Elements created without IDs**")
            details.append(
                "For better scene management, always specify 'id' for elements:"
            )
            for gen_id in data["generated_ids"]:
                # Extract element type from generated ID (e.g., "circle2863" → "circle")
                elem_type = "".join(c for c in gen_id if c.isalpha())
                details.append(f"  {gen_id} (use: {elem_type} id=my_name ...)")
            details.append(
                "This enables later modification with execute-code commands."
            )

        # Build final response with appropriate emoji
        # Check if this is a failed code execution
        is_code_failure = (
            "execution_successful" in data and not data["execution_successful"]
        )

        emoji = "❌" if is_code_failure else "✅"

        if details:
            return f"{emoji} {message}\n\n" + "\n".join(details)
        else:
            return f"{emoji} {message}"

    else:
        error = result.get("data", {}).get("error", "Unknown error")
        return f"❌ {error}"


@mcp.tool()
def inkscape_operation(ctx: Context, command: str) -> Union[str, ImageContent]:
    """
    Execute any Inkscape operation using the extension system.

    CRITICAL SYNTAX RULES - READ CAREFULLY:
    1. Single string parameter with space-separated key=value pairs
    2. Children use special bracket syntax: children=[{tag attr=val attr=val}, {tag attr=val}]
    3. NOT JSON objects - use space-separated attributes inside braces
    4. Use 'svg' variable in execute-code, NOT 'self.svg'

    Parameter: command (str) - Command string following exact syntax below

    ═══ BASIC ELEMENTS ═══
    MANDATORY: Always specify id for every element to enable later modification:
    "rect id=main_rect x=100 y=50 width=200 height=100 fill=blue stroke=black stroke-width=2"
    "circle id=logo_circle cx=150 cy=150 r=75 fill=#ff0000"
    "text id=title_text x=50 y=100 text='Hello World' font-size=16 fill=black"

    ═══ AUTOMATIC ELEMENT PLACEMENT ═══
    The system automatically places elements in the correct SVG sections:
    - Basic elements (rect, circle, text, path, etc.) → placed directly in <svg>
    - Definitions (linearGradient, radialGradient, pattern, filter, inkscape:path-effect, etc.) → automatically placed in <defs>

    Path effects example (use inkscape: namespace for Inkscape-specific elements):
    "inkscape:path-effect id=effect1 effect=powerstroke is_visible=true lpeversion=1.3 scale_width=1 interpolator_type=CentripetalCatmullRom interpolator_beta=0.2 start_linecap_type=zerowidth end_linecap_type=zerowidth offset_points='0.2,0.5 | 1,0.5 | 1.8,0.5' linejoin_type=round miter_limit=4 not_jump=false sort_points=true" → automatically goes to <defs>
    "path id=mypath d='M 20,50 C 20,50 80,20 80,80' inkscape:path-effect=#effect1 inkscape:original-d='M 20,50 C 20,50 80,20 80,80'" → path with effect applied

    Filters example (nested primitives with children syntax):
    "filter id=grunge children=[{feTurbulence baseFrequency=2.5 numOctaves=3 result=noise}, {feColorMatrix in=noise type=saturate values=0}, {feComponentTransfer children=[{feFuncA type=discrete tableValues='0 0 .3 0 0 .7 0 0 1'}]}, {feComposite operator=out in=SourceGraphic in2=noise}]" → automatically goes to <defs>
    "rect id=grunge_rect x=100 y=100 width=100 height=100 fill=blue filter=url(#grunge)" → rectangle with grunge texture

    Patterns example (repeating graphics):
    "pattern id=dots width=20 height=20 patternUnits=userSpaceOnUse children=[{circle cx=10 cy=10 r=5 fill=red}]" → automatically goes to <defs>
    "rect id=patterned_rect x=100 y=100 width=100 height=100 fill=url(#dots)" → rectangle with dot pattern

    IMPORTANT: Create defs elements (gradients, patterns, filters) as SEPARATE commands, not as children of groups:
    ✅ CORRECT: "linearGradient id=grad1 ..." (separate command) → automatically goes to <defs>
    ✅ CORRECT: "rect id=shape fill=url(#grad1)" (separate command) → uses the gradient
    ❌ WRONG: "g children=[{linearGradient ...}, {rect ...}]" → this makes gradient stay inside group (not in defs!)

    ═══ NESTED ELEMENTS (Groups) ═══
    Groups with children - ALWAYS specify id for parent and ALL children:
    "g id=house children=[{rect id=house_body x=100 y=200 width=200 height=150 fill=#F5DEB3}, {path id=house_roof d='M 90,200 L 200,100 L 310,200 Z' fill=#A52A2A}]"

    ═══ CODE EXECUTION ═══
    Execute Python code - use 'svg' variable, not 'self.svg':
    CRITICAL: inkex elements require .set() method with string values, NOT constructor arguments!
    "execute-code code='rect = inkex.Rectangle(); rect.set(\"x\", \"100\"); rect.set(\"y\", \"100\"); rect.set(\"width\", \"100\"); rect.set(\"height\", \"100\"); rect.set(\"fill\", \"blue\"); svg.append(rect)'"
    "execute-code code='circle = inkex.Circle(); circle.set(\"cx\", \"150\"); circle.set(\"cy\", \"100\"); circle.set(\"r\", \"20\"); svg.append(circle)'"

    Single-line code (use semicolons for multiple statements):
    "execute-code code='for i in range(3): circle = inkex.Circle(); circle.set(\"cx\", str(i*50+100)); circle.set(\"cy\", \"100\"); circle.set(\"r\", \"20\"); svg.append(circle)'"

    Multiline code (MUST be properly quoted with single quotes):
    "execute-code code='for i in range(3):\n    circle = inkex.Circle()\n    circle.set(\"cx\", str(i*50+100))\n    circle.set(\"cy\", \"100\")\n    circle.set(\"r\", \"20\")\n    svg.append(circle)'"

    Finding and modifying elements by ID (use get_element_by_id helper):
    "execute-code code='el = get_element_by_id(\"house_body\"); el.set(\"fill\", \"brown\") if el else None'"

    ═══ INFO & EXPORT OPERATIONS ═══
    "get-selection" - Get info about selected objects
    "get-info" - Get document information
    "export-document-image format=png return_base64=true" - Screenshot

    ═══ GRADIENTS ═══
    Use gradientUnits=userSpaceOnUse with absolute coordinates matching your shape:
    "linearGradient id=grad1 x1=50 y1=50 x2=150 y2=50 gradientUnits=userSpaceOnUse children=[{stop offset=0% stop-color=red}, {stop offset=100% stop-color=blue}]"
    "rect id=shape x=50 y=50 width=100 height=100 fill=url(#grad1)"

    "radialGradient id=glow cx=200 cy=200 r=50 gradientUnits=userSpaceOnUse children=[{stop offset=0% stop-color=#fff}, {stop offset=100% stop-color=#f00}]"
    "circle id=glowing_circle cx=200 cy=200 r=50 fill=url(#glow)"

    ═══ ID MANAGEMENT ═══
    ALWAYS specify id for every element - this enables later modification and scene management:
    - Input: "g id=scene children=[{rect id=house x=0 y=0}, {circle id=sun cx=100 cy=50}]"
    - Returns: {"id_mapping": {"scene": "scene", "house": "house", "sun": "sun"}}
    - Collision handling: If "house" exists, creates "house_1" and returns {"house": "house_1"}

    ═══ SEMANTIC ORGANIZATION ═══
    Use hierarchical grouping with descriptive IDs whenever possible:

    Example - Creating a park scene with tree:
    "g id=park_scene children=[{g id=tree1 children=[{rect id=trunk1 x=100 y=200 width=20 height=60 fill=brown}, {circle id=foliage1_1 cx=110 cy=180 r=25 fill=green}, {circle id=foliage1_2 cx=105 cy=175 r=20 fill=darkgreen}]}, {g id=house children=[{rect id=house_body x=200 y=180 width=80 height=60 fill=beige}, {polygon id=house_roof points='195,180 240,150 285,180' fill=red}]}]"

    ID Naming Examples:
    - Scene Group: id=park_scene, id=city_view, id=landscape
    - Object Groups: id=tree1, id=tree2, id=house, id=car1
    - Parts: id=trunk1, id=house_body, id=car1_wheel_left
    - Sub-parts: id=foliage1_1, id=foliage1_2, id=house_window1

    Later Modification Examples (use get_element_by_id helper):
    - Change trunk color: execute-code code="el = get_element_by_id('trunk1'); el.set('fill', 'darkbrown') if el else None"
    - Move entire tree: execute-code code="el = get_element_by_id('tree1'); el.set('transform', 'translate(50,0)') if el else None"

    """
    response_file = None
    try:
        connection = get_inkscape_connection()

        # Create unique response file for this operation
        response_fd, response_file = tempfile.mkstemp(
            suffix=".json", prefix="mcp_response_"
        )
        os.close(response_fd)

        # Parse the command string using the same logic as our client
        from inkmcpcli import parse_command_string

        parsed_data = parse_command_string(command)

        # Add response file to the operation data
        parsed_data["response_file"] = response_file

        logger.info(f"Executing command: {command}")
        logger.debug(f"Parsed data: {parsed_data}")

        result = connection.execute_operation(parsed_data)

        # Handle image export special case
        if (
            parsed_data.get("tag") == "export-document-image"
            and result.get("status") == "success"
            and "base64_data" in result.get("data", {})
        ):
            # Return actual image for viewport screenshot
            base64_data = result["data"]["base64_data"]
            return ImageContent(type="image", data=base64_data, mimeType="image/png")

        # Format and return text response
        return format_response(result)

    except Exception as e:
        logger.error(f"Error in inkscape_operation: {e}")
        return f"❌ Operation failed: {str(e)}"
    finally:
        # Clean up response file if it exists
        if response_file and os.path.exists(response_file):
            try:
                os.remove(response_file)
            except OSError:
                pass


# ══════════════════════════════════════════════════════════════════════════════
# EMBROIDERY TOOLS
# ══════════════════════════════════════════════════════════════════════════════


def format_embroidery_response(result: Dict[str, Any]) -> str:
    """Format embroidery operation result for AI client display"""
    if result.get("status") == "success":
        data = result.get("data", {})
        message = data.get("message", "Operation completed successfully")
        details = []

        # Element creation details
        if "element" in data:
            elem = data["element"]
            details.append(f"**Element ID**: `{elem.get('id', 'unknown')}`")
            details.append(f"**Tag**: {elem.get('tag', 'path')}")

        if "stitch_type" in data:
            details.append(f"**Stitch Type**: {data['stitch_type']}")

        if "shape_type" in data:
            details.append(f"**Shape**: {data['shape_type']}")

        if "command" in data:
            details.append(f"**InkMCP Command**:\n```\n{data['command']}\n```")

        # Stitch type listing
        if "stitch_types" in data:
            details.append(f"**Total**: {len(data['stitch_types'])} stitch types")
            if "by_category" in data:
                for cat, stitches in data["by_category"].items():
                    stitch_names = [s["name"] for s in stitches]
                    details.append(f"**{cat.title()}**: {', '.join(stitch_names)}")

        # Parameter listing
        if "supported_params" in data:
            params = data["supported_params"]
            details.append(f"**Parameters** ({len(params)} available):")
            for p in params[:10]:  # Show first 10
                default = p.get("default", "N/A")
                unit = f" {p.get('unit')}" if p.get("unit") else ""
                details.append(
                    f"  - `{p['name']}`: {p.get('description', '')} (default: {default}{unit})"
                )
            if len(params) > 10:
                details.append(f"  - ... and {len(params) - 10} more")

        # Export details
        if "output_path" in data:
            details.append(f"**Output File**: {data['output_path']}")
        if "format" in data:
            details.append(
                f"**Format**: {data.get('format_name', data['format']).upper()}"
            )
        if "file_size_kb" in data:
            details.append(f"**Size**: {data['file_size_kb']} KB")

        # Format listing
        if "formats" in data:
            details.append(f"**Available Formats** ({len(data['formats'])}):")
            popular = data.get("popular", [])
            for fmt in data["formats"]:
                marker = "★" if fmt["format"] in popular else " "
                details.append(
                    f"  {marker} `{fmt['format']}` - {fmt['name']} ({fmt['manufacturer']})"
                )

        # Installation check
        if "inkscape_found" in data:
            ink_status = "✅" if data["inkscape_found"] else "❌"
            details.append(
                f"**Inkscape**: {ink_status} {data.get('inkscape_path', 'Not found')}"
            )
        if "inkstitch_found" in data:
            stitch_status = "✅" if data["inkstitch_found"] else "❌"
            details.append(
                f"**Ink/Stitch**: {stitch_status} {data.get('inkstitch_path', 'Not found')}"
            )

        if details:
            return f"✅ {message}\n\n" + "\n".join(details)
        else:
            return f"✅ {message}"

    else:
        error = result.get("data", {}).get("error", "Unknown error")
        extra_info = []

        # Add installation instructions if present
        if "install_instructions" in result.get("data", {}):
            instructions = result["data"]["install_instructions"]
            extra_info.append("\n**Installation Instructions**:")
            for component, url in instructions.items():
                extra_info.append(f"  - {component.title()}: {url}")

        return f"❌ {error}" + "\n".join(extra_info)


@mcp.tool()
def embroidery_create_element(
    ctx: Context,
    shape_type: str,
    element_id: str,
    stitch_type: str,
    thread_color: str = "#000000",
    x: float = 0,
    y: float = 0,
    width: float = 100,
    height: float = 100,
    cx: float = 50,
    cy: float = 50,
    r: float = 50,
    rx: float = 50,
    ry: float = 30,
    d: str = "",
    stitch_length: float = 2.5,
    fill_angle: float = 0,
    row_spacing: float = 0.25,
    underlay: bool = True,
    label: str = "",
) -> str:
    """
    Create an embroidery element with Ink/Stitch parameters.

    This tool generates SVG path elements configured for embroidery production
    using Ink/Stitch. The output includes both the element specification and
    the InkMCP command to create it in Inkscape.

    Parameters:
        shape_type: Shape to create - "rectangle", "circle", "ellipse", or "path"
        element_id: Unique ID for the element (required for later modification)
        stitch_type: Type of stitch to use. Options:
            - FILL STITCHES: "fill", "auto_fill", "contour_fill", "guided_fill",
              "meander_fill", "circular_fill", "linear_gradient_fill", "tartan_fill"
            - STROKE STITCHES: "running_stitch", "bean_stitch", "manual_stitch",
              "ripple_stitch", "zigzag_stitch"
            - SATIN STITCHES: "satin_column", "e_stitch", "s_stitch", "zigzag_satin"
        thread_color: Thread color in hex format (e.g., "#FF0000" for red)

    Shape Parameters (use based on shape_type):
        Rectangle: x, y, width, height
        Circle: cx, cy, r
        Ellipse: cx, cy, rx, ry
        Path: d (SVG path data string)

    Stitch Parameters:
        stitch_length: Length of each stitch in mm (default: 2.5)
        fill_angle: Angle of fill stitches in degrees (default: 0)
        row_spacing: Spacing between fill rows in mm (default: 0.25)
        underlay: Add underlay stitches for stability (default: True)
        label: Optional label for the element

    Returns:
        Formatted result with element spec and InkMCP command

    Example:
        Create a filled rectangle:
        shape_type="rectangle", element_id="my_rect", stitch_type="fill",
        thread_color="#FF0000", x=100, y=100, width=200, height=150

        Create a satin circle outline:
        shape_type="circle", element_id="my_circle", stitch_type="running_stitch",
        thread_color="#0000FF", cx=200, cy=200, r=50
    """
    # Build shape params based on shape type
    shape_params = {"label": label if label else None}

    if shape_type == "rectangle":
        shape_params.update({"x": x, "y": y, "width": width, "height": height})
    elif shape_type == "circle":
        shape_params.update({"cx": cx, "cy": cy, "r": r})
    elif shape_type == "ellipse":
        shape_params.update({"cx": cx, "cy": cy, "rx": rx, "ry": ry})
    elif shape_type == "path":
        shape_params.update({"d": d})

    # Build stitch params
    params = {
        "stitch_length": stitch_length,
        "fill_angle": fill_angle,
        "row_spacing": row_spacing,
    }

    # Add underlay params if enabled
    if underlay:
        params["fill_underlay"] = True
        params["fill_underlay_angle"] = fill_angle + 90  # Perpendicular

    result = create_embroidery_shape(
        shape_type=shape_type,
        element_id=element_id,
        stitch_type=stitch_type,
        thread_color=thread_color,
        params=params,
        **shape_params,
    )

    return format_embroidery_response(result)


@mcp.tool()
def embroidery_list_stitches(ctx: Context, category: str = "") -> str:
    """
    List all available embroidery stitch types.

    Returns comprehensive information about each stitch type including
    category, description, and requirements.

    Parameters:
        category: Optional filter by category ("stroke", "satin", "fill")
                  Leave empty to list all stitch types.

    Stitch Categories:
        - STROKE: Line-based stitches (running, bean, manual, ripple, zigzag)
        - SATIN: Column stitches with two rails (satin_column, e_stitch, s_stitch)
        - FILL: Area-filling stitches (fill, auto_fill, contour_fill, meander, etc.)

    Returns:
        List of stitch types with descriptions organized by category
    """
    result = list_available_stitch_types()

    if category and result.get("status") == "success":
        # Filter by category if specified
        cat_lower = category.lower()
        if "by_category" in result.get("data", {}):
            filtered = result["data"]["by_category"].get(cat_lower, [])
            if filtered:
                result["data"]["stitch_types"] = filtered
                result["data"]["by_category"] = {cat_lower: filtered}
                result["data"]["message"] = (
                    f"Found {len(filtered)} {cat_lower} stitch types"
                )

    return format_embroidery_response(result)


@mcp.tool()
def embroidery_get_stitch_params(ctx: Context, stitch_type: str) -> str:
    """
    Get detailed parameters for a specific stitch type.

    Returns all available parameters that can be configured for the
    specified stitch type, including defaults, ranges, and descriptions.

    Parameters:
        stitch_type: Name of the stitch type (e.g., "fill", "satin_column", "running_stitch")

    Returns:
        Detailed parameter information including:
        - Parameter name and description
        - Data type (float, int, bool, etc.)
        - Default value
        - Min/max range (if applicable)
        - Unit of measurement

    Common Parameters by Category:
        FILL: fill_angle, row_spacing, stitch_length, underlay options
        SATIN: satin_column width, pull_compensation, zigzag_spacing
        STROKE: stitch_length, bean_stitch_repeats, running_stitch_tolerance
    """
    result = get_stitch_parameters(stitch_type)
    return format_embroidery_response(result)


@mcp.tool()
def embroidery_export(
    ctx: Context,
    svg_path: str,
    output_path: str,
    format: str = "dst",
) -> str:
    """
    Export an SVG embroidery design to machine-readable format.

    Converts an SVG file with Ink/Stitch embroidery elements into a format
    that can be loaded onto embroidery machines.

    Parameters:
        svg_path: Path to input SVG file with embroidery elements
        output_path: Path for output embroidery file
        format: Target format. Popular options:
            - "dst" - Tajima (most universal commercial format)
            - "pes" - Brother/Babylock (most popular home format)
            - "jef" - Janome
            - "exp" - Melco
            - "vp3" - Pfaff
            - "hus" - Husqvarna Viking
            - "xxx" - Singer

    Requirements:
        - Inkscape must be installed
        - Ink/Stitch extension must be installed
        - Use embroidery_check_setup to verify installation

    Returns:
        Export result with file path and size

    Example:
        embroidery_export(
            svg_path="/path/to/design.svg",
            output_path="/path/to/output.dst",
            format="dst"
        )
    """
    result = export_embroidery(svg_path, output_path, format)
    return format_embroidery_response(result)


@mcp.tool()
def embroidery_list_formats(ctx: Context) -> str:
    """
    List all available embroidery export formats.

    Returns information about each supported format including:
    - Format code (dst, pes, jef, etc.)
    - File extension
    - Full name
    - Manufacturer/brand

    Popular formats are marked with ★ for easy identification.

    Returns:
        List of all supported embroidery machine formats
    """
    result = list_export_formats()
    return format_embroidery_response(result)


@mcp.tool()
def embroidery_check_setup(ctx: Context) -> str:
    """
    Check if Ink/Stitch is properly installed and ready for embroidery export.

    Verifies that all required components are installed:
    - Inkscape (vector graphics editor)
    - Ink/Stitch (embroidery extension for Inkscape)

    Returns:
        Installation status with paths and instructions if components are missing

    If components are missing, installation instructions are provided:
    - Inkscape: https://inkscape.org/release/
    - Ink/Stitch: https://inkstitch.org/docs/install/
    """
    result = check_inkstitch_installation()
    return format_embroidery_response(result)


@mcp.tool()
def embroidery_simulate(
    ctx: Context,
    svg_path: str,
    output_path: str = "",
    realistic: bool = True,
) -> str:
    """
    Generate a stitch simulation preview of an embroidery design.

    Creates a visual preview showing how the embroidery will look
    when stitched out. Useful for verifying designs before export.

    Parameters:
        svg_path: Path to input SVG file with embroidery elements
        output_path: Path for output simulation SVG (optional, auto-generated if empty)
        realistic: Use realistic thread rendering (default: True)

    Returns:
        Path to the generated simulation file

    Note: Requires Inkscape and Ink/Stitch to be installed.
    """
    result = generate_stitch_simulation(
        svg_path, output_path if output_path else None, realistic
    )
    return format_embroidery_response(result)


@mcp.tool()
def embroidery_format_info(ctx: Context, format: str) -> str:
    """
    Get detailed information about a specific embroidery format.

    Parameters:
        format: Format code (e.g., "dst", "pes", "jef")

    Returns:
        Detailed format specifications including:
        - Full name and manufacturer
        - Maximum design dimensions
        - Maximum color count
        - Trim/jump stitch support
        - File extension
    """
    result = get_format_info(format)
    return format_embroidery_response(result)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for server configuration"""
    parser = argparse.ArgumentParser(
        description="Inkscape MCP Server - Control Inkscape and create embroidery designs via MCP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with stdio (default, for local MCP clients like Claude Desktop)
  python inkscape_mcp_server.py

  # Run with HTTP transport on localhost:8000
  python inkscape_mcp_server.py --transport http

  # Run with HTTP transport accessible from network
  python inkscape_mcp_server.py --transport http --host 0.0.0.0 --port 9000

  # Run with SSE transport (legacy)
  python inkscape_mcp_server.py --transport sse --port 8000

Transport modes:
  stdio  - Standard I/O (default). Use for local MCP clients.
  http   - HTTP with Streamable HTTP. Recommended for remote/network access.
  sse    - Server-Sent Events. Legacy mode for older clients.
        """,
    )

    parser.add_argument(
        "--transport",
        "-t",
        choices=["stdio", "http", "sse"],
        default="stdio",
        help="Transport mode: stdio (default), http, or sse",
    )

    parser.add_argument(
        "--host",
        "-H",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1). Use 0.0.0.0 for network access.",
    )

    parser.add_argument(
        "--port", "-p", type=int, default=8000, help="Port to listen on (default: 8000)"
    )

    parser.add_argument(
        "--log-level",
        "-l",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    return parser.parse_args()


def main():
    """Run the Inkscape MCP server with configurable transport"""
    args = parse_args()

    # Configure logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    logger.info("Starting Inkscape MCP Server...")
    logger.info(f"Transport: {args.transport}")

    if args.transport == "stdio":
        # Standard I/O mode (default for local MCP clients)
        logger.info("Running in stdio mode")
        mcp.run()

    elif args.transport == "http":
        # HTTP transport with Streamable HTTP (recommended for remote)
        import uvicorn
        from starlette.applications import Starlette
        from starlette.responses import JSONResponse
        from starlette.routing import Route, Mount

        logger.info(f"Running Streamable HTTP server on {args.host}:{args.port}")
        logger.info(f"MCP endpoint: http://{args.host}:{args.port}/mcp")
        logger.info(f"Health endpoint: http://{args.host}:{args.port}/health")

        # Get the Starlette ASGI app for streamable HTTP
        mcp_app = mcp.streamable_http_app()

        # Health check endpoint
        async def health_check(request):
            return JSONResponse(
                {"status": "healthy", "service": "InkscapeMCP", "transport": "http"}
            )

        # Create combined app with health check and MCP routes
        app = Starlette(
            routes=[
                Route("/health", health_check, methods=["GET"]),
                Mount("/", app=mcp_app),
            ]
        )

        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level=args.log_level.lower(),
        )

    elif args.transport == "sse":
        # SSE transport (legacy, for backward compatibility)
        import uvicorn
        from starlette.applications import Starlette
        from starlette.responses import JSONResponse
        from starlette.routing import Route, Mount

        logger.info(f"Running SSE server on {args.host}:{args.port}")
        logger.info(f"SSE endpoint: http://{args.host}:{args.port}/sse")
        logger.info(f"Health endpoint: http://{args.host}:{args.port}/health")
        logger.info(
            "Note: SSE is legacy. Consider using HTTP transport for new projects."
        )

        # Get the Starlette ASGI app for SSE
        sse_mcp_app = mcp.sse_app()

        # Health check endpoint
        async def health_check(request):
            return JSONResponse(
                {"status": "healthy", "service": "InkscapeMCP", "transport": "sse"}
            )

        # Create combined app with health check and SSE routes
        app = Starlette(
            routes=[
                Route("/health", health_check, methods=["GET"]),
                Mount("/", app=sse_mcp_app),
            ]
        )

        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level=args.log_level.lower(),
        )


# ASGI app factory for production deployment with uvicorn/gunicorn
# Usage: uvicorn inkscape_mcp_server:http_app --host 0.0.0.0 --port 8000
def create_http_app():
    """Factory function to create the Streamable HTTP ASGI app"""
    return mcp.streamable_http_app()


def create_sse_app():
    """Factory function to create the SSE ASGI app"""
    return mcp.sse_app()


# Pre-created app instances for direct uvicorn usage
# Usage: uvicorn inkscape_mcp_server:http_app --host 0.0.0.0 --port 8000
http_app = mcp.streamable_http_app()
sse_app = mcp.sse_app()


if __name__ == "__main__":
    main()
