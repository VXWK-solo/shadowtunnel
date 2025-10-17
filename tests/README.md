# Advanced VPN Server - Test Suite

## Overview
Comprehensive test suite for Advanced VPN Server covering unit, integration, end-to-end, and performance testing.

## Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_vpn_protocols.py
│   ├── test_webpanel.py
│   ├── test_monitoring.py
│   └── test_security.py
├── integration/            # Integration tests
│   ├── test_vpn_integration.py
│   ├── test_database_integration.py
│   └── test_api_integration.py
├── e2e/                    # End-to-end tests
│   ├── test_user_workflow.py
│   ├── test_admin_workflow.py
│   └── test_monitoring_workflow.py
├── performance/            # Performance tests
│   ├── load_test.js
│   ├── stress_test.js
│   └── benchmark_test.js
├── security/               # Security tests
│   ├── test_vulnerabilities.py
│   ├── test_penetration.py
│   └── test_compliance.py
└── fixtures/               # Test data and fixtures
    ├── test_configs/
    ├── test_users/
    └── test_certificates/
```

## Unit Tests

### VPN Protocol Tests
```python
# tests/unit/test_vpn_protocols.py
import pytest
from src.vpn.protocols import VLESSProtocol, VMessProtocol, TrojanProtocol

class TestVLESSProtocol:
    def test_vless_config_generation(self):
        """Test VLESS configuration generation"""
        protocol = VLESSProtocol()
        config = protocol.generate_config("testuser", "testpassword")
        
        assert config["protocol"] == "vless"
        assert config["user_id"] == "testuser"
        assert "encryption" in config
    
    def test_vless_connection_establishment(self):
        """Test VLESS connection establishment"""
        protocol = VLESSProtocol()
        connection = protocol.establish_connection("testuser", "testpassword")
        
        assert connection.is_connected()
        assert connection.get_latency() < 100  # ms
    
    def test_vless_traffic_encryption(self):
        """Test VLESS traffic encryption"""
        protocol = VLESSProtocol()
        data = b"test data"
        encrypted = protocol.encrypt(data)
        decrypted = protocol.decrypt(encrypted)
        
        assert decrypted == data

class TestVMessProtocol:
    def test_vmess_config_generation(self):
        """Test VMess configuration generation"""
        protocol = VMessProtocol()
        config = protocol.generate_config("testuser", "testpassword")
        
        assert config["protocol"] == "vmess"
        assert config["user_id"] == "testuser"
        assert "alterId" in config
    
    def test_vmess_connection_establishment(self):
        """Test VMess connection establishment"""
        protocol = VMessProtocol()
        connection = protocol.establish_connection("testuser", "testpassword")
        
        assert connection.is_connected()
        assert connection.get_latency() < 150  # ms

class TestTrojanProtocol:
    def test_trojan_config_generation(self):
        """Test Trojan configuration generation"""
        protocol = TrojanProtocol()
        config = protocol.generate_config("testuser", "testpassword")
        
        assert config["protocol"] == "trojan"
        assert config["password"] == "testpassword"
        assert "tls" in config
    
    def test_trojan_https_mimicking(self):
        """Test Trojan HTTPS mimicking"""
        protocol = TrojanProtocol()
        request = protocol.create_https_request("example.com")
        
        assert "Host: example.com" in request
        assert "User-Agent" in request
```

### Web Panel Tests
```python
# tests/unit/test_webpanel.py
import pytest
from src.webpanel.api import UserAPI, ConfigAPI, MetricsAPI

class TestUserAPI:
    def test_create_user(self):
        """Test user creation"""
        api = UserAPI()
        user = api.create_user("testuser", "vless")
        
        assert user.username == "testuser"
        assert user.protocol == "vless"
        assert user.is_active()
    
    def test_delete_user(self):
        """Test user deletion"""
        api = UserAPI()
        user = api.create_user("testuser", "vless")
        result = api.delete_user(user.id)
        
        assert result is True
        assert not api.get_user(user.id)
    
    def test_update_user(self):
        """Test user update"""
        api = UserAPI()
        user = api.create_user("testuser", "vless")
        updated_user = api.update_user(user.id, protocol="vmess")
        
        assert updated_user.protocol == "vmess"
        assert updated_user.username == "testuser"

