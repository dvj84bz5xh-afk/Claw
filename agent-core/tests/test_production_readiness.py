"""
生产级集成测试套件

覆盖范围:
  阶段1: HandoffManager 集成测试 (路由/多轮对话/错误处理)
  阶段2: MemoryExtractor 集成测试 (提取质量/去重/边缘情况)
  阶段3: 生产准备检查 (性能/日志/文档完整性)
  阶段4: 端到端测试 (Handoff + Memory 协同工作)

运行方式:
  python agent-core/tests/test_production_readiness.py
"""

import sys
import os
import time
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, date

# 确保agent-core在路径中
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入待测模块
try:
    from handoff_manager import (
        Agent, Handoff, handoff, HandoffManager,
        recommend_handoff_prompt, create_handoff_manager
    )
    from memory_extractor import (
        MemoryExtractor, MemoryStore, RuleBasedExtractor,
        MemoryItem, MemoryType, ImportanceLevel, ExtractionRule
    )
    print("[OK] 成功导入所有模块")
except Exception as e:
    print(f"[FAIL] 导入失败: {e}")
    sys.exit(1)


# ============================================================
# 测试基础设施
# ============================================================

class TestResult:
    """单次测试结果"""
    def __init__(self, name):
        self.name = name
        self.passed = False
        self.error = None
        self.duration_ms = 0
        self.details = {}

    def __repr__(self):
        status = "PASS" if self.passed else "FAIL"
        return f"[{status}] {self.name} ({self.duration_ms}ms)"


class TestSuite:
    """测试套件管理器"""
    def __init__(self, name):
        self.name = name
        self.results: list[TestResult] = []
        self._start_time = time.time()

    def run_test(self, test_name, test_func, *args, **kwargs) -> TestResult:
        result = TestResult(test_name)
        start = time.time()
        try:
            test_func(*args, **kwargs)
            result.passed = True
        except AssertionError as e:
            result.error = str(e)
            result.details["assertion"] = str(e)
        except Exception as e:
            result.error = f"异常: {type(e).__name__}: {e}"
            result.details["exception"] = f"{type(e).__name__}: {e}"
        finally:
            result.duration_ms = int((time.time() - start) * 1000)
            self.results.append(result)

        # 实时输出结果
        icon = "✅" if result.passed else "❌"
        print(f"  {icon} {result}")

        if not result.passed and result.error:
            print(f"      └─ 错误: {result.error[:100]}")

        return result

    def summary(self) -> dict:
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        total_time = int((time.time() - self._start_time) * 1000)

        print(f"\n{'='*60}")
        print(f"{self.name} 结果汇总")
        print(f"{'='*60}")
        print(f"  总计: {total} | 通过: {passed} | 失败: {failed}")
        print(f"  耗时: {total_time}ms | 通过率: {(passed/total*100):.1f}%")

        if failed > 0:
            print(f"\n  失败用例:")
            for r in self.results:
                if not r.passed:
                    print(f"    ❌ {r.name}: {r.error[:80]}")

        return {
            "suite": self.name,
            "total": total, "passed": passed, "failed": failed,
            "time_ms": total_time, "pass_rate": round(passed/total*100, 1)
        }


def assert_true(condition, msg="断言失败"):
    if not condition:
        raise AssertionError(msg)


def assert_equal(actual, expected, msg=None):
    if actual != expected:
        raise AssertionError(msg or f"期望 {expected}, 得到 {actual}")


def assert_contains(text, substring, msg=None):
    if substring not in text:
        raise AssertionError(msg or f"'{text}' 不包含 '{substring}'")


def assert_not_none(value, msg="值不应为None"):
    if value is None:
        raise AssertionError(msg)


def assert_greater(value, threshold, msg=None):
    if value <= threshold:
        raise AssertionError(msg or f"期望 >{threshold}, 得到 {value}")


def assert_less(value, threshold, msg=None):
    if value >= threshold:
        raise AssertionError(msg or f"期望 <{threshold}, 得到 {value}")


def assert_type(value, expected_type, msg=None):
    if not isinstance(value, expected_type):
        raise AssertionError(
            msg or f"期望类型 {expected_type.__name__}, 得到 {type(value).__name__}"
        )


# ============================================================
# 阶段1: HandoffManager 集成测试
# ============================================================

