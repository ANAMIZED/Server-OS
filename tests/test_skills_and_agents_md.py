"""Validate AGENTS.md and SKILL.md packages."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
AGENTS_MD = ROOT / "AGENTS.md"


def test_agents_md_exists_and_has_contract_markers():
    assert AGENTS_MD.is_file()
    text = AGENTS_MD.read_text()
    assert "verify.sh" in text
    assert "fail-closed" in text.lower() or "Fail closed" in text


def test_skill_packages_present():
    required = ["cost-control", "governance-audit", "deploy-verify", "x402-payments", "multi-agent-workflow"]
    for name in required:
        assert (SKILLS / name / "SKILL.md").is_file()


def test_skill_frontmatter_minimum():
    for skill_dir in SKILLS.iterdir():
        if not skill_dir.is_dir():
            continue
        path = skill_dir / "SKILL.md"
        if not path.is_file():
            continue
        text = path.read_text()
        assert text.startswith("---")
        parts = text.split("---", 2)
        assert len(parts) >= 3
        fm = parts[1]
        assert "name:" in fm
        assert "description:" in fm
