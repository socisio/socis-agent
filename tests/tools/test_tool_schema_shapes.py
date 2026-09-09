"""Tool definitions arrive in two schema shapes; readers must handle both.

``tools/registry.py`` builds a tool's function dict as
``{**entry.schema, "name": ...}``, so a registered tool keeps the Anthropic
``input_schema`` key it was declared with. MCP tools are normalised to OpenAI's
``parameters``. Reading only ``parameters`` returned ``{}`` for EVERY registry
tool — at least 18 of them across cisa_kev, detection_tools,
domain_permutations and yara_strings.

The symptom was never an exception. The model was handed a tool name and a
prose description with no argument names at all, and behaved accordingly:
calling tools with empty arguments purely to read the error and learn the
schema, and guessing that a parameter documented as "YARA rule text" might
accept a file path. MCP tools described correctly throughout, which is why it
survived.
"""

import ast
import pathlib

import pytest

REGISTRY_STYLE = {
    "name": "yargen_generate",
    "description": "...",
    "input_schema": {
        "type": "object",
        "properties": {"samples_dir": {}, "author": {}, "opcodes": {}},
        "required": ["samples_dir"],
    },
}

MCP_STYLE = {
    "name": "remote_thing",
    "description": "...",
    "parameters": {"type": "object", "properties": {"q": {}}, "required": ["q"]},
}


@pytest.fixture(scope="module")
def fn_parameters():
    """Load the helper without importing tool_search.

    tool_search pulls in optional search dependencies that need not be present
    to check a pure schema-shape decision.
    """
    src = pathlib.Path("tools/tool_search.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    node = next(
        n
        for n in tree.body
        if isinstance(n, ast.FunctionDef) and n.name == "_fn_parameters"
    )
    ns = {"Dict": dict, "Any": object}
    exec(  # noqa: S102 - a single function definition from our own source
        compile(ast.Module(body=[node], type_ignores=[]), "<fn>", "exec"), ns
    )
    return ns["_fn_parameters"]


def _props(fn_parameters, fn):
    return sorted((fn_parameters(fn).get("properties") or {}).keys())


def test_registry_input_schema_is_read(fn_parameters):
    assert _props(fn_parameters, REGISTRY_STYLE) == ["author", "opcodes", "samples_dir"]


def test_mcp_parameters_still_read(fn_parameters):
    assert _props(fn_parameters, MCP_STYLE) == ["q"]


def test_parameters_wins_when_both_are_present(fn_parameters):
    fn = {
        "parameters": {"type": "object", "properties": {"p": {}}},
        "input_schema": {"type": "object", "properties": {"i": {}}},
    }
    assert _props(fn_parameters, fn) == ["p"]


def test_empty_parameters_falls_through_to_input_schema(fn_parameters):
    """The exact failing shape: `parameters` present but empty."""
    fn = {"parameters": {}, "input_schema": {"type": "object", "properties": {"x": {}}}}
    assert _props(fn_parameters, fn) == ["x"]


def test_malformed_parameters_do_not_raise(fn_parameters):
    fn = {"parameters": "nonsense", "input_schema": {"properties": {"y": {}}}}
    assert _props(fn_parameters, fn) == ["y"]


def test_neither_key_returns_empty(fn_parameters):
    assert _props(fn_parameters, {"description": "x"}) == []


def test_required_is_preserved(fn_parameters):
    assert fn_parameters(REGISTRY_STYLE).get("required") == ["samples_dir"]


def test_registered_detection_tools_expose_their_parameters(fn_parameters):
    """End-to-end over the real schemas, the way registry.py assembles them.

    Guards the whole class rather than one helper: if a future tool is declared
    in a third shape, this fails rather than silently offering the model a
    nameless tool.
    """
    import re

    src = pathlib.Path("tools/detection_tools.py").read_text(encoding="utf-8")
    found = {}
    for m in re.finditer(
        r'registry\.register\(\s*name="(\w+)".*?schema=(\{.*?\}),\s*\n\s*handler=',
        src,
        re.S,
    ):
        name, literal = m.group(1), m.group(2)
        schema = ast.literal_eval(literal)
        fn = {**schema, "name": name}  # exactly what registry.py builds
        found[name] = _props(fn_parameters, fn)

    assert found, "no registered tools parsed out of detection_tools.py"
    for name, params in found.items():
        assert params, f"{name} exposes no parameter names to the model"

    # Spot-check the two whose arguments were invisible in a live session.
    assert "samples_dir" in found["yargen_generate"]
    assert "rule_file" in found["yara_scan"]
