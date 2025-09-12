"""
Test suite for MetaPython v0.8.0 GA enterprise features
"""

import pytest
import tempfile
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import metapython


class TestVersion:
    """Test version information"""
    
    def test_version_is_0_8_0(self):
        assert metapython.__version__ == "0.8.0"
    
    def test_enterprise_classes_available(self):
        """Test that enterprise classes are importable"""
        assert hasattr(metapython, 'ObservabilityManager')
        assert hasattr(metapython, 'DataLineageTracker')
        assert hasattr(metapython, 'EnterpriseSecurityManager')
        assert hasattr(metapython, 'BIConnectorSuite')
        assert hasattr(metapython, 'RBridgeExperimental')
        assert hasattr(metapython, 'ContentAddressableCache')


class TestObservabilityManager:
    """Test observability features"""
    
    def test_observability_manager_creation(self):
        obs = metapython.ObservabilityManager(
            service_name="test-service",
            prometheus_port=0  # Disable server start
        )
        assert obs.service_name == "test-service"
        assert obs.prometheus_port == 0
    
    def test_record_analysis_without_prometheus(self):
        obs = metapython.ObservabilityManager(prometheus_port=0)
        # Should not raise exception
        obs.record_analysis("test", 1.0, 10)
        obs.record_error("test_error")
        obs.record_cache_result(True)


class TestDataLineageTracker:
    """Test data lineage tracking"""
    
    def test_lineage_tracker_creation(self):
        tracker = metapython.DataLineageTracker(
            openlineage_url="http://test.example.com",
            namespace="test"
        )
        assert tracker.namespace == "test"
        assert tracker.openlineage_url == "http://test.example.com"
    
    def test_lineage_operations_without_client(self):
        tracker = metapython.DataLineageTracker()
        
        # Should return None when no client
        run_id = tracker.start_analysis_run(
            "test-analysis",
            ["input.csv"],
            {"method": "REML"}
        )
        assert run_id is None
        
        # Should not raise exception
        tracker.complete_analysis_run("test-run", ["output.csv"])


class TestEnterpriseSecurityManager:
    """Test enterprise security features"""
    
    def test_security_manager_creation(self):
        manager = metapython.EnterpriseSecurityManager(
            kms_provider="aws",
            region="us-west-2"
        )
        assert manager.kms_provider == "aws"
        assert manager.region == "us-west-2"
    
    def test_encrypt_decrypt_without_kms(self):
        manager = metapython.EnterpriseSecurityManager()
        
        # Should return data as-is when no KMS
        test_data = "sensitive information"
        encrypted = manager.encrypt_sensitive_data(test_data, "test-key")
        assert encrypted == test_data
        
        decrypted = manager.decrypt_sensitive_data(encrypted, "test-key")
        assert decrypted == test_data


class TestBIConnectorSuite:
    """Test BI connector functionality"""
    
    def test_bi_connector_creation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bi = metapython.BIConnectorSuite(temp_dir=temp_dir)
            assert bi.temp_dir == temp_dir
            assert os.path.exists(temp_dir)
    
    def test_csv_export(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bi = metapython.BIConnectorSuite(temp_dir=temp_dir)
            
            test_results = {
                'studies': [
                    {'effect': 0.5, 'se': 0.1, 'weight': 1.0},
                    {'effect': 0.3, 'se': 0.15, 'weight': 0.8}
                ]
            }
            
            csv_file = bi.export_to_csv(test_results, "test_export")
            assert csv_file is not None
            assert os.path.exists(csv_file)
            assert csv_file.endswith('.csv')


class TestRBridgeExperimental:
    """Test R bridge functionality"""
    
    def test_r_bridge_creation(self):
        r_bridge = metapython.RBridgeExperimental()
        # Should initialize without error
        assert hasattr(r_bridge, 'r_available')
    
    def test_r_wrapper_generation(self):
        r_bridge = metapython.RBridgeExperimental()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            wrapper_path = r_bridge.generate_r_wrapper(temp_dir)
            
            if r_bridge.r_available:
                assert wrapper_path is not None
                assert os.path.exists(wrapper_path)
                assert wrapper_path.endswith('.R')
            else:
                assert wrapper_path is None
    
    def test_r_integration_demo(self):
        r_bridge = metapython.RBridgeExperimental()
        demo_result = r_bridge.demonstrate_r_integration()
        
        assert 'available' in demo_result
        assert isinstance(demo_result['available'], bool)


class TestContentAddressableCache:
    """Test content-addressable caching"""
    
    def test_cache_creation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = metapython.ContentAddressableCache(
                cache_dir=temp_dir,
                max_size_mb=10
            )
            assert cache.cache_dir == temp_dir
            assert cache.max_size_mb == 10
            assert os.path.exists(temp_dir)
    
    def test_cache_operations(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = metapython.ContentAddressableCache(cache_dir=temp_dir)
            
            # Test put and get
            test_data = {"key": "value", "number": 42}
            assert cache.put("test_key", test_data)
            
            retrieved = cache.get("test_key")
            assert retrieved == test_data
            
            # Test missing key
            missing = cache.get("missing_key")
            assert missing is None


class TestCLIFunctions:
    """Test CLI entry points"""
    
    def test_main_function_exists(self):
        assert hasattr(metapython, 'main')
        assert callable(metapython.main)
    
    def test_run_cli_function_exists(self):
        assert hasattr(metapython, 'run_cli')
        assert callable(metapython.run_cli)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])