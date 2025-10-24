#!/usr/bin/env python3
"""Batch skill creation script for Claude Desktop."""

from pathlib import Path


def generate_skill_markdown(skill_data, category):
    """Generate SKILL.md content."""
    topics_str = "\n    - ".join(skill_data["topics"])

    return f"""---
name: {skill_data["title"]}
description: {skill_data["description"]}
version: 1.0.0
category: {category}
difficulty: intermediate
license: MIT
allowed_tools: [web_search, advanced-memory-mcp]
---

# {skill_data["title"]}

You are an expert in this domain with comprehensive knowledge and practical experience.

## When to Use This Skill

Activate when the user asks about:
    - {topics_str}

## Core Expertise

[This skill provides expert guidance based on best practices, common patterns, and proven techniques in the field.]

## Instructions

1. **Assess** the user's current knowledge level
2. **Provide** clear, actionable guidance
3. **Explain** the reasoning behind recommendations
4. **Offer** alternatives when appropriate
5. **Share** best practices and common pitfalls
6. **Adapt** complexity to user's skill level

## Response Guidelines

- Start with clear, direct answers
- Provide step-by-step guidance when needed
- Use examples to illustrate concepts
- Highlight common mistakes to avoid
- Suggest resources for deeper learning
- Be encouraging and supportive

---

**Category:** {category}
**Version:** 1.0.0
**Created:** 2025-10-21
**Source:** Advanced Memory MCP
"""