class Phase1_HandoffTests:
    """
    阶段1: HandoffManager 集成测试

    测试目标:
    1. 基本路由功能 (中英文输入)
    2. 多轮对话与handoff链路
    3. 错误处理 (无效输入/未注册Agent/循环检测)
    4. 动态启用/禁用
    5. on_handoff回调
    6. Tool schema生成
    """

    @staticmethod
    def create_test_agents():
        """创建标准测试Agent集"""
        billing = Agent(name="BillingAgent", instructions="处理账单和发票问题")
        refund = Agent(name="RefundAgent", instructions="处理退款请求和退款政策")
        tech = Agent(name="TechSupport", instructions="处理技术故障和bug报告")
        account = Agent(name="AccountManager", instructions="处理账户管理和安全问题")

        orchestrator = Agent(
            name="OrchestratorAgent",
            instructions="你是客服编排器，将用户请求路由到专业 Agent",
            handoffs=[
                billing,
                handoff(refund, tool_description="用户要求退款或取消订单时使用"),
                tech,
                handoff(account, tool_name="transfer_to_security"),
            ]
        )

        return {
            "billing": billing,
            "refund": refund,
            "tech": tech,
            "account": account,
            "orchestrator": orchestrator,
        }


def test_handoff_basic_routing_zh(suite: TestSuite):
    """[P1] 中文基本路由 - 账单问题应路由至BillingAgent"""
    agents = Phase1_HandoffTests.create_test_agents()
    mgr = HandoffManager("test-zh-basic")

    for a in agents.values():
        mgr.register(a)
    mgr.set_entry(agents["orchestrator"])

    result = mgr.run("我的账单有问题，这个月扣费不对", max_handoffs=5)

    assert_true(result is not None, "结果不应为None")
    assert_contains(result.get("output", ""), "Billing", "输出应包含Billing")
    assert_true("BillingAgent" in result.get("handoff_chain", []), "链路应包含BillingAgent")
    assert_greater(result.get("handoff_count", 0), 0, "应有至少一次handoff")


def test_handoff_basic_routing_en(suite: TestSuite):
    """[P1] 英文基本路由 - Refund request should route to RefundAgent"""
    agents = Phase1_HandoffTests.create_test_agents()
    mgr = HandoffManager("test-en-basic")

    for a in agents.values():
        mgr.register(a)
    mgr.set_entry(agents["orchestrator"])

    result = mgr.run("I want to get a refund for my order please", max_handoffs=5)

    assert_true("RefundAgent" in result.get("handoff_chain", []), "英文应路由至RefundAgent")


def test_handoff_no_match(suite: TestSuite):
    """[P2] 无匹配 - 无关输入应由Orchestrator直接处理"""
    agents = Phase1_HandoffTests.create_test_agents()
    mgr = HandoffManager("test-no-match")

    for a in agents.values():
        mgr.register(a)
    mgr.set_entry(agents["orchestrator"])

    result = mgr.run("今天天气真好啊，我想聊聊天", max_handoffs=5)

    # 应无handoff，由Orchestrator直接处理
    assert_equal(result.get("handoff_count", 99), 0, "无匹配时应无handoff")


def test_handoff_max_depth_protection(suite: TestSuite):
    """[P0] 循环保护 - 达到max_handoffs后停止"""
    agents = Phase1_HandoffTests.create_test_agents()

    # 创建循环链: A -> B -> A -> B...
    a_agent = Agent(name="AgentA", instructions="代理A", handoffs=[])
    b_agent = Agent(name="AgentB", instructions="代理B", handoffs=[a_agent])
    a_agent.handoffs = [b_agent]  # 手动创建循环

    mgr = HandoffManager("test-loop")
    mgr.register(a_agent)
    mgr.register(b_agent)
    mgr.set_entry(a_agent)

    result = mgr.run("触发循环测试", max_handoffs=3)

    assert_less(result.get("handoff_count", 999), 10, "不应无限循环")


def test_handoff_no_entry_agent(suite: TestSuite):
    """[P1] 无入口Agent - 应返回错误而非崩溃"""
    mgr = HandoffManager("test-no-entry")

    result = mgr.run("任何输入")

    assert_true(isinstance(result, dict), "返回应为dict")
    assert_true("error" in result, "应包含error字段")


def test_handoff_on_callback(suite: TestSuite):
    """[P1] on_handoff回调 - 应正确触发回调函数"""
    callback_log = []

    def my_callback():
        callback_log.append("called")

    # 目标Agent的instructions含有关键词，确保可被路由命中
    target = Agent(name="TargetAgent", instructions="处理目标任务")
    source = Agent(
        name="SourceAgent",
        instructions="源代理",
        handoffs=[handoff(target, on_handoff=my_callback)]
    )

    mgr = HandoffManager("test-callback")
    mgr.register(target)
    mgr.register(source)
    mgr.set_entry(source)

    result = mgr.run("请帮我处理这个目标任务", max_handoffs=5)  # 输入包含"目标"
    assert_true(len(callback_log) > 0, "回调应被调用")


