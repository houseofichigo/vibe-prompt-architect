#!/usr/bin/env python3
"""Shared, dependency-free rules for Agent Skills (SKILL.md) packages.

This module is the single source of truth used by Skill Repo Forge's audit,
build and verify scripts. It is also copied verbatim into every generated
repository (as ``scripts/skill_rules.py``) so the repository can validate and
rebuild itself without Skill Repo Forge installed.

Targets
-------
``portable``  the open Agent Skills specification (agentskills.io/specification)
``claude``    portable + Claude rules (reserved words, no XML tags)
``openai``    portable + OpenAI/Codex rules (no angle brackets, agents/openai.yaml)
``all``       every rule above; the default, for Skills meant to run everywhere

Only the Python 3.9+ standard library is used.
"""

from __future__ import annotations

import os
import re
import stat
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

RULES_VERSION = "1.0.0"

TARGETS = ("all", "portable", "claude", "openai")
TARGET_ALIASES = {"anthropic": "claude", "codex": "openai", "chatgpt": "openai"}

# Agent Skills spec frontmatter fields.
SPEC_KEYS = ("name", "description", "license", "compatibility", "metadata", "allowed-tools")
# Fields accepted by OpenAI's skill-creator validator (quick_validate.py).
OPENAI_VALIDATOR_KEYS = ("name", "description", "license", "allowed-tools", "metadata")
CLAUDE_RESERVED_WORDS = ("anthropic", "claude")

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
XML_TAG_RE = re.compile(r"<[^>]*>")
MAX_NAME = 64
MAX_DESCRIPTION = 1024
MAX_COMPATIBILITY = 500
MAX_BODY_LINES = 500

# Files and folders never shipped in a Skill payload.
EXCLUDE_PARTS = {
    ".git", "__pycache__", ".DS_Store", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", ".venv", "venv", "node_modules", ".idea", ".vscode",
}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}
SENSITIVE_NAMES = {"id_rsa", "id_dsa", "id_ecdsa", "id_ed25519", ".git-credentials", ".netrc", ".npmrc", ".pypirc"}

ZIP_DATE = (2020, 1, 1, 0, 0, 0)

Finding = Tuple[str, str, str, Optional[str]]  # (severity, code, message, path)
Value = Union[str, List[str], Dict[str, str]]


def normalize_target(target: str) -> str:
    t = (target or "all").strip().lower()
    t = TARGET_ALIASES.get(t, t)
    if t not in TARGETS:
        raise ValueError(f"Unknown target '{target}'. Use one of: {', '.join(TARGETS)}")
    return t


def wants(target: str, host: str) -> bool:
    """True when rules for ``host`` ('claude' or 'openai') must be enforced as blockers."""
    return target == "all" or target == host


# ---------------------------------------------------------------------------
# Frontmatter parsing (a strict, documented subset of YAML)
# ---------------------------------------------------------------------------

STRING_KEYS = ("name", "description", "license", "compatibility", "allowed-tools")

# Plain scalars that YAML 1.1 loaders (PyYAML, used by most hosts) do not read as strings.
_IMPLICIT = [
    ("boolean", re.compile(r"^(?:y|Y|yes|Yes|YES|n|N|no|No|NO|true|True|TRUE|false|False|FALSE|on|On|ON|off|Off|OFF)$")),
    ("null", re.compile(r"^(?:~|null|Null|NULL)$")),
    ("integer", re.compile(r"^[-+]?(?:0b[01_]+|0x[0-9a-fA-F_]+|0[0-7_]+|(?:0|[1-9][0-9_]*)|[1-9][0-9_]*(?::[0-5]?[0-9])+)$")),
    ("float", re.compile(r"^[-+]?(?:(?:[0-9][0-9_]*)?\.[0-9_]*(?:[eE][-+]?[0-9]+)?|[0-9][0-9_]*(?::[0-5]?[0-9])+\.[0-9_]*|\.(?:inf|Inf|INF))$|^\.(?:nan|NaN|NAN)$")),
    ("date", re.compile(r"^[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}(?:[Tt ].*)?$")),
]
_ESCAPES = {"0": "\0", "a": "\a", "b": "\b", "t": "\t", "\t": "\t", "n": "\n", "v": "\v", "f": "\f", "r": "\r",
            "e": "\x1b", " ": " ", '"': '"', "/": "/", "\\": "\\", "N": "\x85", "_": "\xa0", "L": " ", "P": " "}
