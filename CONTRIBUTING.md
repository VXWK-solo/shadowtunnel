# Contributing to Advanced VPN Server

Thank you for your interest in contributing to Advanced VPN Server! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Process](#contributing-process)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Security](#security)
- [Release Process](#release-process)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- Python 3.8+
- Ansible 2.9+
- Docker and Docker Compose
- Git
- Node.js 16+ (for web panel development)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/advanced-vpn.git
   cd advanced-vpn
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements-dev.txt
   npm install
   ```

3. **Set Up Development Environment**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

4. **Run Tests**
   ```bash
   pytest tests/unit/
   ```

## Contributing Process

### 1. Issue Creation

Before starting work, please:
- Check existing issues to avoid duplicates
- Create an issue describing the problem or feature
- Wait for maintainer approval before starting work

### 2. Branch Strategy

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Feature branches
- `bugfix/*`: Bug fix branches
- `hotfix/*`: Critical bug fixes

### 3. Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow code standards
   - Write tests
   - Update documentation

3. **Test Changes**
   ```bash
   pytest tests/
   npm test
   docker-compose -f docker-compose.test.yml up --abort-on-container-exit
   ```

4. **Submit Pull Request**
   - Fill out the PR template
   - Link related issues
   - Request reviews from maintainers

### 4. Review Process

- All PRs require at least 2 approvals
- CI/CD pipeline must pass
- Code coverage must not decrease
- Security scans must pass

## Code Standards

### Python Code

- Follow PEP 8
- Use Black for formatting
- Use isort for import sorting
- Use mypy for type checking
- Maximum line length: 88 characters

```python
# Example Python code
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class VPNProtocol:
    """Base class for VPN protocols."""
    
    def __init__(self, name: str, port: int) -> None:
        self.name = name
        self.port = port
        self._connections: List[Connection] = []
    
    def add_connection(self, connection: Connection) -> None:
        """Add a new connection."""
        self._connections.append(connection)
        logger.info(f"Added connection to {self.name}")
    
    def get_active_connections(self) -> int:
        """Get number of active connections."""
        return len([c for c in self._connections if c.is_active()])
```

### JavaScript/TypeScript Code

- Use ESLint with recommended rules
- Use Prettier for formatting
- Use TypeScript for type safety
- Follow React best practices

```typescript
// Example TypeScript code
interface User {
  id: string;
  username: string;
  protocol: VPNProtocol;
  isActive: boolean;
}

interface UserAPI {
  getUsers(): Promise<User[]>;
  createUser(user: Omit<User, 'id'>): Promise<User>;
  deleteUser(id: string): Promise<void>;
}

class UserService implements UserAPI {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async getUsers(): Promise<User[]> {
    const response = await fetch(`${this.baseUrl}/api/users`);
    if (!response.ok) {
      throw new Error('Failed to fetch users');
    }
    return response.json();
  }

  async createUser(user: Omit<User, 'id'>): Promise<User> {
    const response = await fetch(`${this.baseUrl}/api/users`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(user),
    });
    if (!response.ok) {
      throw new Error('Failed to create user');
    }
    return response.json();
  }

  async deleteUser(id: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/users/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('Failed to delete user');
    }
  }
}
```

### YAML/Ansible Code

- Use consistent indentation (2 spaces)
- Include comments for complex logic
- Use meaningful variable names
- Follow Ansible best practices

```yaml
# Example Ansible task
- name: Install Xray
  apt:
    name: xray
    state: present
    update_cache: yes
  when: vpn_protocols.xray_enabled | default(true)
  tags:
    - xray
    - vpn
    - packages

- name: Configure Xray
  template:
    src: xray-config.json.j2
    dest: /etc/xray/config.json
    owner: xray
    group: xray
    mode: '0644'
  notify: restart xray
  when: vpn_protocols.xray_enabled | default(true)
  tags:
    - xray
    - vpn
    - configuration
```

## Testing

### Test Types

1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete user workflows
4. **Performance Tests**: Test system performance
5. **Security Tests**: Test security vulnerabilities

### Writing Tests

```python
# Example unit test
import pytest
from unittest.mock import Mock, patch
from src.vpn.protocols import VLESSProtocol

class TestVLESSProtocol:
    def test_config_generation(self):
        """Test VLESS configuration generation."""
        protocol = VLESSProtocol()
        config = protocol.generate_config("testuser", "testpassword")
        
        assert config["protocol"] == "vless"
        assert config["user_id"] == "testuser"
        assert "encryption" in config
    
    @patch('src.vpn.protocols.requests.post')
    def test_connection_establishment(self, mock_post):
        """Test VLESS connection establishment."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "connected"}
        mock_post.return_value = mock_response
        
        protocol = VLESSProtocol()
        connection = protocol.establish_connection("testuser", "testpassword")
        
        assert connection.is_connected()
        mock_post.assert_called_once()
    
    def test_invalid_credentials(self):
        """Test handling of invalid credentials."""
        protocol = VLESSProtocol()
        
        with pytest.raises(ValueError, match="Invalid credentials"):
            protocol.establish_connection("", "")
```

### Test Coverage

- Maintain minimum 80% code coverage
- Aim for 90%+ coverage for critical components
- Use `pytest-cov` for coverage reporting

```bash
# Run tests with coverage
pytest --cov=src --cov-report=html --cov-report=xml

# Run specific test types
pytest -m unit
pytest -m integration
pytest -m e2e
pytest -m security
```

## Documentation

### Documentation Standards

- Use Markdown for all documentation
- Include code examples
- Keep documentation up-to-date
- Use clear, concise language

### Documentation Types

1. **API Documentation**: Use OpenAPI/Swagger
2. **User Guides**: Step-by-step instructions
3. **Developer Guides**: Technical documentation
4. **Architecture Docs**: System design and components

### Writing Documentation

```markdown
# API Endpoint Documentation

## Create User

Creates a new VPN user.

**Endpoint**: `POST /api/users`

**Request Body**:
```json
{
  "username": "string",
  "protocol": "vless|vmess|trojan|shadowsocks",
  "device": "string (optional)"
}
```

**Response**:
```json
{
  "id": "uuid",
  "username": "string",
  "protocol": "string",
  "device": "string",
  "created_at": "datetime",
  "is_active": true
}
```

**Example**:
```bash
curl -X POST http://localhost:2053/api/users \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "protocol": "vless"}'
```
```

## Security

### Security Guidelines

- Never commit secrets or credentials
- Use environment variables for sensitive data
- Follow OWASP security guidelines
- Report security vulnerabilities responsibly

### Reporting Security Issues

1. **DO NOT** create public GitHub issues
2. Email security issues to: security@advanced-vpn.com
3. Include detailed reproduction steps
4. Wait for maintainer response before disclosure

### Security Checklist

- [ ] No hardcoded credentials
- [ ] Input validation implemented
- [ ] Output encoding used
- [ ] Authentication required
- [ ] Authorization checked
- [ ] Error handling secure
- [ ] Logging doesn't expose sensitive data

## Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):
- `MAJOR`: Breaking changes
- `MINOR`: New features, backward compatible
- `PATCH`: Bug fixes, backward compatible

### Release Steps

1. **Update Version**
   ```bash
   # Update version in setup.py, package.json, etc.
   git tag v1.2.3
   git push origin v1.2.3
   ```

2. **Create Release**
   - GitHub will automatically create a release
   - Update CHANGELOG.md
   - Generate release notes

3. **Deploy**
   - CI/CD pipeline handles deployment
   - Monitor deployment status
   - Verify functionality

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version numbers updated
- [ ] Security scan passed
- [ ] Performance tests passed
- [ ] Release notes written

## Community Guidelines

### Communication

- Be respectful and inclusive
- Use clear, constructive language
- Help others learn and grow
- Follow the code of conduct

### Getting Help

- Check existing documentation
- Search closed issues
- Ask questions in discussions
- Join our Discord community

### Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation
- Community highlights

## Development Tools

### Recommended IDE Setup

**VS Code Extensions**:
- Python
- Ansible
- Docker
- GitLens
- Prettier
- ESLint

**PyCharm Plugins**:
- Ansible
- Docker
- Git Integration
- Database Tools

### Useful Commands

```bash
# Development
docker-compose -f docker-compose.dev.yml up -d
pytest tests/unit/ -v
npm run dev

# Testing
pytest tests/ --cov=src
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Linting
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/

# Security
bandit -r src/
safety check
```

## License

By contributing to Advanced VPN Server, you agree that your contributions will be licensed under the AGPL-3.0 License.

---

Thank you for contributing to ShadowTunnel!