class TestConfigAPI:
    def test_generate_config(self):
        """Test configuration generation"""
        api = ConfigAPI()
        config = api.generate_config("testuser", "vless")
        
        assert "vless" in config
        assert "server" in config
        assert "port" in config
    
    def test_validate_config(self):
        """Test configuration validation"""
        api = ConfigAPI()
        valid_config = {"protocol": "vless", "server": "example.com", "port": 443}
        invalid_config = {"protocol": "invalid", "server": "", "port": -1}
        
        assert api.validate_config(valid_config) is True
        assert api.validate_config(invalid_config) is False

class TestMetricsAPI:
    def test_get_system_metrics(self):
        """Test system metrics retrieval"""
        api = MetricsAPI()
        metrics = api.get_system_metrics()
        
        assert "cpu_usage" in metrics
        assert "memory_usage" in metrics
        assert "disk_usage" in metrics
        assert 0 <= metrics["cpu_usage"] <= 100
    
    def test_get_vpn_metrics(self):
        """Test VPN metrics retrieval"""
        api = MetricsAPI()
        metrics = api.get_vpn_metrics()
        
        assert "active_connections" in metrics
        assert "total_traffic" in metrics
        assert "connection_errors" in metrics
        assert metrics["active_connections"] >= 0
```

## Integration Tests

### VPN Integration Tests
```python
# tests/integration/test_vpn_integration.py
import pytest
from src.vpn.server import VPNServer
from src.vpn.protocols import VLESSProtocol, VMessProtocol

class TestVPNIntegration:
    @pytest.fixture
    def vpn_server(self):
        """Create VPN server instance"""
        server = VPNServer()
        server.start()
        yield server
        server.stop()
    
    def test_vless_integration(self, vpn_server):
        """Test VLESS protocol integration"""
        protocol = VLESSProtocol()
        config = protocol.generate_config("testuser", "testpassword")
        
        # Add user to server
        vpn_server.add_user(config)
        
        # Test connection
        connection = protocol.establish_connection("testuser", "testpassword")
        assert connection.is_connected()
        
        # Test data transfer
        test_data = b"Hello, World!"
        connection.send(test_data)
        received_data = connection.receive()
        assert received_data == test_data
    
    def test_vmess_integration(self, vpn_server):
        """Test VMess protocol integration"""
        protocol = VMessProtocol()
        config = protocol.generate_config("testuser", "testpassword")
        
        # Add user to server
        vpn_server.add_user(config)
        
        # Test connection
        connection = protocol.establish_connection("testuser", "testpassword")
        assert connection.is_connected()
        
        # Test data transfer
        test_data = b"Hello, World!"
        connection.send(test_data)
        received_data = connection.receive()
        assert received_data == test_data
    
    def test_multi_protocol_integration(self, vpn_server):
        """Test multiple protocols running simultaneously"""
        vless_config = VLESSProtocol().generate_config("vless_user", "password")
        vmess_config = VMessProtocol().generate_config("vmess_user", "password")
        
        vpn_server.add_user(vless_config)
        vpn_server.add_user(vmess_config)
        
        # Test both connections
        vless_conn = VLESSProtocol().establish_connection("vless_user", "password")
        vmess_conn = VMessProtocol().establish_connection("vmess_user", "password")
        
        assert vless_conn.is_connected()
        assert vmess_conn.is_connected()
        
        # Test data transfer on both
        test_data = b"Multi-protocol test"
        vless_conn.send(test_data)
        vmess_conn.send(test_data)
        
        assert vless_conn.receive() == test_data
        assert vmess_conn.receive() == test_data