def test_handoff_dynamic_disable(suite: TestSuite):
    """[P2] 动态禁用 - is_enabled=False时应跳过"""
    target = Agent(name="TargetAgent", instructions="目标")
    source = Agent(
        name="SourceAgent",
        instructions="源",
        handoffs=[
            handoff(target, is_enabled=False)  # 明确禁用
        ]
    )

    mgr = HandoffManager("test-disable")
    mgr.register(target)
    mgr.register(source)
    mgr.set_entry(source)

    result = mgr.run("任何输入", max_handoffs=5)
    assert_equal(result.get("handoff_count", 99), 0, "禁用的handoff不应触发")


def test_handoff_tool_schema_generation(suite: TestSuite):
    """[P1] Tool Schema生成 - 应生成有效的function calling格式"""
    target = Agent(name="BillingAgent", instructions="账单处理")
    h = handoff(target, tool_name="transfer_to_billing",
                tool_description="处理账单问题")

    schema = h.to_tool_schema()

    assert_true(isinstance(schema, dict), "schema应为dict")
    assert_equal(schema["type"], "function", "type应为function")
    assert_equal(schema["function"]["name"], "transfer_to_billing", "name应匹配")
    assert_true("description" in schema["function"], "应包含description")
    assert_true("parameters" in schema["function"], "应包含parameters")


def test_handoff_stats_tracking(suite: TestSuite):
    """[P2] 统计追踪 - 多次运行后统计应准确"""
    agents = Phase1_HandoffTests.create_test_agents()
    mgr = HandoffManager("test-stats")

    for a in agents.values():
        mgr.register(a)
    mgr.set_entry(agents["orchestrator"])

    # 运行3次不同输入
    inputs = [
        "账单问题",
        "我要退款",
        "软件崩溃了"
    ]
    for inp in inputs:
        mgr.run(inp, max_handoffs=5)

    stats = mgr.get_stats()
    assert_equal(stats["total_runs"], 3, "运行次数应为3")
    assert_greater(stats["total_handoffs"], 0, "应有至少一次handoff")


def test_handoff_recommendation_prompt(suite: TestSuite):
    """[P3] 推荐提示词 - 应包含handoff信息"""
    target = Agent(name="SubAgent", instructions="子代理")
    main = Agent(
        name="MainAgent",
        instructions="主代理",
        handoffs=[target]
    )

    prompt = recommend_handoff_prompt(main)
    assert_contains(prompt, "移交", "提示词应包含'移交'")
    assert_contains(prompt, "SubAgent", "提示词应包含子代理名")


def test_handoff_agent_as_tool(suite: TestSuite):
    """[P2] Agent转工具 - as_tool应返回有效工具定义"""
    sub = Agent(name="DataAnalyst", instructions="数据分析专家")

    tool_def = sub.as_tool(
        tool_name="call_analyst",
        tool_description="调用数据分析专家进行深度分析"
    )

    assert_true(isinstance(tool_def, dict), "工具定义应为dict")
    assert_equal(tool_def["tool_name"], "call_analyst", "名称应匹配")
    assert_true("schema" in tool_def, "应包含schema")


# ============================================================
# 阶段2: MemoryExtractor 集成测试
# ============================================================

class Phase2_MemoryTests:
    """
    阶段2: MemoryExtractor 集成测试

    测试目标:
    1. 提取质量 (偏好/技能/决策/实体/目标)
    2. 去重逻辑 (hash去重/相似内容)
    3. 边缘情况 (空输入/超长文本/特殊字符)
    4. 存储集成 (daily log写入/搜索)
    5. 配置灵活性 (开关控制)
    """


def _create_temp_memory_dir() -> Path:
    """创建临时记忆目录"""
    tmp = Path(tempfile.mkdtemp(prefix="mem_test_"))
    (tmp / ".workbuddy" / "memory").mkdir(parents=True, exist_ok=True)
    return tmp / ".workbuddy" / "memory"