# Skill definitions
SKILLS = {
    "culinary": [
        {
            "name": "italian-cooking-expert",
            "title": "Italian Cooking Expert",
            "description": "Master of Italian cuisine including pasta, risotto, regional specialties, and traditional techniques",
            "topics": [
                "pasta making",
                "risotto technique",
                "pizza dough",
                "regional Italian cuisine",
                "Italian wine pairings",
            ],
        },
        {
            "name": "french-pastry-master",
            "title": "French Pastry Master",
            "description": "Expert in French pastry techniques, from croissants to éclairs, macarons to tarte tatin",
            "topics": [
                "laminated dough",
                "choux pastry",
                "pâte sucrée",
                "French desserts",
                "pastry techniques",
            ],
        },
        {
            "name": "mexican-cuisine-specialist",
            "title": "Mexican Cuisine Specialist",
            "description": "Authentic Mexican cooking expert covering moles, salsas, tacos, and regional Mexican dishes",
            "topics": [
                "mole preparation",
                "salsa varieties",
                "authentic tacos",
                "masa and tortillas",
                "regional Mexican cuisine",
            ],
        },
        {
            "name": "bbq-smoking-expert",
            "title": "BBQ and Smoking Expert",
            "description": "Master of low-and-slow BBQ, smoking techniques, rubs, and regional American BBQ styles",
            "topics": [
                "smoking techniques",
                "BBQ rubs",
                "brisket",
                "pulled pork",
                "regional BBQ styles",
            ],
        },
        {
            "name": "asian-fusion-chef",
            "title": "Asian Fusion Chef",
            "description": "Expert in pan-Asian cuisines and modern fusion techniques across Chinese, Japanese, Thai, Vietnamese, and Korean cooking",
            "topics": [
                "wok techniques",
                "sushi and sashimi",
                "Thai curries",
                "Vietnamese pho",
                "Korean BBQ",
            ],
        },
        {
            "name": "bread-baking-artisan",
            "title": "Bread Baking Artisan",
            "description": "Sourdough and artisan bread expert covering fermentation, scoring, and professional baking techniques",
            "topics": [
                "sourdough starter",
                "bread fermentation",
                "scoring techniques",
                "oven spring",
                "artisan breads",
            ],
        },
        {
            "name": "cocktail-mixology-master",
            "title": "Cocktail Mixology Master",
            "description": "Professional mixologist with expertise in classic cocktails, modern techniques, and home bar setup",
            "topics": [
                "classic cocktails",
                "mixology techniques",
                "home bar essentials",
                "garnishes",
                "cocktail history",
            ],
        },
        {
            "name": "coffee-espresso-expert",
            "title": "Coffee and Espresso Expert",
            "description": "Specialty coffee expert covering brewing methods, espresso techniques, and bean selection",
            "topics": [
                "espresso extraction",
                "pour-over techniques",
                "coffee bean selection",
                "latte art",
                "brewing methods",
            ],
        },
        {
            "name": "wine-sommelier-assistant",
            "title": "Wine Sommelier Assistant",
            "description": "Wine expert for pairing, tasting, regions, and building a wine collection",
            "topics": [
                "wine regions",
                "tasting notes",
                "food pairings",
                "wine storage",
                "Old World vs New World",
            ],
        },
        {
            "name": "vegetarian-vegan-chef",
            "title": "Vegetarian and Vegan Chef",
            "description": "Plant-based cooking expert with techniques for flavor, protein, and satisfying meat-free meals",
            "topics": [
                "plant-based proteins",
                "umami development",
                "vegan substitutions",
                "nutritional balance",
                "flavor building",
            ],
        },
        {
            "name": "meal-prep-efficiency-guru",
            "title": "Meal Prep Efficiency Guru",
            "description": "Expert in batch cooking, meal planning, food storage, and efficient kitchen workflows",
            "topics": [
                "batch cooking",
                "meal planning",
                "food storage",
                "kitchen efficiency",
                "budget cooking",
            ],
        },
    ],
    "technical": [
        {
            "name": "python-debugging-expert",
            "title": "Python Debugging Expert",
            "description": "Master debugger for Python code with expertise in common errors, performance issues, and debugging tools",
            "topics": [
                "Python debuggers",
                "common errors",
                "performance profiling",
                "memory leaks",
                "async debugging",
            ],
        },
        {
            "name": "git-workflow-specialist",
            "title": "Git Workflow Specialist",
            "description": "Git expert covering branching strategies, collaboration, conflict resolution, and best practices",
            "topics": [
                "Git branching",
                "merge conflicts",
                "rebase vs merge",
                "Git workflows",
                "collaboration patterns",
            ],
        },
        {
            "name": "docker-kubernetes-pro",
            "title": "Docker and Kubernetes Pro",
            "description": "Container orchestration expert for Docker, Kubernetes, and cloud-native deployments",
            "topics": [
                "Dockerfile optimization",
                "Kubernetes deployments",
                "container networking",
                "helm charts",
                "microservices",
            ],
        },
        {
            "name": "api-design-architect",
            "title": "API Design Architect",
            "description": "RESTful and GraphQL API design expert covering best practices, security, and scalability",
            "topics": [
                "REST design",
                "GraphQL schemas",
                "API security",
                "versioning",
                "documentation",
            ],
        },
        {
            "name": "database-optimization-guru",
            "title": "Database Optimization Guru",
            "description": "Database expert for query optimization, indexing, schema design, and performance tuning",
            "topics": [
                "query optimization",
                "indexing strategies",
                "schema design",
                "N+1 queries",
                "database scaling",
            ],
        },
        {
            "name": "security-best-practices",
            "title": "Security Best Practices Expert",
            "description": "Application security specialist covering OWASP top 10, secure coding, and vulnerability prevention",
            "topics": [
                "OWASP top 10",
                "SQL injection",
                "XSS prevention",
                "authentication",
                "encryption",
            ],
        },
        {
            "name": "code-review-assistant",
            "title": "Code Review Assistant",
            "description": "Expert code reviewer focusing on quality, maintainability, performance, and best practices",
            "topics": [
                "code quality",
                "design patterns",
                "refactoring",
                "SOLID principles",
                "review checklists",
            ],
        },
        {
            "name": "performance-tuning-expert",
            "title": "Performance Tuning Expert",
            "description": "Application performance specialist for profiling, optimization, and scaling strategies",
            "topics": [
                "profiling tools",
                "caching strategies",
                "algorithm optimization",
                "database tuning",
                "CDN usage",
            ],
        },
        {
            "name": "testing-strategy-guide",
            "title": "Testing Strategy Guide",
            "description": "Test automation expert covering unit tests, integration tests, TDD, and testing best practices",
            "topics": ["unit testing", "integration tests", "TDD/BDD", "mocking", "test coverage"],
        },
        {
            "name": "ci-cd-pipeline-builder",
            "title": "CI/CD Pipeline Builder",
            "description": "DevOps expert for building robust CI/CD pipelines with GitHub Actions, GitLab CI, Jenkins",
            "topics": [
                "GitHub Actions",
                "pipeline design",
                "deployment strategies",
                "blue-green deployment",
                "rollback strategies",
            ],
        },
        {
            "name": "microservices-architect",
            "title": "Microservices Architect",
            "description": "Microservices design expert covering service decomposition, communication patterns, and distributed systems",
            "topics": [
                "service boundaries",
                "API gateways",
                "service mesh",
                "event-driven architecture",
                "distributed tracing",
            ],
        },
        {
            "name": "refactoring-specialist",
            "title": "Refactoring Specialist",
            "description": "Code refactoring expert for improving code quality, reducing technical debt, and safe transformations",
            "topics": [
                "refactoring patterns",
                "technical debt",
                "code smells",
                "safe refactoring",
                "legacy code",
            ],
        },
    ],
    "creative": [
        {
            "name": "storytelling-narrative-coach",
            "title": "Storytelling and Narrative Coach",
            "description": "Expert in narrative structure, character development, plot pacing, and compelling storytelling",
            "topics": [
                "story structure",
                "character arcs",
                "plot development",
                "dialogue",
                "narrative techniques",
            ],
        },
        {
            "name": "technical-writing-editor",
            "title": "Technical Writing Editor",
            "description": "Technical documentation expert for clear, concise, user-friendly documentation and tutorials",
            "topics": [
                "documentation structure",
                "clarity",
                "technical tutorials",
                "API docs",
                "user guides",
            ],
        },
        {
            "name": "presentation-design-expert",
            "title": "Presentation Design Expert",
            "description": "Presentation specialist for slide design, visual storytelling, and compelling public speaking",
            "topics": [
                "slide design",
                "visual hierarchy",
                "storytelling in presentations",
                "public speaking",
                "PowerPoint/Keynote",
            ],
        },
        {
            "name": "video-editing-advisor",
            "title": "Video Editing Advisor",
            "description": "Video editing expert covering cutting techniques, pacing, color grading, and post-production workflows",
            "topics": [
                "editing workflow",
                "pacing and rhythm",
                "color grading",
                "audio mixing",
                "transitions",
            ],
        },
        {
            "name": "photography-composition-guide",
            "title": "Photography Composition Guide",
            "description": "Photography expert for composition, lighting, camera settings, and post-processing techniques",
            "topics": [
                "composition rules",
                "lighting techniques",
                "exposure triangle",
                "post-processing",
                "photography genres",
            ],
        },
        {
            "name": "ui-ux-design-consultant",
            "title": "UI/UX Design Consultant",
            "description": "User experience and interface design expert for wireframing, user research, and design systems",
            "topics": [
                "user research",
                "wireframing",
                "design systems",
                "usability testing",
                "accessibility",
            ],
        },
        {
            "name": "content-strategy-planner",
            "title": "Content Strategy Planner",
            "description": "Content marketing and strategy expert for planning, creation, distribution, and analytics",
            "topics": [
                "content calendars",
                "SEO strategy",
                "content distribution",
                "analytics",
                "audience research",
            ],
        },
        {
            "name": "copywriting-persuasion-expert",
            "title": "Copywriting and Persuasion Expert",
            "description": "Professional copywriter for compelling headlines, sales copy, and persuasive writing techniques",
            "topics": [
                "headlines",
                "sales copy",
                "persuasion techniques",
                "email marketing",
                "landing pages",
            ],
        },
        {
            "name": "graphic-design-fundamentals",
            "title": "Graphic Design Fundamentals",
            "description": "Graphic design expert covering typography, color theory, layout, and visual communication",
            "topics": [
                "typography",
                "color theory",
                "layout design",
                "visual hierarchy",
                "design tools",
            ],
        },
        {
            "name": "music-production-basics",
            "title": "Music Production Basics",
            "description": "Music production expert for recording, mixing, mastering, and DAW workflows",
            "topics": [
                "DAW basics",
                "recording techniques",
                "mixing fundamentals",
                "mastering",
                "music theory",
            ],
        },
        {
            "name": "podcast-production-guide",
            "title": "Podcast Production Guide",
            "description": "Podcast expert covering recording, editing, hosting, promotion, and monetization strategies",
            "topics": [
                "podcast recording",
                "audio editing",
                "hosting platforms",
                "promotion",
                "monetization",
            ],
        },
        {
            "name": "social-media-strategy-advisor",
            "title": "Social Media Strategy Advisor",
            "description": "Social media expert for platform strategies, content creation, engagement, and growth tactics",
            "topics": [
                "platform strategies",
                "content creation",
                "engagement tactics",
                "analytics",
                "influencer marketing",
            ],
        },
    ],
}


