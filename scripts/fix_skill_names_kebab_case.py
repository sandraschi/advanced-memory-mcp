#!/usr/bin/env python3
"""Fix skill names to kebab-case format."""

from pathlib import Path
import re


def to_kebab_case(text):
    """Convert text to kebab-case."""
    # Remove special characters except spaces and hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces with hyphens
    text = text.replace(' ', '-')
    # Convert to lowercase
    text = text.lower()
    # Remove multiple hyphens
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def fix_skill_name(skill_path):
    """Fix skill name in YAML frontmatter."""
    skill_md = skill_path / "SKILL.md"
    
    if not skill_md.exists():
        return None
    
    content = skill_md.read_text(encoding="utf-8")
    
    # Extract current name
    name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
    if not name_match:
        return None
    
    current_name = name_match.group(1).strip()
    
    # Convert to kebab-case
    kebab_name = to_kebab_case(current_name)
    
    # If it's the same, skip
    if current_name == kebab_name:
        return None
    
    # Replace the name
    new_content = re.sub(
        r'^name:\s*.+$',
        f'name: {kebab_name}',
        content,
        count=1,
        flags=re.MULTILINE
    )
    
    skill_md.write_text(new_content, encoding="utf-8")
    return (current_name, kebab_name)


def main():
    """Fix all skill names."""
    skills_base = Path("skills")
    claude_base = Path(r"C:\Users\sandr\.claude\skills")
    
    total = 0
    fixed = 0
    changes = []
    
    print("\n🔧 Converting all skill names to kebab-case...\n")
    
    for category_dir in skills_base.iterdir():
        if not category_dir.is_dir() or category_dir.name == 'spanish-cooking':
            continue
            
        print(f"📁 {category_dir.name}")
        
        for skill_dir in category_dir.iterdir():
            if not skill_dir.is_dir():
                continue
                
            total += 1
            
            # Fix in both locations
            result = fix_skill_name(skill_dir)
            if result:
                fixed += 1
                changes.append((skill_dir.name, result[0], result[1]))
                
                # Also fix in Claude directory
                claude_skill = claude_base / category_dir.name / skill_dir.name
                if claude_skill.exists():
                    fix_skill_name(claude_skill)
    
    print(f"\n✅ Fixed {fixed}/{total} skills!")
    
    if changes:
        print(f"\n📋 Changed names:")
        for folder, old, new in changes[:10]:  # Show first 10
            print(f"  {old} → {new}")
        if len(changes) > 10:
            print(f"  ... and {len(changes) - 10} more")
    
    # Re-create ZIPs
    print("\n🗜️  Re-zipping all skills with corrected names...")
    
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
    print("\n🎯 All skill names now in kebab-case format!")
    print("   (lowercase-letters-with-hyphens)")


if __name__ == "__main__":
    main()