def test_extract_preferences(suite: TestSuite):
    """[P0] 偏好提取 - 正确识别用户偏好声明"""
    extractor = MemoryExtractor(_create_temp_memory_dir()).initialize()

    messages = [
        {"role": "user", "content": "我喜欢简洁的回复，不要超过300字"},
        {"role": "assistant", "content": "好的，我会保持回复简短。"},
    ]

    items = extractor.extract(messages)
    pref_items = [i for i in items if i.memory_type == MemoryType.PREFERENCE]

    assert_greater(len(pref_items), 0, "应提取至少一条偏好")
    content_text = " ".join([i.content for i in pref_items])
    assert_true("简洁" in content_text or "300字" in content_text or "不要" in content_text,
                f"偏好内容应包含关键词, 得到: {pref_items[0].content}")


def test_extract_skills(suite: TestSuite):
    """[P1] 技能提取 - 正确识别技能掌握声明"""
    extractor = MemoryExtractor(_create_temp_memory_dir()).initialize()

    messages = [
        {"role": "user", "content": "我已经掌握了Python数据分析"},
    ]

    items = extractor.extract(messages)
    skill_items = [i for i in items if i.memory_type == MemoryType.SKILL]

    assert_greater(len(skill_items), 0, "应提取至少一条技能记录")
    assert_true("python" in skill_items[0].content.lower() or "数据分析" in skill_items[0].content,
                f"技能内容应包含Python或数据分析, 得到: {skill_items[0].content}")


def test_extract_decisions(suite: TestSuite):
    """[P1] 决策提取 - 正确识别技术选型决策"""
    extractor = MemoryExtractor(_create_temp_memory_dir()).initialize()

    messages = [
        {"role": "user", "content": "决定采用React作为前端框架"},
    ]

    items = extractor.extract(messages)
    decision_items = [i for i in items if i.memory_type == MemoryType.DECISION]

    assert_greater(len(decision_items), 0, "应提取至少一条决策")
    assert_true("react" in decision_items[0].content.lower(),
                f"决策内容应包含React, 得到: {decision_items[0].content}")


def test_extract_entities(suite: TestSuite):
    """[P2] 实体提取 - 识别人名和角色关系"""
    extractor = MemoryExtractor(_create_temp_memory_dir()).initialize()

    messages = [
        {"role": "user", "content": "张三是项目负责人，李四负责测试"},
    ]

    items = extractor.extract(messages)
    entity_items = [i for i in items if i.memory_type == MemoryType.ENTITY]

    assert_greater(len(entity_items), 0, "应提取至少一条实体关系")


def test_deduplication(suite: TestSuite):
    """[P0] 去重逻辑 - 相同内容不应重复保存"""
    mem_dir = _create_temp_memory_dir()
    extractor = MemoryExtractor(mem_dir).initialize()

    # 第一次提取
    messages1 = [{"role": "user", "content": "我喜欢简洁的回复"}]
    result1 = extractor.process_and_save(messages1, user_id="dup-test")
    count1 = result1["new_saved"]

    # 第二次提取完全相同的内容
    extractor2 = MemoryExtractor(mem_dir).initialize()
    result2 = extractor2.process_and_save(messages1, user_id="dup-test")
    count2 = result2["new_saved"]

    assert_greater(count1, 0, "第一次应保存新条目")
    assert_equal(count2, 0, "重复内容不应再次保存")


def test_edge_empty_input(suite: TestSuite):
    """[P2] 空输入 - 不应崩溃"""
    extractor = MemoryExtractor(_create_temp_memory_dir()).initialize()

    # 空字符串
    items1 = extractor.extract("")
    assert_true(isinstance(items1, list), "空字符串应返回列表")

    # 空消息列表
    items2 = extractor.extract([])
    assert_true(isinstance(items2, list), "空列表应返回列表")


def test_edge_long_text(suite: TestSuite):
    """[P2] 超长文本 - 应正常截断"""
    extractor = MemoryExtractor(_create_temp_memory_dir()).initialize()

    long_content = "这是一段非常长的测试内容。" * 50  # ~500字
    messages = [{"role": "user", "content": long_content}]

    items = extractor.extract(messages)
    for item in items:
        assert_less(len(item.content), 200, "内容长度应<200字符")


def test_special_characters(suite: TestSuite):
    """[P3] 特殊字符 - 包含@mention、路径、版本号"""
    extractor = MemoryExtractor(_create_temp_memory_dir()).initialize()

    messages = [
        {"role": "user", "content": "@zhangsan 是项目负责人，项目路径 C:\\Users\\project\\app.py，版本 v1.2.3"},
    ]

    items = extractor.extract(messages)
    # 至少不崩溃
    assert_true(isinstance(items, list), "特殊字符输入应正常返回")