_KEY_LINE = re.compile(r"^([^\s:#'\"-][^:]*|'[^']*'|\"[^\"]*\"):(?:[ \t]+(.*))?$")


class _Msgs:
    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []


def _implicit_type(value: str) -> Optional[str]:
    if value == "":
        return None
    for label, pat in _IMPLICIT:
        if pat.match(value) and not (label == "float" and value in (".", "-.", "+.")):
            return label
    return None


def _unescape_double(s: str, key: str, msgs: _Msgs) -> str:
    def repl(m: "re.Match[str]") -> str:
        esc = m.group(1)
        if esc[0] in "xuU":
            try:
                return chr(int(esc[1:], 16))
            except ValueError:
                msgs.errors.append(f"`{key}`: invalid escape \\{esc}")
                return ""
        if esc in _ESCAPES:
            return _ESCAPES[esc]
        msgs.errors.append(f"`{key}`: invalid escape \\{esc}")
        return esc
    return re.sub(r"\\(x[0-9A-Fa-f]{2}|u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8}|.)", repl, s)


def _plain_piece(raw: str, key: str, msgs: _Msgs, first: bool) -> Tuple[str, bool]:
    """Validate one line of a plain scalar. Returns (text, comment_found)."""
    comment = re.search(r"(?:^|[ \t])#", raw)
    text = raw
    if comment:
        text = raw[:comment.start()].rstrip()
    if first and text and (text[0] in "[]{}&*!%@`,?|>\"'" or text.startswith("- ") or text == "-"):
        msgs.errors.append(f"`{key}`: value starts with a YAML indicator character ({text[0]!r}); wrap the value in quotes")
    if ": " in text or "\t:" in text or text.endswith(":"):
        msgs.errors.append(f"`{key}`: unquoted value contains ': ', which is invalid YAML on most hosts; wrap the value in quotes")
    if comment:
        msgs.warnings.append(f"`{key}`: YAML treats ' #…' as a comment, so the value ends before it; quote the value if '#' is meant as text")
    return text, bool(comment)


def _quoted(raw: str, key: str, msgs: _Msgs) -> Optional[str]:
    if raw[0] == '"':
        m = re.fullmatch(r'"((?:[^"\\]|\\.)*)"(?:[ \t]+#.*)?', raw)
        if m:
            return _unescape_double(m.group(1), key, msgs)
        msgs.errors.append(f"`{key}`: malformed double-quoted string (unterminated, or text after the closing quote)")
        return raw.strip('"')
    m = re.fullmatch(r"'((?:[^']|'')*)'(?:[ \t]+#.*)?", raw)
    if m:
        return m.group(1).replace("''", "'")
    msgs.errors.append(f"`{key}`: malformed single-quoted string (unterminated, or text after the closing quote)")
    return raw.strip("'")


def _scalar(raw: str, key: str, msgs: _Msgs, strict_type: bool) -> Value:
    raw = raw.strip()
    if not raw:
        return ""
    if raw[0] in "\"'":
        return _quoted(raw, key, msgs) or ""
    if raw[0] == "[":
        m = re.fullmatch(r"\[(.*)\](?:[ \t]+#.*)?", raw)
        if not m:
            msgs.errors.append(f"`{key}`: malformed flow list; use one '- item' per line")
            return raw
        items = []
        for part in [s.strip() for s in m.group(1).split(",") if s.strip()]:
            items.append(_quoted(part, key, msgs) if part[0] in "\"'" else part)
        return [str(x) for x in items]
    text, _ = _plain_piece(raw, key, msgs, first=True)
    kind = _implicit_type(text)
    if kind:
        msg = f"`{key}`: YAML reads `{text}` as a {kind}, not a string; wrap it in quotes"
        (msgs.errors if strict_type else msgs.warnings).append(msg)
    return text


