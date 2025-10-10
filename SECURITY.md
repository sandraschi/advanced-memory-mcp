# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          | Status |
| ------- | ------------------ | ------ |
| 1.x.x   | :white_check_mark: | Active development |
| 0.x.x   | :white_check_mark: | Beta releases |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability, please email **hello@basicmachines.co** with:

1. **Description** of the vulnerability
2. **Steps to reproduce** the issue
3. **Potential impact** of the vulnerability
4. **Suggested fix** (if you have one)

### What to Expect

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Critical issues within 14 days, others within 30 days
- **Credit**: We will credit you in the security advisory (unless you prefer to remain anonymous)

## Security Best Practices

### For Users

1. **Keep Updated**: Always use the latest version
2. **Review Permissions**: Understand what file system access the MCP server requires
3. **Secure Credentials**: Never commit credentials or sensitive data to your knowledge base
4. **Project Isolation**: Use separate projects for different sensitivity levels
5. **Backup Regularly**: Use the archive export feature for backups

### For Developers

1. **Input Validation**: All user inputs are validated with Pydantic schemas
2. **Path Traversal**: File operations are restricted to project directories
3. **SQL Injection**: We use SQLAlchemy ORM with parameterized queries
4. **Dependencies**: Regularly updated via Dependabot
5. **Code Scanning**: Automated security scanning with CodeQL

## Security Features

### Current Protections

- ✅ **Path Validation**: Prevents directory traversal attacks
- ✅ **Input Sanitization**: Pydantic validation on all inputs
- ✅ **Project Isolation**: Database and file system separation per project
- ✅ **Safe Defaults**: Restrictive permissions by default
- ✅ **Audit Logging**: All operations logged with Loguru
- ✅ **Dependency Scanning**: Automated vulnerability detection

### Known Limitations

- Local file system access required for operation
- SQLite database files must be readable/writable
- No built-in encryption for data at rest (use OS-level encryption)
- Network access required for import/export from external services

## Security Advisories

Security advisories will be published on:
- [GitHub Security Advisories](https://github.com/basicmachines-co/advanced-memory-mcp/security/advisories)
- Project CHANGELOG.md with `[Security]` tag

## Vulnerability Disclosure Timeline

1. **Day 0**: Vulnerability reported
2. **Day 2**: Initial response and acknowledgment
3. **Day 7**: Status update and severity assessment
4. **Day 14-30**: Fix developed and tested
5. **Fix Release**: Security patch released
6. **+7 Days**: Public disclosure after users have time to update

## Security Hall of Fame

We appreciate security researchers who help keep Advanced Memory secure. Contributors will be listed here (with permission):

_No vulnerabilities reported yet_

## Contact

- **Security Issues**: hello@basicmachines.co
- **General Issues**: [GitHub Issues](https://github.com/basicmachines-co/advanced-memory-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/basicmachines-co/advanced-memory-mcp/discussions)

---

**Last Updated**: October 9, 2025  
**Policy Version**: 1.0
