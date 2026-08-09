# Documentation

Welcome to the Salad Monitor documentation! This guide will help you navigate the various documentation files.

---

## 📚 Documentation Structure

### Getting Started
- **[README.md](README.md)** - Start here! Project overview, features, installation, and API reference

### Testing
- **[TESTING.md](TESTING.md)** - Unit test structure and conventions for developers
- **[MANUAL_TESTING.md](MANUAL_TESTING.md)** - Manual testing procedures for API and Docker

### Project Information
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and release notes
- **[LICENSE](LICENSE)** - MIT License information

---

## 📖 Quick Links

### For Users

**Installing Salad Monitor:**
1. Read the [Installation section in README](README.md#-installation)
2. Follow the [Docker Installation guide](README.md#-docker-installation-recommended)
3. Configure using [Environment Variables](README.md#environment-variables)

**Using the API:**
1. See [API Endpoints documentation](README.md#-api-endpoints)
2. Browse interactive docs at `http://localhost:8000/docs` when running
3. Check [MANUAL_TESTING.md](MANUAL_TESTING.md) for example API calls

**Integrations:**
- [Home Assistant Integration](https://github.com/dellanx/salad-monitor-ha)

### For Developers

**Setting Up Development:**
1. Clone the repository
2. Open in VS Code with devcontainer
3. Run `pip install -r requirements.txt`
4. See [TESTING.md](TESTING.md) for test structure

**Contributing:**
1. Read [TESTING.md](TESTING.md) for test conventions
2. Follow the test structure (tests mirror src structure)
3. Run `pytest` before submitting PRs
4. Check coverage with `pytest --cov=src`

**Testing Your Changes:**
1. Unit tests: See [TESTING.md](TESTING.md)
2. Manual testing: See [MANUAL_TESTING.md](MANUAL_TESTING.md)
3. Integration testing: Follow Docker testing in [MANUAL_TESTING.md](MANUAL_TESTING.md#6-docker-testing)

---

## 📋 Documentation by Topic

### Installation & Configuration
- [Docker Installation](README.md#-docker-installation-recommended)
- [Environment Variables](README.md#environment-variables)
- [Docker Compose Example](README.md#docker-compose-example)

### API Reference
- [Legacy API Endpoints](README.md#legacy-api-backward-compatible)
- [v1 API Endpoints](README.md#new-v1-api-enhanced-features)
- [Interactive API Docs](http://localhost:8000/docs) (when running)

### Features
- [Core Monitoring](README.md#core-monitoring)
- [Enhanced Metrics](README.md#enhanced-metrics-v20)
- [Wallet Information](README.md#wallet--earnings)
- [Hardware Metrics](README.md#hardware-metrics)
- [Network Statistics](README.md#network-statistics)
- [GPU Demand Data](README.md#gpu-demand-from-salad-api)

### Testing
- [Unit Test Structure](TESTING.md#-test-directory-structure)
- [Running Tests](TESTING.md#-running-tests)
- [Writing Tests](TESTING.md#-writing-tests)
- [Manual Testing](MANUAL_TESTING.md)
- [Docker Testing](MANUAL_TESTING.md#6-docker-testing)
- [Feature Toggle Testing](MANUAL_TESTING.md#3-feature-toggle-testing)

### Troubleshooting
- [Common Issues](MANUAL_TESTING.md#troubleshooting)
- [Expected Results](MANUAL_TESTING.md#expected-results)

### Project History
- [Changelog](CHANGELOG.md)
- [Version 0.2 Release Notes](CHANGELOG.md#020---2026-08-08)

---

## 🎯 Common Tasks

### I want to...

#### ...install and run Salad Monitor
→ [README.md - Installation](README.md#-installation)

#### ...understand what endpoints are available
→ [README.md - API Endpoints](README.md#-api-endpoints)

#### ...test the API manually
→ [MANUAL_TESTING.md](MANUAL_TESTING.md)

#### ...run unit tests
→ [TESTING.md - Running Tests](TESTING.md#-running-tests)

#### ...write new unit tests
→ [TESTING.md - Writing Tests](TESTING.md#-writing-tests)

#### ...understand what changed in v0.2
→ [CHANGELOG.md - v0.2](CHANGELOG.md#020---2026-08-08)

#### ...configure feature toggles
→ [README.md - Environment Variables](README.md#environment-variables)

#### ...troubleshoot issues
→ [MANUAL_TESTING.md - Troubleshooting](MANUAL_TESTING.md#troubleshooting)

#### ...integrate with Home Assistant
→ [Home Assistant Integration](https://github.com/dellanx/salad-monitor-ha)

#### ...build a Docker image
→ [MANUAL_TESTING.md - Docker Testing](MANUAL_TESTING.md#6-docker-testing)

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Set up development environment**
   - Use VS Code with devcontainer
   - Install dependencies: `pip install -r requirements.txt`

2. **Understand the codebase**
   - Read [README.md](README.md) for project overview
   - Check [TESTING.md](TESTING.md) for test structure

3. **Make your changes**
   - Follow existing code style
   - Mirror test structure (see [TESTING.md](TESTING.md))
   - Add unit tests for new code

4. **Test your changes**
   - Run unit tests: `pytest`
   - Run manual tests: See [MANUAL_TESTING.md](MANUAL_TESTING.md)
   - Check coverage: `pytest --cov=src`

5. **Submit a PR**
   - Describe your changes
   - Reference any issues
   - Include test results

---

## 📞 Getting Help

- **Issues**: Open an issue on GitHub
- **Questions**: Start a discussion on GitHub
- **Documentation Issues**: Submit a PR to improve docs

---

## 📝 Documentation Standards

When updating documentation:

1. **Keep it organized** - Put content in the right file
2. **Use clear headings** - Make it easy to scan
3. **Include examples** - Show, don't just tell
4. **Link between docs** - Help users find related info
5. **Update this index** - Keep DOCS.md current

---

## 🔗 External Resources

- [Salad.com](https://salad.com/) - The Salad platform
- [SaladXRay](https://github.com/joseluisfreire/SaladXRay) - Inspiration for v0.2
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Web framework
- [pytest Documentation](https://docs.pytest.org/) - Test framework
- [Docker Documentation](https://docs.docker.com/) - Containerization

---

**Last Updated:** 2026-08-08  
**Version:** 0.2.0 (Pre-release)
