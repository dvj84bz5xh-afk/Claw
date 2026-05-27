#!/usr/bin/env python3
"""
Phase 4 Verification Script
验证Phase 4所有模块是否正常工作
"""

import sys
import time
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

def test_mock_services():
    """测试Mock服务"""
    print("\n[1/7] Testing Mock Services...")
    
    try:
        from mock_services import MockScenarios, TestHarness
        
        harness = TestHarness()
        harness.setup("full")
        
        harness.add_test(
            name="Read virtual file",
            tool="file_read",
            arguments={"file_path": "config.json"},
            expected_success=True
        )
        
        harness.add_test(
            name="Bash command",
            tool="bash",
            arguments={"command": "ls -la"},
            expected_success=True
        )
        
        result = harness.run_all()
        
        if result["passed"] > 0:
            print(f"  [OK] Mock Services: {result['passed']}/{result['total']} tests passed")
            return True
        else:
            print(f"  [WARN] Mock Services: No tests passed")
            return False
            
    except Exception as e:
        print(f"  [ERR] Mock Services: {e}")
        return False


def test_error_recovery():
    """测试错误恢复"""
    print("\n[2/7] Testing Error Recovery...")
    
    try:
        from error_recovery import ErrorRecoveryManager, ErrorSeverity
        
        manager = ErrorRecoveryManager()
        
        # 模拟错误
        record = manager.record_error(
            error=ConnectionError("Test error"),
            component="test",
            severity=ErrorSeverity.MEDIUM
        )
        
        # 尝试恢复
        result = manager.attempt_recovery(record)
        
        summary = manager.get_error_summary()
        
        print(f"  [OK] Error Recovery: {summary['total']} errors, {summary['recovery_rate']*100:.0f}% recovery rate")
        return True
        
    except Exception as e:
        print(f"  [ERR] Error Recovery: {e}")
        return False


def test_audit_logger():
    """测试审计日志"""
    print("\n[3/7] Testing Audit Logger...")
    
    try:
        from audit_logger import AuditLogger, AuditCategory
        
        logger = AuditLogger()
        
        # 记录日志
        logger.info(AuditCategory.SYSTEM, "test.start")
        logger.action(AuditCategory.FILE_ACCESS, "file.read", target="test.txt")
        logger.log_command("ls -la", 0)
        
        stats = logger.get_statistics()
        
        print(f"  [OK] Audit Logger: {stats['total_in_memory']} records in memory")
        
        logger.close()
        return True
        
    except Exception as e:
        print(f"  [ERR] Audit Logger: {e}")
        return False


def test_team_registry():
    """测试团队注册表"""
    print("\n[4/7] Testing Team Registry...")
    
    try:
        from team_registry import TeamRegistry, create_research_team
        
        team = create_research_team()
        
        # 创建任务
        task = team.create_task(
            name="Test Task",
            description="A test task",
            required_capabilities=["web_search"]
        )
        
        # 分配任务
        assigned = team.assign_task(task.task_id)
        
        # 获取状态
        status = team.get_team_status()
        
        print(f"  [OK] Team Registry: {len(status['agents'])} agents, task assigned: {assigned}")
        
        team.close()
        return True
        
    except Exception as e:
        print(f"  [ERR] Team Registry: {e}")
        return False


def test_config_validator():
    """测试配置验证器"""
    print("\n[5/7] Testing Config Validator...")
    
    try:
        from config_validator import ConfigValidator, ValidationLevel
        
        validator = ConfigValidator()
        
        test_config = {
            "session": {
                "retention_days": None,
                "compression_enabled": True
            },
            "cache": {
                "max_size_mb": 200  # 有效值
            }
        }
        
        issues = validator.validate(test_config)
        
        errors = sum(1 for i in issues if i.level == ValidationLevel.ERROR)
        warnings = sum(1 for i in issues if i.level == ValidationLevel.WARNING)
        
        print(f"  [OK] Config Validator: {len(issues)} issues ({errors} errors, {warnings} warnings)")
        return True
        
    except Exception as e:
        print(f"  [ERR] Config Validator: {e}")
        return False


def test_smart_predictor():
    """测试智能预测器"""
    print("\n[6/7] Testing Smart Predictor...")
    
    try:
        from smart_predictor import create_default_predictor
        
        predictor = create_default_predictor()
        
        # 记录指标
        for i in range(10):
            predictor.record("memory_usage_percent", 50 + i * 2)
        
        # 检查预警
        predictor.check_alerts()
        
        # 预测
        pred = predictor.predict("memory_usage_percent", horizon_minutes=10)
        
        active_alerts = len(predictor.get_active_alerts())
        
        print(f"  [OK] Smart Predictor: {active_alerts} active alerts, prediction available: {pred is not None}")
        
        predictor.close()
        return True
        
    except Exception as e:
        print(f"  [ERR] Smart Predictor: {e}")
        return False


def test_integration():
    """测试集成"""
    print("\n[7/7] Testing Integration...")
    
    try:
        # 验证所有模块可以一起导入
        from mock_services import MockServiceRegistry
        from error_recovery import ErrorRecoveryManager
        from audit_logger import AuditLogger
        from team_registry import TeamRegistry
        from config_validator import ConfigValidator
        from smart_predictor import SmartPredictor
        
        print("  [OK] Integration: All Phase 4 modules imported successfully")
        return True
        
    except Exception as e:
        print(f"  [ERR] Integration: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("Phase 4 Module Verification")
    print("=" * 60)
    
    tests = [
        test_mock_services,
        test_error_recovery,
        test_audit_logger,
        test_team_registry,
        test_config_validator,
        test_smart_predictor,
        test_integration
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"  [ERR] Test failed with exception: {e}")
            results.append(False)
        time.sleep(0.1)
    
    # 汇总
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 60)
    print(f"Phase 4 Verification Results: {passed}/{total} passed")
    print("=" * 60)
    
    if passed == total:
        print("All Phase 4 modules are working correctly!")
        return 0
    else:
        print("Some modules have issues. Check output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
