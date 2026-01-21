# Skill Standards

## Overview

Advanced Memory MCP establishes comprehensive standards for Claude Skills to ensure quality, consistency, and interoperability across IDE environments. These standards define the format, structure, content requirements, and maintenance procedures for skills.

## Core Standards

### 1. File Format Standards

#### SKILL.md Structure
All skills must follow this exact structure:

```markdown
---
name: "Skill Title"
description: "Brief description of what this skill does"
tags: "tag1, tag2, tag3"
created: "2026-01-21T10:00:00.000Z"
modified: "2026-01-21T10:00:00.000Z"
---

# Skill Content

Detailed instructions and guidance...

## Usage Examples

## Best Practices
```

#### Required Frontmatter Fields
- **name**: Skill title (required, string)
- **description**: Brief description (required, string, max 200 chars)
- **tags**: Comma-separated tags (required, string)
- **created**: ISO 8601 timestamp (required, string)
- **modified**: ISO 8601 timestamp (required, string)

#### Optional Frontmatter Fields
- **version**: Semantic version (string)
- **author**: Creator name (string)
- **license**: License type (string)
- **compatibility**: Supported IDEs (string)

### 2. Directory Structure Standards

#### Basic Structure
```
skill-directory/
├── SKILL.md          # Required: Main skill file
├── modules/          # Optional: Submodules
├── assets/           # Optional: Supporting files
├── references/       # Optional: External references
└── scripts/          # Optional: Automation scripts
```

#### Naming Conventions
- **Directory**: kebab-case, descriptive names
- **Files**: PascalCase for main files, camelCase for submodules
- **Assets**: descriptive names with extensions

### 3. Content Standards

#### Title Standards
- Clear and descriptive
- Action-oriented when possible
- Consistent capitalization (Title Case)
- Under 50 characters

#### Description Standards
- Complete sentence
- Under 200 characters
- Explains what the skill does
- Includes target use case

#### Tag Standards
- Lowercase, hyphen-separated
- Relevant to skill content
- Maximum 5 tags per skill
- Consistent vocabulary

#### Content Standards
- **Structure**: Clear headings and sections
- **Instructions**: Step-by-step when applicable
- **Examples**: Practical usage scenarios
- **Troubleshooting**: Common issues and solutions

## Quality Standards

### Content Quality
- **Accuracy**: Information must be correct and current
- **Completeness**: Covers all aspects of the topic
- **Clarity**: Easy to understand and follow
- **Practicality**: Real-world applicable

### Technical Quality
- **Formatting**: Valid YAML frontmatter
- **Parsing**: Compatible with ADN parsers
- **Compatibility**: Works across all supported IDEs
- **Performance**: Efficient loading and parsing

### Maintenance Standards
- **Updates**: Regular content updates (quarterly minimum)
- **Versioning**: Semantic versioning for major changes
- **Deprecation**: Clear deprecation notices
- **Archival**: Proper archiving of retired skills

## Skill Categories

### Technical Skills
- **Languages**: Programming languages and syntax
- **Frameworks**: Libraries, platforms, and tools
- **DevOps**: CI/CD, deployment, monitoring
- **Security**: Best practices and tools
- **Performance**: Optimization and profiling

### Creative Skills
- **Writing**: Content creation, editing, style guides
- **Design**: Visual design, UX/UI principles
- **Multimedia**: Audio, video, graphics production
- **Strategy**: Planning, analysis, optimization

### Business Skills
- **Management**: Project management, leadership
- **Analysis**: Data analysis, reporting, insights
- **Operations**: Process optimization, automation
- **Strategy**: Business planning, market analysis

### Domain Skills
- **Science**: Research methods, analysis techniques
- **Education**: Teaching methods, curriculum design
- **Healthcare**: Medical knowledge, patient care
- **Industry**: Specialized industry knowledge

## Validation Standards

### Automated Validation
- **YAML Syntax**: Valid frontmatter parsing
- **Required Fields**: All mandatory fields present
- **Data Types**: Correct field types and formats
- **File Structure**: Proper directory organization

### Manual Review
- **Content Accuracy**: Technical review by experts
- **Clarity Assessment**: Readability and comprehension
- **Completeness Check**: Coverage of topic areas
- **Practicality Review**: Real-world applicability

