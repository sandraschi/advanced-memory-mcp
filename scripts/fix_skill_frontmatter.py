#!/usr/bin/env python3
"""Fix YAML frontmatter in all skills to match Claude's expected format."""

from pathlib import Path
import re


def fix_frontmatter(skill_path):
    """Fix YAML frontmatter to only include name and description."""
    skill_md = skill_path / "SKILL.md"
    
    if not skill_md.exists():
        return False
    
    content = skill_md.read_text(encoding="utf-8")
    
    # Extract name and description from existing frontmatter
    name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
    desc_match = re.search(r'^description:\s*(.+)$', content, re.MULTILINE)
    
    if not name_match or not desc_match:
        print(f"  ⚠️  Could not find name/description in {skill_path.name}")
        return False
    
    name = name_match.group(1).strip()
    description = desc_match.group(1).strip()
    
    # Remove old frontmatter and get body
    body_match = re.search(r'^---\s*\n.*?\n---\s*\n(.+)$', content, re.DOTALL)
    if not body_match:
        print(f"  ⚠️  Could not parse frontmatter in {skill_path.name}")
        return False
    
    body = body_match.group(1).strip()
    
    # Create new minimal frontmatter
    new_content = f"""---
name: {name}
description: {description}
---

{body}
"""
    
    skill_md.write_text(new_content, encoding="utf-8")
    return True


def main():
    """Fix all skills."""
    skills_base = Path("skills")
    claude_base = Path(r"C:\Users\sandr\.claude\skills")
    
    total = 0
    fixed = 0
    
    print("\n🔧 Fixing YAML frontmatter in all skills...\n")
    
    for category_dir in skills_base.iterdir():
        if not category_dir.is_dir():
            continue
            
        print(f"📁 {category_dir.name}")
        
        for skill_dir in category_dir.iterdir():
            if not skill_dir.is_dir():
                continue
                
            total += 1
            
            # Fix in both locations
            if fix_frontmatter(skill_dir):
                fixed += 1
                
                # Also fix in Claude directory if it exists
                claude_skill = claude_base / category_dir.name / skill_dir.name
                if claude_skill.exists():
                    fix_frontmatter(claude_skill)
                
                if fixed % 20 == 0:
                    print(f"  ✅ {fixed} skills fixed...")
    
    print(f"\n✅ Fixed {fixed}/{total} skills!")
    print(f"\n📋 Minimal frontmatter now:")
    print("---")
    print("name: skill-name")
    print("description: What this skill does")
    print("---")
    print("\n🗜️  Now re-zipping all skills...")
    
    # Re-create ZIPs
    zip_dir = Path("skill-zips")
    if zip_dir.exists():
        import shutil
        shutil.rmtree(zip_dir)
    zip_dir.mkdir()
    
    import zipfile
    
    zip_count = 0
    for category_dir in skills_base.iterdir():
        if not category_dir.is_dir():
            continue
            
        for skill_dir in category_dir.iterdir():
            if not skill_dir.is_dir():
                continue
                
            zip_path = zip_dir / f"{skill_dir.name}.zip"
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in skill_dir.rglob('*'):
                    if file.is_file():
                        arcname = file.relative_to(skill_dir.parent)
                        zipf.write(file, arcname)
            
            zip_count += 1
            if zip_count % 20 == 0:
                print(f"  ✅ {zip_count} ZIPs created...")
    
    print(f"\n✅ Created {zip_count} fresh ZIP files!")
    print(f"📁 Location: {zip_dir.absolute()}")
    print("\n🎯 Ready for upload to Claude.ai!")


if __name__ == "__main__":
    main()