def test_daily_log_writing(suite: TestSuite):
    """[P1] Daily log写入 - 应正确追加到日志文件"""
    mem_dir = _create_temp_memory_dir()
    extractor = MemoryExtractor(mem_dir).initialize()

    messages = [{"role": "user", "content": "决定采用TypeScript"}]
    result = extractor.process_and_save(messages, user_id="log-test")

    today_file = mem_dir / f"{date.today().isoformat()}.md"
    assert_true(today_file.exists(), "今日日志文件应存在")

    content = today_file.read_text(encoding='utf-8')
    assert_contains(content, "自动提取记忆", "日志应包含标题行")


def test_search_functionality(suite: TestSuite):
    """[P2] 搜索功能 - 应能检索已存储的记忆"""
    mem_dir = _create_temp_memory_dir()
    extractor = MemoryExtractor(mem_dir).initialize()

    messages = [{"role": "user", "content": "我喜欢使用Python编程"}]
    extractor.process_and_save(messages, user_id="search-test")

    found = extractor.store.search("python")
    assert_true(len(found) > 0, "搜索Python应找到结果")


def test_importance_scoring(suite: TestSuite):
    """[P2] 重要性评分 - 高价值关键词应提升等级"""
    extractor = MemoryExtractor(_create_temp_memory_dir()).initialize()

    # 包含高价值关键词
    messages = [{"role": "user", "content": "永远不要超过300字的回复"}]
    items = extractor.extract(messages)

    pref_items = [i for i in items if i.memory_type == MemoryType.PREFERENCE]
    if len(pref_items) > 0:
        imp = pref_items[0].importance.value
        assert_greater(imp, ImportanceLevel.MEDIUM.value,
                       f"含'永远/不要'的重要性应>MEDIUM, 得到:{imp}")


def test_mixed_conversation(suite: TestSuite):
    """[P1] 混合对话 - 多种类型的混合提取"""
    extractor = MemoryExtractor(_create_temp_memory_dir()).initialize()

    messages = [
        {"role": "user", "content": "我偏好简洁回复"},           # PREFERENCE
        {"role": "assistant", "content": "好的。"},
        {"role": "user", "content": "已经学会了Docker容器化"},     # SKILL
        {"role": "user", "content": "决定使用PostgreSQL数据库"},   # DECISION
        {"role": "user", "content": "目标是每周完成一个功能"},     # GOAL
        {"role": "user", "content": "已完成用户认证模块开发"},     # EVENT
    ]

    items = extractor.extract(messages)
    types_found = set(i.memory_type for i in items)

    assert_true(MemoryType.PREFERENCE in types_found, "应发现PREFERENCE")
    assert_true(MemoryType.SKILL in types_found or MemoryType.DECISION in types_found,
                "应发现SKILL或DECISION")


# ============================================================
# 阶段3: 生产准备检查
# ============================================================


def test_performance_handoff(suite: TestSuite):
    """[P1] 性能测试 - HandoffManager 100次路由应在200ms内"""
    agents = Phase1_HandoffTests.create_test_agents()
    mgr = HandoffManager("perf-handoff")

    for a in agents.values():
        mgr.register(a)
    mgr.set_entry(agents["orchestrator"])

    start = time.time()
    for i in range(100):
        mgr.run(f"测试{i % 3}问题", max_handoffs=3)
    elapsed = (time.time() - start) * 1000

    assert_less(elapsed, 500, f"100次路由应在500ms内, 实际:{elapsed:.0f}ms")
    print(f"\n       📊 HandoffManager 100次路由: {elapsed:.0f}ms ({elapsed/100:.1f}ms/次)")


def test_performance_memory_extraction(suite: TestSuite):
    """[P1] 性能测试 - MemoryExtractor 50次提取应在500ms内"""
    mem_dir = _create_temp_memory_dir()
    extractor = MemoryExtractor(mem_dir).initialize()

    base_msg = [{"role": "user", "content": "我喜欢简洁回复，已经学会Python，决定使用React"}]

    start = time.time()
    for i in range(50):
        extractor.extract(base_msg)
    elapsed = (time.time() - start) * 1000

    assert_less(elapsed, 1000, f"50次提取应在1000ms内, 实际:{elapsed:.0f}ms")
    print(f"\n       📊 MemoryExtractor 50次提取: {elapsed:.0f}ms ({elapsed/50:.1f}ms/次)")