```

## End-to-End Tests

### User Workflow Tests
```python
# tests/e2e/test_user_workflow.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestUserWorkflow:
    @pytest.fixture
    def driver(self):
        """Create web driver instance"""
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        yield driver
        driver.quit()
    
    def test_user_registration_workflow(self, driver):
        """Test complete user registration workflow"""
        # Navigate to web panel
        driver.get("http://localhost:2053")
        
        # Login as admin
        driver.find_element(By.ID, "username").send_keys("admin")
        driver.find_element(By.ID, "password").send_keys("admin123")
        driver.find_element(By.ID, "login-btn").click()
        
        # Wait for dashboard
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dashboard"))
        )
        
        # Add new user
        driver.find_element(By.ID, "add-user-btn").click()
        
        # Fill user form
        driver.find_element(By.ID, "username").send_keys("testuser")
        driver.find_element(By.ID, "protocol").send_keys("vless")
        driver.find_element(By.ID, "device").send_keys("test-device")
        
        # Submit form
        driver.find_element(By.ID, "submit-btn").click()
        
        # Verify user was created
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//td[text()='testuser']"))
        )
        
        # Download configuration
        driver.find_element(By.XPATH, "//tr[td[text()='testuser']]//button[text()='Download']").click()
        
        # Verify download started
        assert "testuser-config.json" in driver.current_url
    
    def test_user_management_workflow(self, driver):
        """Test user management workflow"""
        # Login and navigate to users
        driver.get("http://localhost:2053")
        driver.find_element(By.ID, "username").send_keys("admin")
        driver.find_element(By.ID, "password").send_keys("admin123")
        driver.find_element(By.ID, "login-btn").click()
        
        # Wait for dashboard
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dashboard"))
        )
        
        # Navigate to users page
        driver.find_element(By.ID, "users-tab").click()
        
        # Verify users are displayed
        users = driver.find_elements(By.CLASS_NAME, "user-row")
        assert len(users) > 0
        
        # Test user search
        search_box = driver.find_element(By.ID, "user-search")
        search_box.send_keys("testuser")
        
        # Verify search results
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//td[text()='testuser']"))
        )
        
        # Test user deletion
        delete_btn = driver.find_element(By.XPATH, "//tr[td[text()='testuser']]//button[text()='Delete']")
        delete_btn.click()
        
        # Confirm deletion
        driver.find_element(By.ID, "confirm-delete-btn").click()
        
        # Verify user was deleted
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.XPATH, "//td[text()='testuser']"))
        )
```

## Performance Tests

### Load Testing with k6
```javascript
// tests/performance/load_test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

export let errorRate = new Rate('errors');

export let options = {
  stages: [
    { duration: '2m', target: 100 }, // Ramp up to 100 users
    { duration: '5m', target: 100 }, // Stay at 100 users
    { duration: '2m', target: 200 }, // Ramp up to 200 users
    { duration: '5m', target: 200 }, // Stay at 200 users
    { duration: '2m', target: 0 },   // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests must complete below 2s
    http_req_failed: ['rate<0.1'],     // Error rate must be below 10%
    errors: ['rate<0.1'],              // Custom error rate must be below 10%
  },
};

export default function() {
  // Test web panel endpoints
  let response = http.get('http://localhost:2053/api/users');
  errorRate.add(response.status !== 200);
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 2000ms': (r) => r.timings.duration < 2000,
    'response has users': (r) => r.json().users !== undefined,
  });
  
  // Test VPN connection endpoint
  response = http.post('http://localhost:2053/api/vpn/connect', {
    username: 'testuser',
    password: 'testpassword',
  });
  
  errorRate.add(response.status !== 200);
  
  check(response, {
    'connection status is 200': (r) => r.status === 200,
    'connection response time < 1000ms': (r) => r.timings.duration < 1000,
  });
  
  sleep(1);
}
```

### Stress Testing
```javascript
// tests/performance/stress_test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '1m', target: 10 },   // Ramp up to 10 users
    { duration: '2m', target: 50 },   // Ramp up to 50 users
    { duration: '3m', target: 100 },  // Ramp up to 100 users
    { duration: '4m', target: 200 },  // Ramp up to 200 users
    { duration: '5m', target: 500 },  // Ramp up to 500 users
    { duration: '10m', target: 500 }, // Stay at 500 users
    { duration: '2m', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<5000'], // 95% of requests must complete below 5s
    http_req_failed: ['rate<0.2'],     // Error rate must be below 20%
  },
};

