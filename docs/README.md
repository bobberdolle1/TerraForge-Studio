# RealWorldMapGen-BNG Documentation

Complete documentation for the RealWorldMapGen-BNG project.

## 📚 Documentation Index

### Getting Started
- **[Installation Guide](INSTALLATION.md)** - Complete setup instructions for Windows, Linux, and Mac
  - Prerequisites and dependencies
  - Quick start with setup scripts
  - Manual installation steps
  - Troubleshooting common issues

### API Reference
- **[API Examples](API_EXAMPLES.md)** - Comprehensive API usage guide
  - Health check endpoints
  - Map generation examples
  - File download endpoints
  - Batch processing
  - Task management

### Development
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project
  - Development setup
  - Code style guidelines
  - Pull request process
  - Issue reporting

## 🚀 Quick Links

### For Users
1. [Installation Guide](INSTALLATION.md) - Start here to set up the project
2. [API Examples](API_EXAMPLES.md) - Learn how to use the API
3. [Main README](../README.md) - Project overview and features

### For Developers
1. [Contributing Guide](CONTRIBUTING.md) - Contribution guidelines
2. [API Examples](API_EXAMPLES.md) - API development reference
3. [Installation Guide](INSTALLATION.md#development-setup) - Dev environment setup

## 📖 Additional Resources

- **[GitHub Repository](https://github.com/bobberdolle1/RealWorldMapGen-BNG)** - Source code
- **[Issue Tracker](https://github.com/bobberdolle1/RealWorldMapGen-BNG/issues)** - Report bugs or request features
- **[API Documentation](http://localhost:8000/docs)** - Interactive Swagger UI (when running)

## 🎯 Common Tasks

### Installing the Project
See [Installation Guide](INSTALLATION.md)

### Generating Your First Map
1. Start services: `docker-compose up -d`
2. Open web UI: http://localhost:8080
3. Select area on map
4. Click "Generate Map"
5. Download .zip file

### Using the API
See [API Examples](API_EXAMPLES.md) for:
- Basic map generation
- Batch processing
- File downloads
- Task monitoring

### Troubleshooting
Check [Installation Guide - Troubleshooting](INSTALLATION.md#troubleshooting) for:
- Ollama connection issues
- Docker problems
- Port conflicts
- Permission errors

## 🔧 Configuration

Key configuration files:
- `.env` - Environment variables and settings
- `docker-compose.yml` - Docker services configuration
- `pyproject.toml` - Python dependencies

See [Installation Guide - Configuration](INSTALLATION.md#configuration-options) for details.

## 📝 Documentation Format

All documentation is written in Markdown and follows these conventions:
- **Headers**: Use `#` for main sections, `##` for subsections
- **Code blocks**: Use triple backticks with language specifier
- **Links**: Use relative paths for internal docs
- **Examples**: Include practical, runnable examples

## 🤝 Contributing to Documentation

Found an error or want to improve the docs?
1. Edit the relevant .md file
2. Submit a pull request
3. See [Contributing Guide](CONTRIBUTING.md) for more details

---

**[⬅ Back to Main README](../README.md)**
