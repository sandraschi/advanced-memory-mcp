#!/usr/bin/env python3
"""Test FastMCP features"""

from fastmcp import FastMCP

# Check if multiline descriptions work
server = FastMCP('test')

@server.tool(description='''This is a multiline
description that spans
multiple lines.''')
def test_tool():
    return 'test'

# Check the tool registration
tools = server.get_tools()
if tools:
    tool = tools[0]
    desc = tool.description or ''
    print(f'Tool name: {tool.name}')
    print(f'Description length: {len(desc)}')
    print(f'Description contains newlines: {"\\n" in desc}')
    print(f'Description preview: {desc[:100]}...')
    print(f'Full description:')
    print(repr(desc))
else:
    print('No tools registered')
