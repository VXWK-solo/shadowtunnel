#!/usr/bin/env python3

import os
import sys
import yaml
import json
import subprocess
from pathlib import Path

class VPNProjectTester:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def test_file_structure(self):
        print("Checking file structure...")
        
        required_files = [
            'README.md',
            'config.cfg',
            'deploy',
            'quick-start.sh',
            'docker-compose.yml',
            'Dockerfile',
            'main.yml'
        ]
        
        for file in required_files:
            if (self.project_path / file).exists():
                print(f"  ✓ {file}")
                self.results['passed'] += 1
            else:
                print(f"  ✗ {file} - missing")
                self.results['failed'] += 1
                self.results['errors'].append(f"Missing file: {file}")
    
    def test_yaml_syntax(self):
        print("\nChecking YAML syntax...")
        
        yaml_files = [
            'config.cfg',
            'docker-compose.yml',
            'main.yml'
        ]
        
        for file in yaml_files:
            try:
                with open(self.project_path / file, 'r') as f:
                    yaml.safe_load(f)
                print(f"  ✓ {file} - syntax valid")
                self.results['passed'] += 1
            except Exception as e:
                print(f"  ✗ {file} - syntax error: {e}")
                self.results['failed'] += 1
                self.results['errors'].append(f"YAML syntax error in {file}: {e}")
    
    def test_ansible_structure(self):
        print("\nChecking Ansible structure...")
        
        playbooks_dir = self.project_path / 'playbooks'
        if playbooks_dir.exists():
            playbooks = list(playbooks_dir.glob('*.yml'))
            print(f"  ✓ Found {len(playbooks)} playbooks")
            self.results['passed'] += 1
        else:
            print("  ✗ playbooks directory missing")
            self.results['failed'] += 1
        
        roles_dir = self.project_path / 'roles'
        if roles_dir.exists():
            roles = [d for d in roles_dir.iterdir() if d.is_dir()]
            print(f"  ✓ Found {len(roles)} roles")
            self.results['passed'] += 1
        else:
            print("  ✗ roles directory missing")
            self.results['failed'] += 1
    
    def test_docker_config(self):
        print("\nChecking Docker configuration...")
        
        dockerfile = self.project_path / 'Dockerfile'
        if dockerfile.exists():
            print("  ✓ Dockerfile found")
            self.results['passed'] += 1
        else:
            print("  ✗ Dockerfile missing")
            self.results['failed'] += 1
        
        compose_file = self.project_path / 'docker-compose.yml'
        if compose_file.exists():
            try:
                with open(compose_file, 'r') as f:
                    compose_config = yaml.safe_load(f)
                
                if 'services' in compose_config:
                    services = list(compose_config['services'].keys())
                    print(f"  ✓ Found {len(services)} services in docker-compose.yml")
                    self.results['passed'] += 1
                else:
                    print("  ✗ No services section in docker-compose.yml")
                    self.results['failed'] += 1
            except Exception as e:
                print(f"  ✗ Error in docker-compose.yml: {e}")
                self.results['failed'] += 1
    
    def test_monitoring_config(self):
        print("\nChecking monitoring configuration...")
        
        monitoring_dir = self.project_path / 'monitoring'
        if monitoring_dir.exists():
            config_files = list(monitoring_dir.glob('*.yml'))
            print(f"  ✓ Found {len(config_files)} monitoring config files")
            self.results['passed'] += 1
        else:
            print("  ✗ monitoring directory missing")
            self.results['failed'] += 1
    
    def test_security_config(self):
        print("\nChecking security configuration...")
        
        security_dir = self.project_path / 'security'
        if security_dir.exists():
            security_files = list(security_dir.glob('*.md'))
            print(f"  ✓ Found {len(security_files)} security files")
            self.results['passed'] += 1
        else:
            print("  ✗ security directory missing")
            self.results['failed'] += 1
    
    def test_scripts(self):
        print("\nChecking scripts...")
        
        scripts_dir = self.project_path / 'scripts'
        if scripts_dir.exists():
            scripts = list(scripts_dir.glob('*.sh')) + list(scripts_dir.glob('*.py'))
            print(f"  ✓ Found {len(scripts)} scripts")
            self.results['passed'] += 1
        else:
            print("  ✗ scripts directory missing")
            self.results['failed'] += 1
    
    def test_documentation(self):
        print("\nChecking documentation...")
        
        doc_files = [
            'README.md',
            'QUICK_START.md',
            'USER_FRIENDLY.md',
            'ADVANCED_FEATURES.md',
            'CONTRIBUTING.md',
            'PROJECT_INFO.md'
        ]
        
        found_docs = 0
        for doc in doc_files:
            if (self.project_path / doc).exists():
                found_docs += 1
        
        print(f"  ✓ Found {found_docs}/{len(doc_files)} documentation files")
        self.results['passed'] += 1
    
    def test_ci_cd(self):
        print("\nChecking CI/CD configuration...")
        
        github_dir = self.project_path / '.github' / 'workflows'
        if github_dir.exists():
            workflow_files = list(github_dir.glob('*.yml'))
            print(f"  ✓ Found {len(workflow_files)} workflow files")
            self.results['passed'] += 1
        else:
            print("  ✗ .github/workflows directory missing")
            self.results['failed'] += 1
    
    def run_all_tests(self):
        print("Running ShadowTunnel tests")
        print("=" * 50)
        
        self.test_file_structure()
        self.test_yaml_syntax()
        self.test_ansible_structure()
        self.test_docker_config()
        self.test_monitoring_config()
        self.test_security_config()
        self.test_scripts()
        self.test_documentation()
        self.test_ci_cd()
        
        print("\n" + "=" * 50)
        print("TEST RESULTS")
        print("=" * 50)
        print(f"✓ Passed: {self.results['passed']}")
        print(f"✗ Failed: {self.results['failed']}")
        
        if self.results['errors']:
            print(f"\nErrors:")
            for error in self.results['errors']:
                print(f"  - {error}")
        
        success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed'])) * 100
        print(f"\nSuccess rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("Excellent! Project is ready for use.")
        elif success_rate >= 70:
            print("Good! Minor issues to address.")
        else:
            print("Project needs improvement.")
        
        return success_rate >= 70

def main():
    project_path = "/home/pc-arch/tester/advanced-vpn"
    
    if not os.path.exists(project_path):
        print(f"Path {project_path} does not exist")
        sys.exit(1)
    
    tester = VPNProjectTester(project_path)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