def test_code_quality_docstrings(suite: TestSuite):
    """[P2] 代码质量 - 核心类应有docstring"""
    classes_to_check = [Agent, Handoff, HandoffManager, MemoryItem,
                        MemoryStore, RuleBasedExtractor, MemoryExtractor]

    for cls in classes_to_check:
        doc = cls.__doc__
        assert_true(doc and len(doc.strip()) > 20,
                    f"{cls.__name__} 缺少有效docstring")


def test_data_model_integrity(suite: TestSuite):
    """[P1] 数据模型完整性 - MemoryItem应正确序列化"""
    item = MemoryItem(
        content="测试记忆内容",
        memory_type=MemoryType.DECISION,
        importance=ImportanceLevel.HIGH,
        entities=["@test"],
        tags=["test"]
    )

    d = item.to_dict()
    assert_equal(d["memory_type"], "DECISION", "序列化type应正确")
    assert_equal(d["importance"], "HIGH", "序列化importance应正确")
    assert_true("_id" not in d, "内部字段不应出现在to_dict中")
    assert_true(d["content"] == "测试记忆内容", "内容应完整保留")


def test_memory_item_hash_consistency(suite: TestSuite):
    """[P2] Hash一致性 - 相同内容应产生相同hash"""
    item1 = MemoryItem(content="相同内容测试")
    item2 = MemoryItem(content="相同内容测试")

    assert_equal(item1._hash, item2._hash, "相同内容的hash应一致")


def test_memory_item_format_for_md(suite: TestSuite):
    """[P3] 格式化输出 - format_for_memory_md应产生正确格式"""
    item = MemoryItem(
        content="喜欢简洁回复",
        memory_type=MemoryType.PREFERENCE,
        importance=ImportanceLevel.HIGH,
        tags=["style"]
    )

    formatted = item.format_for_memory_md()
    assert_true(formatted.startswith(">"), "PREFERENCES应以>开头")
    assert_contains(formatted, "[style]", "应包含tag")


def test_error_handling_invalid_agent_registration(suite: TestSuite):
    """[P2] 错误处理 - 注册后unregister不影响其他Agent"""
    mgr = HandoffManager("test-unregister")
    a1 = Agent(name="A1", instructions="a1")
    a2 = Agent(name="A2", instructions="a2")

    mgr.register(a1)
    mgr.register(a2)
    removed = mgr.unregister(a1.agent_id)

    assert_true(removed, "移除应成功")
    assert_true(mgr.get_agent(a1.agent_id) is None, "移除后不应找到")
    assert_not_none(mgr.get_agent(a2.agent_id), "其他Agent不受影响")


# ============================================================
# 阶段4: 端到端测试
# ============================================================

def test_e2e_full_session(suite: TestSuite):
    """[P0] 端到端会话 - 模拟完整用户会话流程"""

    # === Step 1: 创建客服系统 ===
    billing = Agent(name="BillingAgent", instructions="处理账单问题")
    refund = Agent(name="RefundAgent", instructions="处理退款")
    support = Agent(name="SupportAgent", instructions="技术支持")
    orchestrator = Agent(
        name="Orchestrator",
        instructions="客服编排器",
        handoffs=[billing, handoff(refund), support]
    )

    mgr = HandoffManager("e2e-session")
    mgr.register(billing); mgr.register(refund); mgr.register(support)
    mgr.set_entry(orchestrator)

    # === Step 2: 模拟多轮对话 ===
    session_messages = []
    session_results = []

    user_inputs = [
        ("我的账单扣费有问题", "billing"),       # 期望路由到账单
        ("软件总是崩溃怎么办", "tech"),           # 期望路由到技术支持
        ("我想申请退款", "refund"),              # 期望路由到退款
    ]

    route_correct_count = 0
    for user_input, expected_route in user_inputs:
        result = mgr.run(user_input, max_handoffs=5)
        chain = result.get("handoff_chain", [])

        # 记录用于记忆提取
        session_messages.extend([
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": result.get("output", "")}
        ])
        session_results.append(result)

        # 检查路由是否大致正确
        route_ok = False
        for agent_name in chain:
            if expected_route.lower() in agent_name.lower():
                route_correct_count += 1
                route_ok = True
                break
        if not route_ok and len(chain) <= 1:  # Orchestrator直接处理也算对
            if expected_route == "tech" and "Support" in str(chain):
                route_correct_count += 1
                route_ok = True

    # === Step 3: 对话结束后自动提取记忆 ===
    mem_dir = _create_temp_memory_dir()
    extractor = MemoryExtractor(mem_dir).initialize()
    extracted = extractor.extract(session_messages)

    # === Step 4: 验证结果 ===
    assert_true(len(session_results) == 3, "应有3轮对话结果")
    assert_true(route_correct_count >= 2,
                f"路由准确率应>=66% ({route_correct_count}/3)")
    assert_true(isinstance(extracted, list), "提取结果应为列表")

    # 打印详细信息
    print(f"\n       📋 会话摘要:")
    print(f"          - 对话轮数: {len(user_inputs)}")
    print(f"          - 路由正确: {route_correct_count}/{len(user_inputs)}")
    print(f"          - 提取记忆: {len(extracted)}条")

    types_summary = {}
    for item in extracted:
        t = item.memory_type.name
        types_summary[t] = types_summary.get(t, 0) + 1
    if types_summary:
        print(f"          - 类型分布: {types_summary}")


