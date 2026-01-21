# Skill Discovery Guide

## Overview

Advanced Memory MCP provides powerful tools for discovering and accessing skills across multiple IDE environments. This guide covers skill search, filtering, browsing, and integration with your workflow.

## Skill Discovery Methods

### 1. Webapp Interface

#### Skills Dashboard
Access the Skills page in the ADN webapp to:
- Browse skills by IDE source
- Search across all skills
- Filter by tags and categories
- View skill details and content

#### Folder Selection
Choose from skill sources:
- **ADN Skills**: Core skill collection
- **Cursor Skills**: IDE-specific skills
- **Windsurf Skills**: Windsurf IDE skills
- **Antigravity Skills**: Antigravity IDE skills

### 2. IDE Integration

#### Cursor IDE
Skills are automatically available when using ADN MCP in Cursor:
- Skills loaded from `C:\Users\[username]\.cursor\skills-cursor`
- Integrated into Claude chat interface
- Context-aware skill suggestions

#### Windsurf IDE
Skills accessible through Windsurf's ADN integration:
- Skills from `C:\Users\[username]\.codeium\windsurf\skills`
- Workflow integration
- Real-time skill updates

#### Antigravity IDE
Skills for advanced AI workflows:
- Located in `C:\Users\[username]\.gemini\antigravity\skills`
- Specialized for complex tasks
- Enhanced context processing

### 3. ADN MCP Tools

#### Skill Search Tools
- `adn_find_skill`: Search skills by keyword
- `adn_browse_skills`: Browse skills by category
- `adn_recommend_skill`: Get skill recommendations
- `adn_skill_details`: View detailed skill information

## Search and Filtering

### Basic Search
- **Text Search**: Search skill titles, descriptions, and content
- **Tag Filtering**: Filter by skill tags
- **Category Filtering**: Browse by skill categories

### Advanced Filtering
- **Date Range**: Filter by creation or modification date
- **Author/Source**: Filter by skill origin
- **Complexity Level**: Filter by skill difficulty
- **Usage Statistics**: Filter by popularity

### Search Syntax
```
# Basic search
"python development"

# Tag filtering
tag:python tag:web-development

# Category filtering
category:technical

# Date filtering
created:2026-01 modified:2026-01-15

# Combined search
"machine learning" tag:python created:2026
```

## Skill Categories

### Technical Skills
- **Programming**: Languages, frameworks, tools
- **DevOps**: CI/CD, deployment, monitoring
- **Security**: Best practices, tools, compliance
- **Performance**: Optimization, profiling, scaling

### Creative Skills
- **Content Creation**: Writing, design, multimedia
- **Strategy**: Planning, analysis, optimization
- **Communication**: Presentation, documentation
- **Innovation**: Research, prototyping

### Business Skills
- **Management**: Project management, team leadership
- **Analysis**: Data analysis, reporting, insights
- **Operations**: Process optimization, automation
- **Strategy**: Business planning, market analysis

### Domain Skills
- **Science**: Research methods, analysis techniques
- **Education**: Teaching methods, curriculum design
- **Healthcare**: Medical knowledge, patient care
- **Legal**: Compliance, contracts, regulations

## Skill Quality Assessment

### Quality Indicators
- **Rating**: User-rated quality score
- **Usage Count**: Number of times skill has been used
- **Last Updated**: How recently the skill was maintained
- **Completeness**: Coverage of topic areas

### Reliability Metrics
- **Success Rate**: Percentage of successful applications
- **User Feedback**: Reviews and comments
- **Error Reports**: Known issues or limitations
- **Compatibility**: IDE and environment support

### Freshness Indicators
- **Update Frequency**: How often skill is updated
- **Version History**: Change tracking
- **Deprecation Notices**: Outdated skill warnings
- **Alternative Recommendations**: Better alternatives

## Skill Integration

### Workflow Integration
- **Context Awareness**: Skills suggested based on current task
- **One-Click Application**: Easy skill activation
- **Workflow Templates**: Pre-configured skill combinations
- **Automation**: Skill-based workflow automation

### Cross-Platform Access
- **Webapp Access**: Browser-based skill management
- **IDE Integration**: Native IDE skill support
- **API Access**: Programmatic skill access
- **Sharing**: Skill distribution across environments

## Advanced Discovery Features

### Skill Networks
- **Related Skills**: Skills that work well together
- **Prerequisite Skills**: Required foundational knowledge
- **Follow-up Skills**: Next steps after current skill
- **Alternative Approaches**: Different ways to solve problems

### Personalized Recommendations
- **Usage History**: Skills recommended based on past usage
- **Skill Gaps**: Missing skills identified for workflows
- **Learning Paths**: Skill progression recommendations
- **Team Collaboration**: Shared skill recommendations

### Smart Search
- **Semantic Search**: Understanding of skill intent
- **Context Matching**: Skills matching current work context
- **Task Analysis**: Automatic task-to-skill mapping
- **Expertise Matching**: Skills matching user skill level

## Skill Management

### Organization
- **Collections**: Group related skills
- **Favorites**: Mark frequently used skills
- **Custom Categories**: Create personal skill categories
- **Tags**: Flexible skill organization

### Maintenance
- **Updates**: Automatic skill update notifications
- **Validation**: Skill integrity checking
- **Backup**: Skill collection backup
- **Sync**: Skill synchronization across devices

## Troubleshooting

### Common Issues

#### Skills Not Loading
- Check skill directory permissions
- Verify SKILL.md file format
- Check YAML frontmatter syntax
- Ensure directory structure is correct

#### Search Not Working
- Clear search cache
- Check search syntax
- Verify skill indexing
- Update search filters

#### Integration Problems
- Check IDE plugin versions
- Verify MCP server connection
- Update skill definitions
- Check compatibility requirements

### Performance Optimization
- **Caching**: Skill content caching for faster access
- **Indexing**: Optimized search indexing
- **Lazy Loading**: On-demand skill content loading
- **Background Updates**: Non-blocking skill updates

## Best Practices

### Effective Discovery
- Use specific search terms
- Combine filters for precision
- Check skill ratings and reviews
- Consider skill freshness

### Skill Evaluation
- Read skill descriptions carefully
- Check usage examples
- Review user feedback
- Test skills in your environment

### Organization
- Create personal skill collections
- Use consistent tagging
- Maintain skill documentation
- Share valuable skills with team

## Future Enhancements

### Planned Features
- **AI-Powered Discovery**: Machine learning-based recommendations
- **Skill Analytics**: Usage patterns and effectiveness tracking
- **Collaborative Filtering**: Community-based skill discovery
- **Skill Evolution**: Automatic skill improvement suggestions

### Integration Improvements
- **Unified Search**: Cross-platform skill search
- **Skill Marketplace**: Community skill sharing
- **Skill Dependencies**: Automatic dependency management
- **Skill Versioning**: Version control for skills

## Conclusion

Skill discovery is a core feature of Advanced Memory MCP, enabling users to quickly find and apply the right expertise for their tasks. The multi-environment support ensures skills are accessible wherever you work, while advanced search and filtering capabilities help you find exactly what you need.

For additional support or questions about skill discovery, refer to the ADN webapp help system or consult the skill parsing architecture documentation.