### Continuous Validation
- **Parsing Tests**: Regular parsing verification
- **Compatibility Tests**: Cross-IDE functionality
- **Performance Tests**: Loading and search performance
- **Freshness Checks**: Content currency validation

## Distribution Standards

### Directory Locations
- **ADN Skills**: `D:\Dev\repos\advanced-memory-mcp\skills`
- **Cursor Skills**: `C:\Users\[username]\.cursor\skills-cursor`
- **Windsurf Skills**: `C:\Users\[username]\.codeium\windsurf\skills`
- **Antigravity Skills**: `C:\Users\[username]\.gemini\antigravity\skills`

### Distribution Process
1. **Validation**: Pass all automated checks
2. **Review**: Manual quality review
3. **Packaging**: Proper file structure
4. **Deployment**: Copy to target directories
5. **Registration**: Update skill registries

## Maintenance Standards

### Update Frequency
- **Critical Skills**: Monthly updates
- **Technical Skills**: Quarterly updates
- **General Skills**: Bi-annual updates
- **Archive Skills**: Annual review

### Version Control
- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **Changelog**: Update history tracking
- **Breaking Changes**: Major version increments
- **Deprecation**: Clear migration paths

### Retirement Process
1. **Deprecation Notice**: 30-day warning
2. **Alternative Skills**: Recommended replacements
3. **Archive Storage**: Preserved for reference
4. **Registry Update**: Removal from active lists

## Compliance Standards

### ADN Compliance
- **Parser Compatibility**: Works with ADN parsers
- **Webapp Integration**: Displays in ADN webapp
- **Search Integration**: Indexed for search
- **API Compatibility**: Works with ADN APIs

### IDE Compliance
- **Cursor Integration**: Compatible with Cursor IDE
- **Windsurf Integration**: Works with Windsurf IDE
- **Antigravity Integration**: Compatible with Antigravity IDE
- **Cross-Platform**: Windows, macOS, Linux support

### Community Standards
- **Open Source**: Skills available for community use
- **Attribution**: Proper credit for contributions
- **Collaboration**: Community contribution guidelines
- **Feedback**: User feedback integration

## Advanced Standards

### Submodule Standards
- **Naming**: Descriptive, consistent naming
- **Purpose**: Clear purpose and scope
- **Integration**: Proper linking from main skill
- **Maintenance**: Updated with main skill

### Asset Standards
- **Formats**: Standard web-compatible formats
- **Size Limits**: Reasonable file sizes
- **Organization**: Logical directory structure
- **Documentation**: Asset usage documentation

### Reference Standards
- **Citation**: Proper citation formats
- **Accessibility**: Links must be accessible
- **Currency**: References kept current
- **Relevance**: References must be relevant

## Enforcement

### Validation Tools
- **ADN Validators**: Automated skill validation
- **IDE Checkers**: IDE-specific compatibility tests
- **Community Tools**: Open source validation tools
- **CI/CD Integration**: Automated validation pipelines

### Compliance Monitoring
- **Regular Audits**: Periodic standards compliance checks
- **Issue Tracking**: Standards violation reporting
- **Remediation**: Required fixes for violations
- **Appeals Process**: Dispute resolution for standards decisions

### Incentives
- **Quality Badges**: Recognition for high-quality skills
- **Featured Skills**: Highlighting compliant skills
- **Community Recognition**: Awards for standards excellence
- **Priority Support**: Faster issue resolution for compliant skills

## Future Standards

### Planned Enhancements
- **Schema Validation**: JSON Schema for skill validation
- **Skill Dependencies**: Dependency management system
- **Skill Testing**: Automated skill testing frameworks
- **Skill Analytics**: Usage and effectiveness metrics

### Evolving Standards
- **Community Input**: Standards evolution based on feedback
- **Technology Updates**: Adaptation to new technologies
- **Research Integration**: Incorporation of research findings
- **Industry Best Practices**: Alignment with industry standards

## Conclusion

Skill standards ensure that ADN skills maintain high quality, consistency, and interoperability across all supported environments. These standards evolve with technology and community needs while maintaining backward compatibility and reliability.

For questions about skill standards or assistance with compliance, refer to the ADN webapp help system or consult the skill parsing architecture documentation.