def parse_frontmatter_ex(text: str) -> Tuple[Optional[Dict[str, Value]], List[str], List[str], str]:
    """Parse SKILL.md frontmatter. Returns ``(fields, errors, warnings, body)``.

    ``fields`` is None when there is no frontmatter block. Supported YAML:
    ``key: value`` scalars (plain, single- or double-quoted, trailing
    comments), block scalars (``>``, ``|`` with ``-``/``+``), multi-line plain
    scalars, one-level maps (``metadata``) and string lists (``[a, b]`` or
    ``- a``). Values YAML would not read as strings, and YAML traps such as
    an unquoted ``: ``, are reported.
    """
    msgs = _Msgs()
    text = text.lstrip("﻿")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, ["SKILL.md must start with a '---' YAML frontmatter line"], [], text
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return None, ["frontmatter is not closed with a '---' line"], [], text
    fm = lines[1:end]
    body = "\n".join(lines[end + 1:])
    fields: Dict[str, Value] = {}
    i = 0

    def indented(line: str) -> bool:
        return line[:1] in (" ", "\t")

    def take_block() -> List[str]:
        nonlocal i
        block = []
        while i < len(fm) and (indented(fm[i]) or not fm[i].strip()):
            block.append(fm[i])
            i += 1
        while block and not block[-1].strip():
            block.pop()
        return block

    while i < len(fm):
        line = fm[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if indented(line):
            msgs.errors.append(f"frontmatter line {i + 2}: unexpected indentation")
            i += 1
            continue
        m = re.match(r"^([A-Za-z0-9_.-]+):(?:[ \t]+(.*))?$", line)
        if not m:
            msgs.errors.append(f"frontmatter line {i + 2}: expected 'key: value'")
            i += 1
            continue
        key, raw = m.group(1), (m.group(2) or "").rstrip()
        strict = key in STRING_KEYS
        if key in fields:
            msgs.errors.append(f"duplicate frontmatter key `{key}`")
        i += 1

        header = re.match(r"^([>|])([+-]?)(?:[ \t]+#.*)?$", raw)
        if header:
            block = [b.strip() for b in take_block()]
            if header.group(1) == ">":
                paras, cur = [], []
                for b in block:
                    if b:
                        cur.append(b)
                    else:
                        paras.append(" ".join(cur))
                        cur = []
                paras.append(" ".join(cur))
                value = "\n".join(paras)
            else:
                value = "\n".join(block)
            fields[key] = value + ("" if header.group(2) == "-" or not value else "\n")
            continue

        if raw == "" or raw.startswith("#"):
            block = [b for b in take_block() if b.strip() and not b.strip().startswith("#")]
            if not block:
                fields[key] = ""
                continue
            first = block[0].strip()
            if first.startswith("- ") or first == "-":
                items = []
                for b in block:
                    c = b.strip()
                    if not (c.startswith("- ") or c == "-"):
                        msgs.errors.append(f"`{key}`: mixes list items with other lines")
                        continue
                    v = _scalar(c[1:].strip(), key, msgs, strict_type=False)
                    if not isinstance(v, str):
                        msgs.errors.append(f"`{key}`: nested lists are not supported")
                    items.append(str(v))
                fields[key] = items
            elif _KEY_LINE.match(first):
                children: Dict[str, str] = {}
                for b in block:
                    c = b.strip()
                    cm = _KEY_LINE.match(c)
                    if not cm:
                        msgs.errors.append(f"`{key}`: cannot parse nested line '{c}' (only one level of nesting is supported)")
                        continue
                    ck = cm.group(1).strip().strip("'\"")
                    if cm.group(2) is None:
                        msgs.errors.append(f"`{key}.{ck}`: nested maps deeper than one level are not supported")
                        continue
                    v = _scalar(cm.group(2), f"{key}.{ck}", msgs, strict_type=False)
                    if not isinstance(v, str):
                        msgs.errors.append(f"`{key}.{ck}`: values must be strings, not lists")
                        v = str(v)
                    children[ck] = v
                fields[key] = children
            else:  # multi-line plain scalar starting on the next line
                parts = []
                for n, b in enumerate(block):
                    piece, stop = _plain_piece(b.strip(), key, msgs, first=(n == 0))
                    parts.append(piece)
                    if stop:
                        break
                fields[key] = " ".join(p for p in parts if p)
            continue

        value = _scalar(raw, key, msgs, strict_type=strict)
        stopped = raw[0] not in "\"'[" and bool(re.search(r"(?:^|[ \t])#", raw))
        cont: List[str] = []
        while i < len(fm) and indented(fm[i]) and fm[i].strip():
            cont.append(fm[i].strip())
            i += 1
        if cont:
            if raw[0] in "\"'[":
                msgs.errors.append(f"`{key}`: quoted or bracketed values must stay on one line")
            elif stopped:
                msgs.errors.append(f"`{key}`: indented lines after a comment are invalid YAML")
            else:
                parts = [str(value)]
                for c in cont:
                    if c.startswith("#"):
                        msgs.warnings.append(f"`{key}`: a line starting with '#' ends the value (YAML comment); quote the value if it is text")
                        break
                    piece, stop = _plain_piece(c, key, msgs, first=False)
                    parts.append(piece)
                    if stop:
                        break
                value = " ".join(p for p in parts if p)
                # A multi-line plain scalar is always a string; drop any single-line type complaint.
                msgs.errors = [e for e in msgs.errors if not e.startswith(f"`{key}`: YAML reads")]
                msgs.warnings = [w for w in msgs.warnings if not w.startswith(f"`{key}`: YAML reads")]
        fields[key] = value
    return fields, msgs.errors, msgs.warnings, body


def parse_frontmatter(text: str) -> Tuple[Optional[Dict[str, Value]], List[str], str]:
    """Backward-compatible wrapper: returns ``(fields, errors, body)``."""
    fields, errors, _warnings, body = parse_frontmatter_ex(text)
    return fields, errors, body


# ---------------------------------------------------------------------------
# Rule checks
# ---------------------------------------------------------------------------

def _add(out: List[Finding], sev: str, code: str, msg: str, path: Optional[str] = "SKILL.md") -> None:
    out.append((sev, code, msg, path))


def check_frontmatter(fields: Dict[str, Value], dir_name: Optional[str], target: str) -> List[Finding]:
    target = normalize_target(target)
    out: List[Finding] = []
    claude_sev = "blocker" if wants(target, "claude") else "warning"
    openai_sev = "blocker" if wants(target, "openai") else "warning"

    name = fields.get("name")
    if name is None or name == "":
        _add(out, "blocker", "missing_name", "Frontmatter requires `name`")
    elif not isinstance(name, str):
        _add(out, "blocker", "invalid_name_type", "`name` must be a string")
    else:
        if len(name) > MAX_NAME:
            _add(out, "blocker", "name_too_long", f"`name` is {len(name)} characters; the limit is {MAX_NAME}")
        if not NAME_RE.fullmatch(name):
            _add(out, "blocker", "invalid_name", "`name` must use lowercase letters, digits and single hyphens, and must not start or end with a hyphen")
        if dir_name is not None and dir_name != name:
            _add(out, "blocker" if target in ("all", "portable") else "warning", "name_directory_mismatch",
                 f"`name` ({name}) must match the Skill folder name ({dir_name})")
        hit = [w for w in CLAUDE_RESERVED_WORDS if w in name]
        if hit:
            _add(out, claude_sev, "claude_reserved_word",
                 f"Claude rejects Skill names containing the reserved word(s): {', '.join(hit)}")
        if "<" in name or ">" in name:
            _add(out, "blocker", "name_angle_brackets", "`name` must not contain angle brackets")

    desc = fields.get("description")
    if desc is None or (isinstance(desc, str) and not desc.strip()):
        _add(out, "blocker", "missing_description", "Frontmatter requires a non-empty `description`")
    elif not isinstance(desc, str):
        _add(out, "blocker", "invalid_description_type", "`description` must be a string")
    else:
        if len(desc) > MAX_DESCRIPTION:
            _add(out, "blocker", "description_too_long", f"`description` is {len(desc)} characters; the limit is {MAX_DESCRIPTION}")
        if XML_TAG_RE.search(desc):
            _add(out, claude_sev, "description_xml_tag", "Claude rejects descriptions containing XML tags")
        if "<" in desc or ">" in desc:
            _add(out, openai_sev, "description_angle_brackets", "OpenAI's Skill validator rejects `<` or `>` in the description")
        if len(desc) < 40:
            _add(out, "warning", "thin_description", "Description is short; say what the Skill does and when to use it")
        if not re.search(r"\b(use|when|whenever|asks?|request(?:s|ed)?|trigger)\b", desc, re.I):
            _add(out, "warning", "trigger_context_unclear", "Description may not say when the Skill should be used")
        if re.search(r"\b(TODO|TBD|FIXME|lorem ipsum)\b", desc, re.I):
            _add(out, "blocker", "placeholder_description", "Description contains placeholder text")

    for key in fields:
        if key not in SPEC_KEYS:
            _add(out, "warning", "non_spec_frontmatter_key",
                 f"`{key}` is not an Agent Skills spec field; hosts may ignore or reject it")
        elif key not in OPENAI_VALIDATOR_KEYS:
            _add(out, "warning", "openai_validator_key",
                 f"`{key}` is in the Agent Skills spec but OpenAI's skill-creator validator does not accept it")

    if "license" in fields:
        lic = fields["license"]
        if not isinstance(lic, str) or not lic.strip():
            _add(out, "blocker", "invalid_license", "`license` must be a non-empty string")

    if "compatibility" in fields:
        comp = fields["compatibility"]
        if not isinstance(comp, str) or not comp.strip():
            _add(out, "blocker", "invalid_compatibility", "`compatibility` must be a non-empty string when present")
        elif len(comp) > MAX_COMPATIBILITY:
            _add(out, "blocker", "compatibility_too_long", f"`compatibility` exceeds {MAX_COMPATIBILITY} characters")

    if "metadata" in fields:
        meta = fields["metadata"]
        if not isinstance(meta, dict) or not meta:
            _add(out, "blocker", "invalid_metadata", "`metadata` must be a map of string keys to string values")

    if "allowed-tools" in fields:
        tools = fields["allowed-tools"]
        if isinstance(tools, dict) or tools == "":
            _add(out, "blocker", "invalid_allowed_tools", "`allowed-tools` must be a space-separated string")
        else:
            _add(out, "note", "allowed_tools_experimental", "`allowed-tools` is experimental; support varies by host", "SKILL.md")
    return out


def check_openai_yaml(skill_root: Path, name: Optional[str], target: str) -> List[Finding]:
    target = normalize_target(target)
    out: List[Finding] = []
    path = skill_root / "agents" / "openai.yaml"
    rel = "agents/openai.yaml"
    if not path.is_file():
        if target == "openai":
            _add(out, "warning", "missing_openai_yaml", "Codex/ChatGPT show nicer UI metadata when agents/openai.yaml exists", rel)
        elif target == "all":
            _add(out, "note", "missing_openai_yaml", "Optional agents/openai.yaml improves how the Skill appears in Codex/ChatGPT", rel)
        return out
    text = path.read_text(encoding="utf-8", errors="replace")

    def field(key: str) -> Optional[str]:
        m = re.search(rf"(?m)^\s+{re.escape(key)}:\s*(.*)$", text)
        if not m:
            return None
        v = m.group(1).strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        return v

    if not re.search(r"(?m)^interface:\s*$", text):
        _add(out, "warning", "openai_yaml_no_interface", "agents/openai.yaml should define an `interface:` block", rel)
    if not field("display_name"):
        _add(out, "warning", "openai_yaml_display_name", "agents/openai.yaml should define interface.display_name", rel)
    short = field("short_description")
    if short is not None and not (25 <= len(short) <= 64):
        _add(out, "warning", "openai_yaml_short_description", f"interface.short_description should be 25-64 characters (is {len(short)})", rel)
    prompt = field("default_prompt")
    if prompt is not None and name and f"${name}" not in prompt:
        _add(out, "warning", "openai_yaml_default_prompt", f"interface.default_prompt should mention the Skill as ${name}", rel)
    root = skill_root.resolve()
    for icon_key in ("icon_small", "icon_large"):
        icon = field(icon_key)
        if not icon:
            continue
        ip = (root / icon).resolve()
        try:
            ip.relative_to(root)
        except ValueError:
            _add(out, "blocker", "openai_yaml_icon_outside", f"interface.{icon_key} points outside the Skill folder: {icon}", rel)
            continue
        if not ip.is_file():
            _add(out, "blocker", "openai_yaml_missing_icon", f"interface.{icon_key} points to a missing file: {icon}", rel)
    color = field("brand_color")
    if color and not re.fullmatch(r"#[0-9A-Fa-f]{6}", color):
        _add(out, "warning", "openai_yaml_brand_color", "interface.brand_color should be a hex color like #1A2B3C", rel)
    return out


LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
RESOURCE_RE = re.compile(r"(?<![A-Za-z0-9_./$-])((?:scripts|references|assets|agents)/[A-Za-z0-9_./-]*[A-Za-z0-9_-]\.[A-Za-z0-9]+)")


def local_references(text: str) -> Tuple[List[str], List[str]]:
    """Return (markdown link targets, bare resource-path mentions), both local."""
    links = set()
    for raw in LINK_RE.findall(text):
        raw = raw.split("#", 1)[0].strip()
        if not raw or re.match(r"^[a-z][a-z0-9+.-]*:", raw, re.I) or raw.startswith("/"):
            continue
        links.add(raw)
    mentions = {m.group(1) for m in RESOURCE_RE.finditer(text)} - links
    return sorted(links), sorted(mentions)


def check_references(skill_root: Path, text: str) -> List[Finding]:
    out: List[Finding] = []
    root = skill_root.resolve()
    links, mentions = local_references(text)
    for ref, is_link in [(r, True) for r in links] + [(r, False) for r in mentions]:
        p = (root / ref).resolve()
        try:
            p.relative_to(root)
        except ValueError:
            _add(out, "blocker", "reference_escapes_root", f"Reference points outside the Skill folder: {ref}")
            continue
        if not p.exists():
            if is_link:
                _add(out, "blocker", "missing_resource_reference", f"Linked file does not exist: {ref}")
            else:
                _add(out, "warning", "missing_resource_mention",
                     f"`{ref}` is mentioned but not bundled; fine only if it refers to a file outside the Skill")
    return out


SAFE_ENV_TEMPLATES = {".env.example", ".env.sample", ".env.template", ".env.dist"}


def is_sensitive(name: str) -> bool:
    low = name.lower()
    if low in SAFE_ENV_TEMPLATES:
        return False
    return (low == ".env" or low.startswith(".env.") or low in SENSITIVE_NAMES
            or low.endswith((".pem", ".key", ".p12", ".pfx")))


def excluded(name: str) -> bool:
    """Never part of a Skill payload: caches, editor folders, credentials."""
    return name in EXCLUDE_PARTS or Path(name).suffix in EXCLUDE_SUFFIXES or is_sensitive(name)


def payload_files(skill_root: Path) -> List[Tuple[str, Path]]:
    """Files that belong in the canonical Skill payload, sorted, POSIX-relative."""
    out: List[Tuple[str, Path]] = []
    for current, dirs, names in os.walk(skill_root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDE_PARTS and not (Path(current) / d).is_symlink())
        for n in sorted(names):
            p = Path(current) / n
            if excluded(n) or p.is_symlink():
                continue
            out.append((p.relative_to(skill_root).as_posix(), p))
    out.sort(key=lambda t: t[0])
    return out


def check_tree(skill_root: Path) -> List[Finding]:
    out: List[Finding] = []
    for current, dirs, names in os.walk(skill_root, followlinks=False):
        for n in list(dirs) + list(names):
            p = Path(current) / n
            rel = p.relative_to(skill_root).as_posix()
            if p.is_symlink():
                _add(out, "blocker", "symlink", "Symlinks are not allowed in a Skill payload", rel)
            if p.is_file() and is_sensitive(n):
                _add(out, "blocker", "sensitive_file", "Credential-like file; it is excluded from every package, but remove it from the source", rel)
        dirs[:] = [d for d in dirs if d not in EXCLUDE_PARTS]
    return out


def validate_skill_dir(skill_root: Path, target: str = "all", check_dir_name: bool = True) -> Tuple[Dict[str, Value], List[Finding]]:
    """Structural validation of one Skill folder. Returns (frontmatter, findings)."""
    target = normalize_target(target)
    findings: List[Finding] = []
    skill_md = skill_root / "SKILL.md"
    if not skill_md.is_file():
        _add(findings, "blocker", "missing_skill_md", "SKILL.md is required")
        return {}, findings
    raw = skill_md.read_bytes()
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        _add(findings, "blocker", "not_utf8", "SKILL.md is UTF-16; save it as UTF-8")
        return {}, findings
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        _add(findings, "blocker", "not_utf8", f"SKILL.md is not valid UTF-8 (byte {e.start}); save it as UTF-8")
        return {}, findings
    fields, errors, warnings, body = parse_frontmatter_ex(text)
    for e in errors:
        _add(findings, "blocker", "invalid_frontmatter", e)
    for w in warnings:
        _add(findings, "warning", "frontmatter_yaml", w)
    fields = fields or {}
    if fields or not errors:
        findings += check_frontmatter(fields, skill_root.name if check_dir_name else None, target)
    if not body.strip():
        _add(findings, "blocker", "empty_body", "SKILL.md has no instructions after the frontmatter")
    n = len(body.splitlines())
    if n > MAX_BODY_LINES:
        _add(findings, "warning", "skill_md_long", f"SKILL.md body is {n} lines; the spec recommends under {MAX_BODY_LINES}")
    findings += check_references(skill_root, text)
    findings += check_openai_yaml(skill_root, fields.get("name") if isinstance(fields.get("name"), str) else None, target)
    findings += check_tree(skill_root)
    return fields, findings


# ---------------------------------------------------------------------------
# Deterministic skill.zip
# ---------------------------------------------------------------------------

def _mode(p: Path) -> int:
    """0755 for scripts with a shebang line, else 0644: identical on every OS and checkout."""
    with open(p, "rb") as fh:
        return 0o755 if fh.read(2) == b"#!" else 0o644


def build_zip(skill_root: Path, out_zip: Path, name: str) -> List[str]:
    """Write a byte-reproducible ZIP with one top-level folder named ``name``."""
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    written: List[str] = []
    tmp = out_zip.with_suffix(out_zip.suffix + ".tmp")
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel, p in payload_files(skill_root):
            zi = zipfile.ZipInfo(f"{name}/{rel}", date_time=ZIP_DATE)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.create_system = 3
            zi.external_attr = (stat.S_IFREG | _mode(p)) << 16
            zf.writestr(zi, p.read_bytes())
            written.append(f"{name}/{rel}")
    os.replace(tmp, out_zip)
    return written


def compare_zip(skill_root: Path, zip_path: Path, name: str) -> List[str]:
    """Return human-readable differences between the Skill folder and its ZIP."""
    if not zip_path.is_file():
        return [f"{zip_path.name} does not exist"]
    try:
        with zipfile.ZipFile(zip_path) as zf:
            infos = [i for i in zf.infolist() if not i.filename.endswith("/")]
            in_zip = {i.filename: zf.read(i) for i in infos}
            modes = {i.filename: (i.external_attr >> 16) & 0o777 for i in infos}
    except zipfile.BadZipFile:
        return [f"{zip_path.name} is not a valid ZIP"]
    expected = {f"{name}/{rel}": p for rel, p in payload_files(skill_root)}
    diffs: List[str] = []
    for n in sorted(set(expected) - set(in_zip)):
        diffs.append(f"missing from ZIP: {n}")
    for n in sorted(set(in_zip) - set(expected)):
        diffs.append(f"in ZIP but not in the Skill folder: {n}")
    for n in sorted(set(expected) & set(in_zip)):
        if expected[n].read_bytes() != in_zip[n]:
            diffs.append(f"content differs: {n}")
        elif modes[n] != _mode(expected[n]):
            diffs.append(f"file mode differs: {n}")
    return diffs


def find_repo_skill(repo_root: Path) -> Tuple[Optional[Path], List[Path]]:
    """Locate the single Skill at skills/<name>/SKILL.md in a repository."""
    roots = sorted(p.parent for p in (repo_root / "skills").glob("*/SKILL.md")) if (repo_root / "skills").is_dir() else []
    return (roots[0] if len(roots) == 1 else None), roots


def format_findings(findings: List[Finding]) -> str:
    order = {"blocker": 0, "warning": 1, "note": 2}
    lines = []
    for sev, code, msg, path in sorted(findings, key=lambda f: order.get(f[0], 3)):
        loc = f" [{path}]" if path else ""
        lines.append(f"- {sev.upper()} {code}{loc}: {msg}")
    return "\n".join(lines)
