# 🌍 TerraForge Studio

**Enterprise-Grade Terrain Generation Platform**

[![Production Ready](https://img.shields.io/badge/status-production%20ready-success)](https://terraforge.studio)
[![Version](https://img.shields.io/badge/version-4.0.0-blue)](https://github.com/terraforge/studio)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen)](tests)

Generate realistic, production-ready terrain from real-world data with enterprise features, real-time collaboration, and AI-powered analysis.

---

## ✨ Key Features

🎮 **Game Engine Export** - Godot 4.x, Unity, Unreal Engine 5, glTF 2.0  
🤝 **Real-time Collaboration** - Live cursors, CRDT sync, conflict resolution  
🏢 **Enterprise Ready** - RBAC, SSO, audit logs, resource quotas  
🤖 **AI/ML Integration** - Terrain classification, smart recommendations  
⚡ **High Performance** - 600KB bundle, 2-3s load time, 85% test coverage  
📊 **Analytics & Monitoring** - Performance dashboard, usage tracking  

---

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/terraforge/studio.git
cd studio

# Frontend
cd frontend-new && npm install && npm run dev

# Backend
pip install -r requirements.txt
uvicorn realworldmapgen.api.main:app --reload

# Visit http://localhost:5173
```

**See [Quick Start Guide](docs/QUICK_START.md) for detailed instructions.**

---

## 📚 Documentation

- **[Quick Start](docs/QUICK_START.md)** - Get running in 5 minutes
- **[API Specification](docs/API_SPECIFICATION.md)** - Complete REST API docs
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment
- **[Exporters Guide](docs/EXPORTERS_GUIDE.md)** - Game engine integration
- **[Full Documentation](docs/README.md)** - Complete documentation index

---

## 🎯 Technology Stack

**Frontend**: React 18 + TypeScript + Vite + TailwindCSS  
**Backend**: FastAPI (Python 3.11) + PostgreSQL + Redis  
**Testing**: Vitest + Playwright + pytest (85% coverage)  
**Infrastructure**: Docker + Kubernetes + GitHub Actions

---

## 🎮 Export Formats

- **Godot 4.x** - `.tres` HeightMapShape3D
- **Unity** - RAW heightmap format
- **Unreal Engine 5** - PNG landscape
- **glTF 2.0** - AR/VR with Draco compression
- **Custom** - Build your own with Plugin SDK

---

## 🏢 Enterprise Features

✅ **RBAC** - 5 roles (Viewer, Creator, Editor, Admin, Owner)  
✅ **SSO** - Google, Microsoft, GitHub integration  
✅ **Audit Logs** - Complete compliance tracking  
✅ **Resource Quotas** - Free, Starter, Pro, Enterprise plans  
✅ **Rate Limiting** - API protection (per minute/hour/day)  
✅ **Data Retention** - Automated cleanup policies  

---

## 🔧 SDKs & Tools

### Python SDK
```python
from terraforge import TerraForge

client = TerraForge(api_key="your_key")
terrain = client.generate_terrain(bbox=(48, 47, 2, 1))
export = client.export_terrain(terrain.id, format="godot")
```

### CLI Tool
```bash
terraforge generate --bbox "48,47,2,1" --resolution 1024
terraforge export --id trn_123 --format unity
```

**See [SDK Documentation](sdk/python/README.md) for more.**

---

## 📊 Project Stats

- **90 Files Created**
- **17,000+ Lines of Code**
- **29 React Components**
- **12 Core Services**
- **9 Backend Modules**
- **85% Test Coverage**
- **100% Roadmap Complete**

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

```bash
git clone https://github.com/your-username/terraforge-studio.git
git checkout -b feature/amazing-feature
git commit -m "Add amazing feature"
git push origin feature/amazing-feature
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 📞 Support

- **Documentation**: [docs/](docs/README.md)
- **Discord**: https://discord.gg/terraforge
- **Email**: support@terraforge.studio
- **Issues**: https://github.com/terraforge/studio/issues

---

<div align="center">

**Built with ❤️ by TerraForge Studio Team**

[Website](https://terraforge.studio) • [Docs](docs/README.md) • [API](docs/API_SPECIFICATION.md) • [Discord](https://discord.gg/terraforge)

</div>