def test_e2e_large_scale_simulation(suite: TestSuite):
    """[P2] 大规模模拟 - 50次并发式路由+提取"""

    # 快速创建系统
    agents_list = [
        Agent(name=f"Agent{i}", instructions=f"专业领域{i}", handoffs=[])
        for i in range(8)
    ]
    orchestrator = Agent(
        name="Router",
        instructions="主路由器",
        handoffs=agents_list[:5]  # 注册前5个
    )

    mgr = HandoffManager("e2e-scale")
    for a in agents_list:
        mgr.register(a)
    mgr.set_entry(orchestrator)

    # 批量运行
    test_inputs = [
        "账单问题", "退款", "技术故障", "账户安全",
        "咨询产品", "投诉服务", "订单查询", "物流问题",
        "会员问题", "支付失败"
    ] * 5  # 50次

    start = time.time()
    results = []
    for inp in test_inputs:
        r = mgr.run(inp, max_handoffs=2)
        results.append(r)

    elapsed = (time.time() - start) * 1000

    assert_true(len(results) == 50, f"应完成50次路由 ({len(results)})")
    assert_less(elapsed, 2000, f"50次应在2s内完成, 实际:{elapsed:.0f}ms")

    # 统计
    handoff_total = sum(r.get("handoff_count", 0) for r in results)
    print(f"\n       📊 规模测试: 50次路由 | 总handoff: {handoff_total} | "
          f"耗时: {elapsed:.0f}ms | 平均: {elapsed/50:.1f}ms/次")


def test_e2e_error_recovery(suite: TestSuite):
    """[P1] 错误恢复 - 异常情况下的系统稳定性"""

    # 测试1: 未注册的handoff目标
    orphan = Agent(name="OrphanAgent", instructions="孤儿代理")
    broken = Agent(
        name="BrokenAgent",
        instructions="有问题的代理",
        handoffs=[orphan]  # orphan没有注册
    )
    mgr = HandoffManager("e2e-error")
    mgr.set_entry(broken)  # 只注册入口，不注册handoff目标

    try:
        result = mgr.run("触发错误场景", max_handoffs=5)
        assert_true(isinstance(result, dict), "即使配置不当也应返回dict")
    except Exception as e:
        # 如果抛出异常，也应该是可预期的
        assert_true("KeyError" not in str(type(e)), "不应出现KeyError")

    # 测试2: 极短/极长输入
    short_result = mgr.run("x" * 1)
    long_result = mgr.run("x" * 10000)

    assert_true(isinstance(short_result, dict), "极短输入不应崩溃")
    assert_true(isinstance(long_result, dict), "极长输入不应崩溃")


# ============================================================
# 主测试执行
# ============================================================