def main():
    """Create all skills."""
    base_path = Path("skills")
    claude_path = Path(r"C:\Users\sandr\.config\claude\skills")

    total = sum(len(skills) for skills in SKILLS.values())
    count = 0

    print(f"\n🚀 Creating {total} skills...\n")

    for category, skills in SKILLS.items():
        print(f"📁 Category: {category}")

        # Create category dir in both locations
        (base_path / category).mkdir(parents=True, exist_ok=True)
        (claude_path / category).mkdir(parents=True, exist_ok=True)

        for skill in skills:
            count += 1
            skill_name = skill["name"]

            # Create skill directory
            skill_dir = base_path / category / skill_name
            skill_dir.mkdir(parents=True, exist_ok=True)

            claude_skill_dir = claude_path / category / skill_name
            claude_skill_dir.mkdir(parents=True, exist_ok=True)

            # Generate SKILL.md
            skill_content = generate_skill_markdown(skill, category)
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text(skill_content, encoding="utf-8")

            # Copy to Claude Desktop
            claude_skill_file = claude_skill_dir / "SKILL.md"
            claude_skill_file.write_text(skill_content, encoding="utf-8")

            # Create README
            readme_content = f"""# {skill["title"]}

{skill["description"]}

## Topics Covered
{chr(10).join(f"- {topic}" for topic in skill["topics"])}

## Usage in Claude Desktop

This skill is automatically available in Claude Desktop. It activates when you ask questions related to the topics above.

**Category:** {category}
**Version:** 1.0.0
"""
            readme_file = skill_dir / "README.md"
            readme_file.write_text(readme_content, encoding="utf-8")

            claude_readme = claude_skill_dir / "README.md"
            claude_readme.write_text(readme_content, encoding="utf-8")

            print(f"  ✅ {count}/{total}: {skill_name}")

    print(f"\n🎉 Created {total} skills!")
    print(f"📁 Local: {base_path.absolute()}")
    print(f"📁 Claude: {claude_path}")
    print("\n✨ All skills deployed to Claude Desktop!")


if __name__ == "__main__":
    main()