export default function() {
  // Test various endpoints under stress
  let endpoints = [
    'http://localhost:2053/api/users',
    'http://localhost:2053/api/metrics',
    'http://localhost:2053/api/status',
    'http://localhost:3000/api/health',
    'http://localhost:9090/api/v1/query?query=up',
  ];
  
  for (let endpoint of endpoints) {
    let response = http.get(endpoint);
    
    check(response, {
      'status is 200': (r) => r.status === 200,
      'response time < 5000ms': (r) => r.timings.duration < 5000,
    });
    
    sleep(0.1);
  }
}
```

## Security Tests

### Vulnerability Tests
```python
# tests/security/test_vulnerabilities.py
import pytest
import requests
from src.security.scanner import VulnerabilityScanner

class TestVulnerabilities:
    def test_sql_injection(self):
        """Test for SQL injection vulnerabilities"""
        scanner = VulnerabilityScanner()
        payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
        ]
        
        for payload in payloads:
            response = requests.post(
                "http://localhost:2053/api/users",
                json={"username": payload, "password": "test"}
            )
            
            # Should not return user data or cause errors
            assert response.status_code != 200 or "error" in response.text.lower()
    
    def test_xss_vulnerability(self):
        """Test for XSS vulnerabilities"""
        scanner = VulnerabilityScanner()
        payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
        ]
        
        for payload in payloads:
            response = requests.post(
                "http://localhost:2053/api/users",
                json={"username": payload, "password": "test"}
            )
            
            # Should not execute JavaScript
            assert "<script>" not in response.text
            assert "javascript:" not in response.text
    
    def test_csrf_protection(self):
        """Test CSRF protection"""
        scanner = VulnerabilityScanner()
        
        # Test without CSRF token
        response = requests.post(
            "http://localhost:2053/api/users",
            json={"username": "testuser", "password": "test"},
            headers={"X-CSRF-Token": ""}
        )
        
        # Should be rejected
        assert response.status_code == 403
    
    def test_authentication_bypass(self):
        """Test authentication bypass vulnerabilities"""
        scanner = VulnerabilityScanner()
        
        # Test with invalid credentials
        response = requests.post(
            "http://localhost:2053/api/auth/login",
            json={"username": "admin", "password": "wrongpassword"}
        )
        
        # Should be rejected
        assert response.status_code == 401
        
        # Test with empty credentials
        response = requests.post(
            "http://localhost:2053/api/auth/login",
            json={"username": "", "password": ""}
        )
        
        # Should be rejected
        assert response.status_code == 401
```

## Test Configuration

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=xml
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance tests
    security: Security tests
    slow: Slow running tests
```

### conftest.py
```python
import pytest
import tempfile
import shutil
from src.vpn.server import VPNServer
from src.webpanel.api import UserAPI

@pytest.fixture(scope="session")
def temp_dir():
    """Create temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def vpn_server(temp_dir):
    """Create VPN server instance for tests"""
    server = VPNServer(config_dir=temp_dir)
    server.start()
    yield server
    server.stop()

@pytest.fixture
def user_api():
    """Create user API instance for tests"""
    return UserAPI()

@pytest.fixture
def test_user():
    """Create test user"""
    return {
        "username": "testuser",
        "password": "testpassword",
        "protocol": "vless",
        "device": "test-device"
    }
```

## Running Tests

### Command Line
```bash
# Run all tests
pytest

# Run specific test types
pytest -m unit
pytest -m integration
pytest -m e2e
pytest -m performance
pytest -m security

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_vpn_protocols.py

# Run with verbose output
pytest -v

# Run in parallel
pytest -n auto
```

### CI/CD Integration
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v3
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          pytest --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

---

**Test Suite Version**: 1.0  
**Last Updated**: 2024-01-01  
**Coverage Target**: 80%  
**Test Types**: Unit, Integration, E2E, Performance, Security
