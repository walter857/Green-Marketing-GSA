"""UserPromptSubmit hook: name the skills that fit each request.

Reads the hook payload on stdin, matches the prompt against skill-routes.json, and
prints additionalContext naming the project skill to load first and the supporting
plugin skills to consult. Prints nothing when no route matches. The prompt is only
matched in memory; nothing is logged or sent anywhere.

The hook never blocks a prompt: every failure exits 0 with no output.

    python skill_router.py                     hook mode (payload on stdin)
    python skill_router.py --check             validate routes and skill names
    python skill_router.py --explain "text"    show what a prompt would route to
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROUTES_FILE = HERE / "skill-routes.json"
PROJECT_DIR = HERE.parents[1]
REQUIRED_KEYS = ("id", "patterns", "primary", "support", "note")
INVOKED = re.compile(r"^/([\w:-]+)")


def load_routes() -> dict:
    data = json.loads(ROUTES_FILE.read_text(encoding="utf-8"))
    for route in data["routes"]:
        route["_compiled"] = [re.compile(p, re.IGNORECASE) for p in route["patterns"]]
    return data


def match(data: dict, prompt: str) -> tuple[list[dict], set[str]]:
    """Return the best routes (most patterns hit, then file order) and any /skill invoked."""
    text = prompt.strip().lower()
    invoked = set(INVOKED.findall(text))
    scored = []
    for index, route in enumerate(data["routes"]):
        score = sum(1 for rx in route["_compiled"] if rx.search(text))
        if score:
            scored.append((-score, index, route))
    scored.sort(key=lambda item: (item[0], item[1]))
    return [route for _, _, route in scored[: data.get("max_routes", 3)]], invoked


def build_context(data: dict, routes: list[dict], invoked: set[str]) -> str:
    primary: list[str] = []
    support: list[str] = []
    for route in routes:
        for skill in route["primary"]:
            if skill not in primary and skill not in invoked:
                primary.append(skill)
    for route in routes:
        for skill in route["support"]:
            if skill not in support and skill not in primary and skill not in invoked:
                support.append(skill)
    support = support[: data.get("max_support", 4)]

    lines = [f"Skill router matched: {', '.join(r['id'] for r in routes)}."]
    if primary:
        lines.append(f"Load first (skip if already loaded this session): {', '.join(primary)}.")
    if support:
        lines.append(f"Then consult once per session (skip any already loaded): {', '.join(support)}.")
    lines.extend(f"[{r['id']}] {r['note']}" for r in routes if r["note"])
    if primary or support:
        lines.append(data["precedence"])
    return "\n".join(lines)


def route_prompt(prompt: str) -> str:
    if len(prompt.strip()) < 3:
        return ""
    data = load_routes()
    routes, invoked = match(data, prompt)
    return build_context(data, routes, invoked) if routes else ""


def hook_main() -> None:
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        payload = json.loads(raw) if raw.strip() else {}
        context = route_prompt(payload.get("prompt") or "")
        if context:
            sys.stdout.write(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": context,
                }
            }))
    except Exception:  # noqa: BLE001 - a routing hint must never block the prompt
        return


def skill_exists(name: str) -> bool:
    if ":" in name:
        plugin, skill = name.split(":", 1)
        config = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
        installed = (config / "plugins" / "cache").glob(f"*/{plugin}/*/**/{skill}/SKILL.md")
        skills_dir = config / "skills" / plugin / "skills" / skill / "SKILL.md"
        return skills_dir.exists() or any(True for _ in installed)
    return ((PROJECT_DIR / ".claude" / "commands" / f"{name}.md").exists()
            or (PROJECT_DIR / ".claude" / "skills" / name / "SKILL.md").exists())


def check_main() -> int:
    problems: list[str] = []
    try:
        data = load_routes()
    except (OSError, ValueError, re.error) as exc:
        print(f"FAIL cannot load {ROUTES_FILE.name}: {exc}")
        return 1
    if not data.get("precedence"):
        problems.append("precedence text is missing")
    external = set(data.get("external_skills", []))
    seen_ids: set[str] = set()
    checked: dict[str, bool] = {}
    for route in data["routes"]:
        rid = route.get("id", "?")
        missing = [k for k in REQUIRED_KEYS if k not in route]
        if missing:
            problems.append(f"route {rid}: missing keys {missing}")
            continue
        if rid in seen_ids:
            problems.append(f"route {rid}: duplicate id")
        seen_ids.add(rid)
        for skill in route["primary"] + route["support"]:
            if skill in external:
                continue
            if skill not in checked:
                checked[skill] = skill_exists(skill)
            if not checked[skill]:
                problems.append(f"route {rid}: skill not found on disk: {skill}")
    for problem in problems:
        print(f"FAIL {problem}")
    print(f"{len(data['routes'])} routes, {len(checked)} skills checked, "
          f"{len(problems)} problem(s)")
    return 1 if problems else 0


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if argv[:1] == ["--check"]:
        return check_main()
    if argv[:1] == ["--explain"]:
        print(route_prompt(" ".join(argv[1:])) or "(no route matched)")
        return 0
    hook_main()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
