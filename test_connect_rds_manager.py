"""
Tests for RDS Connection Manager
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestConnectionManager:
    """Tests for connection manager"""
    
    @pytest.fixture
    def sample_catalog(self, tmp_path):
        """Sample database catalog for testing"""
        catalog = [
            {
                "alias": "prod-main",
                "dbname": "prod_db",
                "db_endpoint": "prod.example.com",
                "port": 5432,
                "region": "ap-south-1",
                "account_id": "123456789012",
                "env": "prod"
            },
            {
                "alias": "dev-local",
                "dbname": "dev_db",
                "db_endpoint": "dev.example.com",
                "port": 5432,
                "region": "ap-south-1",
                "account_id": "123456789012",
                "env": "dev"
            }
        ]
        
        catalog_file = tmp_path / "catalog.json"
        with open(catalog_file, 'w') as f:
            json.dump(catalog, f)
        
        return str(catalog_file)
    
    def test_catalog_loads(self, sample_catalog):
        """Catalog file loads without errors"""
        with open(sample_catalog, 'r') as f:
            data = json.load(f)
        assert len(data) == 2
        assert data[0]['alias'] == 'prod-main'
    
    def test_catalog_structure(self, sample_catalog):
        """Catalog entries have required fields"""
        with open(sample_catalog, 'r') as f:
            catalog = json.load(f)
        
        required = ['alias', 'dbname', 'db_endpoint', 'port', 'region', 'account_id', 'env']
        for entry in catalog:
            for field in required:
                assert field in entry
    
    def test_invalid_catalog(self, tmp_path):
        """Invalid JSON raises error"""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not valid json {")
        
        with pytest.raises(json.JSONDecodeError):
            with open(bad_file, 'r') as f:
                json.load(f)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
