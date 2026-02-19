# Advanced Memory WebApp

A beautiful, dark-themed React web interface for Advanced Memory MCP that provides standalone access to research capabilities without requiring MCP client integration.

## Features

- **Dark Professional Theme**: High-contrast design with gold accents
- **Research Dashboard**: Real-time multi-source research interface
- **Skill Studio**: Interactive skill creation from research findings
- **LLM Management**: Provider discovery, model loading/unloading
- **Zero Crash Design**: Comprehensive error handling and logging
- **Responsive Layout**: Works on desktop, tablet, and mobile

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Architecture

```
webapp/
├── src/
│   ├── components/
│   │   ├── layout/          # Sidebar, Topbar, Modals
│   │   └── ui/              # Reusable UI components
│   ├── pages/
│   │   ├── dashboard/       # Main research interface
│   │   ├── settings/        # LLM and export configuration
│   │   └── help/            # Documentation and guides
│   ├── services/            # ADN API integration
│   ├── utils/               # Helper functions
│   ├── styles/              # CSS and Tailwind config
│   └── types/               # TypeScript definitions
├── public/                  # Static assets
└── dist/                    # Production build output
```

## Key Components

### Layout System
- **Sidebar**: Navigation with collapsible mobile support
- **Topbar**: Status indicators and quick actions
- **Logger Modal**: Real-time application logging
- **Help Modal**: Integrated documentation

### Research Interface
- **Hero Section**: Feature overview and quick actions
- **Research Cards**: Real-time progress tracking
- **Skill Cards**: Generated expertise display
- **System Status**: Provider and service health

### Settings Management
- **LLM Providers**: Automatic detection and configuration
- **Model Management**: Load/unload local models
- **Research Sources**: Enable/disable research providers
- **Export Formats**: Configure output destinations

## Development

### Code Quality
- **ESLint**: Strict linting rules
- **TypeScript**: Full type safety
- **Prettier**: Consistent code formatting
- **Error Boundaries**: Zero crash guarantee

### Styling
- **Tailwind CSS**: Utility-first CSS framework
- **Custom Theme**: Dark palette with gold accents
- **Responsive Design**: Mobile-first approach
- **Performance**: Optimized bundle size

### Error Handling
- **React Error Boundaries**: Application-level crash prevention
- **API Error Handling**: Graceful degradation on service failures
- **User Feedback**: Clear error messages and recovery options
- **Logging**: Comprehensive error tracking and debugging

## Integration

The webapp integrates with Advanced Memory MCP through:

- **HTTP API**: RESTful endpoints for research operations
- **WebSocket**: Real-time progress updates and notifications
- **Local Storage**: Persistent user preferences and settings
- **Service Discovery**: Automatic ADN instance detection

## Deployment

### Development
```bash
npm run dev
# Starts Vite dev server on http://localhost:3000
```

### Production Build
```bash
npm run build
npm run preview
# Serves production build locally for testing
```

### Docker Deployment
```dockerfile
FROM nginx:alpine
COPY dist/ /usr/share/nginx/html/
EXPOSE 80
```

## Browser Support

- **Chrome/Edge**: Full support (recommended)
- **Firefox**: Full support
- **Safari**: Full support
- **Mobile Browsers**: Responsive design support

## Contributing

1. Follow the established code style and patterns
2. Add comprehensive error handling
3. Include TypeScript types for all new features
4. Test on multiple browsers and screen sizes
5. Update documentation for any new features

## License

AGPL-3.0-or-later - See main project LICENSE file.