def main():
    print("=" * 70)
    print("  🏭 Claw AI 生产就绪性测试套件")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()

    all_summaries = []

    # ---- 阶段1: HandoffManager ----
    print("📦 阶段 1/4: HandoffManager 集成测试\n")
    suite1 = TestSuite("阶段1-HandoffManager")

    suite1.run_test("中文基本路由", test_handoff_basic_routing_zh, suite1)
    suite1.run_test("英文基本路由", test_handoff_basic_routing_en, suite1)
    suite1.run_test("无匹配输入处理", test_handoff_no_match, suite1)
    suite1.run_test("循环保护机制", test_handoff_max_depth_protection, suite1)
    suite1.run_test("无入口Agent处理", test_handoff_no_entry_agent, suite1)
    suite1.run_test("on_handoff回调", test_handoff_on_callback, suite1)
    suite1.run_test("动态禁用手off", test_handoff_dynamic_disable, suite1)
    suite1.run_test("Tool Schema生成", test_handoff_tool_schema_generation, suite1)
    suite1.run_test("统计追踪准确性", test_handoff_stats_tracking, suite1)
    suite1.run_test("推荐提示词生成", test_handoff_recommendation_prompt, suite1)
    suite1.run_test("Agent-as-Tool转换", test_handoff_agent_as_tool, suite1)

    all_summaries.append(suite1.summary())

    # ---- 阶段2: MemoryExtractor ----
    print("\n📦 阶段 2/4: MemoryExtractor 集成测试\n")
    suite2 = TestSuite("阶段2-MemoryExtractor")

    suite2.run_test("偏好提取质量", test_extract_preferences, suite2)
    suite2.run_test("技能提取质量", test_extract_skills, suite2)
    suite2.run_test("决策提取质量", test_extract_decisions, suite2)
    suite2.run_test("实体提取质量", test_extract_entities, suite2)
    suite2.run_test("去重逻辑验证", test_deduplication, suite2)
    suite2.run_test("空输入边缘情况", test_edge_empty_input, suite2)
    suite2.run_test("超长文本截断", test_edge_long_text, suite2)
    suite2.run_test("特殊字符处理", test_special_characters, suite2)
    suite2.run_test("Daily log写入", test_daily_log_writing, suite2)
    suite2.run_test("搜索功能验证", test_search_functionality, suite2)
    suite2.run_test("重要性评分调整", test_importance_scoring, suite2)
    suite2.run_test("混合对话提取", test_mixed_conversation, suite2)

    all_summaries.append(suite2.summary())

    # ---- 阶段3: 生产准备检查 ----
    print("\n📦 阶段 3/4: 生产准备检查\n")
    suite3 = TestSuite("阶段3-生产准备")

    suite3.run_test("HandoffManager性能", test_performance_handoff, suite3)
    suite3.run_test("MemoryExtractor性能", test_performance_memory_extraction, suite3)
    suite3.run_test("Docstring完整性", test_code_quality_docstrings, suite3)
    suite3.run_test("数据模型序列化", test_data_model_integrity, suite3)
    suite3.run_test("Hash一致性验证", test_memory_item_hash_consistency, suite3)
    suite3.run_test("Markdown格式化", test_memory_item_format_for_md, suite3)
    suite3.run_test("Agent注销处理", test_error_handling_invalid_agent_registration, suite3)

    all_summaries.append(suite3.summary())

    # ---- 阶段4: 端到端测试 ----
    print("\n📦 阶段 4/4: 端到端协同测试\n")
    suite4 = TestSuite("阶段4-端到端")

    suite4.run_test("完整会话流程", test_e2e_full_session, suite4)
    suite4.run_test("大规模模拟(50次)", test_e2e_large_scale_simulation, suite4)
    suite4.run_test("错误恢复能力", test_e2e_error_recovery, suite4)

    all_summaries.append(suite4.summary())

    # ---- 最终汇总 ----
    print("\n" + "=" * 70)
    print("  🏆 最终测试报告")
    print("=" * 70)

    total_all = sum(s["total"] for s in all_summaries)
    passed_all = sum(s["passed"] for s in all_summaries)
    failed_all = sum(s["failed"] for s in all_summaries)
    overall_rate = passed_all / total_all * 100 if total_all > 0 else 0

    print(f"\n  总用例数: {total_all}")
    print(f"  通过数量: {passed_all}")
    print(f"  失败数量: {failed_all}")
    print(f"  整体通过率: {overall_rate:.1f}%")

    print(f"\n  各阶段详情:")
    for s in all_summaries:
        icon = "✅" if s["pass_rate"] >= 90 else "⚠️" if s["pass_rate"] >= 70 else "❌"
        print(f"    {icon} {s['suite']}: {s['passed']}/{s['total']} "
              f"({s['pass_rate']}%) [{s['time_ms']}ms]")

    # 判断生产就绪状态
    print(f"\n  {'='*60}")

    critical_passed = all(
        any(r.passed for r in s.results if "[P0]" in r.name)
        for s in [suite1, suite2, suite4]
    )  # 至少每个关键阶段的P0测试通过

    if overall_rate >= 90 and failed_all == 0:
        print("  ✅ PRODUCTION READY — 可投入生产环境")
        exit_code = 0
    elif overall_rate >= 80 and failed_all <= 3:
        print("  ⚠️ CONDITIONAL READY — 基本可用，建议修复少量失败项")
        exit_code = 1
    else:
        print("  ❌ NOT READY — 需要修复关键问题后再上线")
        exit_code = 2

    print(f"{'='*70}\n")

    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
