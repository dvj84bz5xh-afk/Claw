"""
Hermes Agent 借鉴优化：增强持久记忆系统
基于 Hermes Agent 的记忆设计理念，增强现有记忆系统的存储、检索和关联能力。
"""

import json
import os
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
import hashlib
from pathlib import Path
import pickle

class MemoryType(Enum):
    """记忆类型枚举，借鉴 Hermes 的分类思想"""
    FACT = "fact"           # 事实信息
    PREFERENCE = "preference"  # 用户偏好
    PROJECT = "project"     # 项目相关信息
    SKILL = "skill"         # 技能知识
    DECISION = "decision"   # 决策记录
    CONTEXT = "context"     # 会话上下文
    INSIGHT = "insight"     # 洞察分析
    TODO = "todo"          # 待办事项
    SOLUTION = "solution"   # 解决方案

class MemoryPriority(Enum):
    """记忆优先级，用于重要性评分"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class MemoryItem:
    """记忆项数据结构，类似 Hermes 的记忆单元"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    memory_type: MemoryType = MemoryType.FACT
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    priority: MemoryPriority = MemoryPriority.MEDIUM
    importance_score: float = 0.5  # 0-1重要性评分
    related_items: List[str] = field(default_factory=list)  # 相关记忆ID
    metadata: Dict[str, Any] = field(default_factory=dict)  # 扩展元数据
    
    # 来源信息
    source: str = "system"  # 来源：system, user, agent, external
    session_id: Optional[str] = None  # 所属会话ID
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，用于序列化"""
        data = asdict(self)
        # 处理datetime对象
        data['created_at'] = self.created_at.isoformat()
        data['accessed_at'] = self.accessed_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        # 处理枚举
        data['memory_type'] = self.memory_type.value
        data['priority'] = self.priority.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        """从字典创建MemoryItem"""
        # 转换datetime
        for time_key in ['created_at', 'accessed_at', 'updated_at']:
            if time_key in data and isinstance(data[time_key], str):
                data[time_key] = datetime.fromisoformat(data[time_key])
        
        # 转换枚举
        if 'memory_type' in data and isinstance(data['memory_type'], str):
            data['memory_type'] = MemoryType(data['memory_type'])
        if 'priority' in data and isinstance(data['priority'], int):
            data['priority'] = MemoryPriority(data['priority'])
        
        return cls(**data)
    
    def calculate_content_hash(self) -> str:
        """计算内容哈希，用于去重"""
        content_str = f"{self.content}{self.memory_type.value}{''.join(sorted(self.tags))}"
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def update_access(self):
        """更新访问时间"""
        self.accessed_at = datetime.now()
    
    def add_relation(self, other_memory_id: str):
        """添加相关记忆"""
        if other_memory_id not in self.related_items:
            self.related_items.append(other_memory_id)
    
    def calculate_importance(self, access_count: int = 1) -> float:
        """计算重要性评分，基于优先级、类型、时效性等"""
        base_score = self.priority.value / 4.0  # 优先级权重 25%
        
        # 类型权重
        type_weights = {
            MemoryType.FACT: 0.8,
            MemoryType.PREFERENCE: 0.9,
            MemoryType.SKILL: 1.0,
            MemoryType.DECISION: 0.9,
            MemoryType.INSIGHT: 0.85,
            MemoryType.SOLUTION: 0.95
        }
        type_weight = type_weights.get(self.memory_type, 0.7)
        
        # 时效性衰减（按天计算）
        days_old = (datetime.now() - self.created_at).days
        recency_factor = max(0.1, 1.0 - (days_old / 365))  # 一年衰减到0.1
        
        # 访问频率
        frequency_factor = min(1.0, access_count / 100)
        
        self.importance_score = (base_score * 0.25 + type_weight * 0.35 + 
                                recency_factor * 0.25 + frequency_factor * 0.15)
        return self.importance_score

class MemoryManager:
    """记忆管理器，负责记忆的存储、检索和更新"""
    
    def __init__(self, memory_dir: str = ".workbuddy/memory_enhanced"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # 记忆索引
        self.memory_index: Dict[str, MemoryItem] = {}  # id -> MemoryItem
        self.tag_index: Dict[str, Set[str]] = {}  # tag -> set of memory ids
        self.type_index: Dict[MemoryType, Set[str]] = {}  # type -> set of memory ids
        self.content_hash_index: Dict[str, str] = {}  # content_hash -> memory_id (去重)
        
        # 统计信息
        self.access_counts: Dict[str, int] = {}  # memory_id -> access count
        
        self.load_memories()
    
    def save_memory(self, memory: MemoryItem) -> str:
        """保存记忆项"""
        # 检查是否重复
        content_hash = memory.calculate_content_hash()
        if content_hash in self.content_hash_index:
            # 更新现有记忆的访问时间
            existing_id = self.content_hash_index[content_hash]
            existing_memory = self.memory_index[existing_id]
            existing_memory.updated_at = datetime.now()
            existing_memory.update_access()
            self.access_counts[existing_id] = self.access_counts.get(existing_id, 0) + 1
            self._save_to_disk(existing_memory)
            return existing_id
        
        # 计算重要性
        memory.calculate_importance()
        
        # 添加到索引
        self.memory_index[memory.id] = memory
        self.content_hash_index[content_hash] = memory.id
        
        for tag in memory.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = set()
            self.tag_index[tag].add(memory.id)
        
        if memory.memory_type not in self.type_index:
            self.type_index[memory.memory_type] = set()
        self.type_index[memory.memory_type].add(memory.id)
        
        # 保存到磁盘
        self._save_to_disk(memory)
        
        # 初始化访问计数
        self.access_counts[memory.id] = 1
        
        return memory.id
    
    def get_memory(self, memory_id: str) -> Optional[MemoryItem]:
        """获取记忆项"""
        if memory_id not in self.memory_index:
            return None
        
        memory = self.memory_index[memory_id]
        memory.update_access()
        self.access_counts[memory_id] = self.access_counts.get(memory_id, 0) + 1
        
        # 定期重新计算重要性
        if self.access_counts[memory_id] % 10 == 0:
            memory.calculate_importance(self.access_counts[memory_id])
            self._save_to_disk(memory)
        
        return memory
    
    def search_memories(self, 
                       query: Optional[str] = None,
                       memory_type: Optional[MemoryType] = None,
                       tags: Optional[List[str]] = None,
                       min_importance: float = 0.0,
                       limit: int = 20) -> List[MemoryItem]:
        """搜索记忆项，支持多种筛选条件"""
        results = []
        
        # 筛选候选集
        candidate_ids = set(self.memory_index.keys())
        
        # 按类型筛选
        if memory_type:
            candidate_ids &= self.type_index.get(memory_type, set())
        
        # 按标签筛选
        if tags:
            tag_sets = [self.tag_index.get(tag, set()) for tag in tags]
            if tag_sets:
                candidate_ids &= set.intersection(*tag_sets) if len(tag_sets) > 1 else tag_sets[0]
        
        # 按重要性筛选
        for memory_id in candidate_ids:
            memory = self.memory_index[memory_id]
            if memory.importance_score >= min_importance:
                results.append(memory)
        
        # 按查询词筛选（简单的内容匹配）
        if query:
            query_lower = query.lower()
            filtered_results = []
            for memory in results:
                if (query_lower in memory.content.lower() or 
                    any(query_lower in tag.lower() for tag in memory.tags)):
                    filtered_results.append(memory)
            results = filtered_results
        
        # 排序：重要性 > 访问时间 > 创建时间
        results.sort(key=lambda m: (
            -m.importance_score,
            -m.accessed_at.timestamp(),
            -m.created_at.timestamp()
        ))
        
        return results[:limit]
    
    def get_related_memories(self, memory_id: str, depth: int = 1) -> List[MemoryItem]:
        """获取相关记忆，支持多层关联"""
        if memory_id not in self.memory_index:
            return []
        
        visited = set()
        related = []
        to_explore = [memory_id]
        
        for _ in range(depth):
            next_level = []
            for current_id in to_explore:
                if current_id in visited:
                    continue
                visited.add(current_id)
                
                memory = self.memory_index.get(current_id)
                if not memory:
                    continue
                
                # 添加当前记忆（除了原始记忆）
                if current_id != memory_id:
                    related.append(memory)
                
                # 探索相关记忆
                for related_id in memory.related_items:
                    if related_id not in visited and related_id in self.memory_index:
                        next_level.append(related_id)
            
            to_explore = next_level
        
        return related
    
    def create_relation(self, memory_id1: str, memory_id2: str, bidirectional: bool = True):
        """创建记忆间关联"""
        if memory_id1 in self.memory_index and memory_id2 in self.memory_index:
            memory1 = self.memory_index[memory_id1]
            memory2 = self.memory_index[memory_id2]
            
            memory1.add_relation(memory_id2)
            if bidirectional:
                memory2.add_relation(memory_id1)
            
            self._save_to_disk(memory1)
            if bidirectional:
                self._save_to_disk(memory2)
    
    def migrate_legacy_memories(self, legacy_dir: str = ".workbuddy/memory"):
        """迁移旧版记忆系统到新系统"""
        legacy_path = Path(legacy_dir)
        if not legacy_path.exists():
            return 0
        
        migrated_count = 0
        
        # 迁移 MEMORY.md
        memory_file = legacy_path / "MEMORY.md"
        if memory_file.exists():
            try:
                content = memory_file.read_text(encoding='utf-8')
                memory = MemoryItem(
                    content=content,
                    memory_type=MemoryType.PROJECT,
                    tags=["legacy_migration", "project_context"],
                    priority=MemoryPriority.HIGH,
                    source="legacy_migration"
                )
                self.save_memory(memory)
                migrated_count += 1
            except Exception as e:
                print(f"迁移 MEMORY.md 失败: {e}")
        
        # 迁移每日日志文件
        for log_file in legacy_path.glob("*.md"):
            if log_file.name == "MEMORY.md":
                continue
            
            try:
                content = log_file.read_text(encoding='utf-8')
                date_str = log_file.stem
                
                memory = MemoryItem(
                    content=content,
                    memory_type=MemoryType.CONTEXT,
                    tags=["daily_log", date_str],
                    priority=MemoryPriority.MEDIUM,
                    source="legacy_migration",
                    metadata={"file_date": date_str}
                )
                self.save_memory(memory)
                migrated_count += 1
            except Exception as e:
                print(f"迁移日志文件 {log_file.name} 失败: {e}")
        
        return migrated_count
    
    def export_to_hermes_format(self, export_dir: str) -> int:
        """导出为 Hermes 兼容格式"""
        export_path = Path(export_dir)
        export_path.mkdir(parents=True, exist_ok=True)
        
        export_count = 0
        
        for memory_id, memory in self.memory_index.items():
            # Hermes 使用 JSON 格式存储记忆
            export_file = export_path / f"{memory_id}.json"
            export_data = memory.to_dict()
            
            # 添加 Hermes 特定的元数据
            export_data["hermes_format"] = True
            export_data["export_version"] = "1.0"
            export_data["export_timestamp"] = datetime.now().isoformat()
            
            try:
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                export_count += 1
            except Exception as e:
                print(f"导出记忆 {memory_id} 失败: {e}")
        
        return export_count
    
    def cleanup_old_memories(self, days_threshold: int = 365, min_importance: float = 0.2):
        """清理旧的低重要性记忆"""
        current_time = datetime.now()
        to_remove = []
        
        for memory_id, memory in self.memory_index.items():
            days_old = (current_time - memory.created_at).days
            if days_old > days_threshold and memory.importance_score < min_importance:
                to_remove.append(memory_id)
        
        for memory_id in to_remove:
            self._delete_memory(memory_id)
        
        return len(to_remove)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取记忆系统统计信息"""
        total = len(self.memory_index)
        type_counts = {t.value: len(ids) for t, ids in self.type_index.items()}
        tag_counts = {tag: len(ids) for tag, ids in self.tag_index.items()}
        
        # 计算平均重要性
        avg_importance = sum(m.importance_score for m in self.memory_index.values()) / total if total > 0 else 0
        
        # 访问统计
        total_accesses = sum(self.access_counts.values())
        avg_accesses = total_accesses / total if total > 0 else 0
        
        return {
            "total_memories": total,
            "memory_types": type_counts,
            "tag_distribution": tag_counts,
            "average_importance": round(avg_importance, 3),
            "total_accesses": total_accesses,
            "average_accesses_per_memory": round(avg_accesses, 1),
            "storage_size_mb": self._calculate_storage_size()
        }
    
    def _save_to_disk(self, memory: MemoryItem):
        """保存记忆到磁盘"""
        memory_file = self.memory_dir / f"{memory.id}.json"
        memory_data = memory.to_dict()
        
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=2)
    
    def _load_from_disk(self, memory_file: Path) -> Optional[MemoryItem]:
        """从磁盘加载记忆"""
        try:
            with open(memory_file, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
            return MemoryItem.from_dict(memory_data)
        except Exception as e:
            print(f"加载记忆文件 {memory_file} 失败: {e}")
            return None
    
    def load_memories(self):
        """加载所有记忆"""
        self.memory_index.clear()
        self.tag_index.clear()
        self.type_index.clear()
        self.content_hash_index.clear()
        
        for memory_file in self.memory_dir.glob("*.json"):
            memory = self._load_from_disk(memory_file)
            if memory:
                memory_id = memory.id
                self.memory_index[memory_id] = memory
                
                # 更新索引
                content_hash = memory.calculate_content_hash()
                self.content_hash_index[content_hash] = memory_id
                
                for tag in memory.tags:
                    if tag not in self.tag_index:
                        self.tag_index[tag] = set()
                    self.tag_index[tag].add(memory_id)
                
                if memory.memory_type not in self.type_index:
                    self.type_index[memory.memory_type] = set()
                self.type_index[memory.memory_type].add(memory_id)
    
    def _delete_memory(self, memory_id: str):
        """删除记忆项"""
        if memory_id not in self.memory_index:
            return
        
        memory = self.memory_index[memory_id]
        
        # 从索引中移除
        content_hash = memory.calculate_content_hash()
        if content_hash in self.content_hash_index:
            del self.content_hash_index[content_hash]
        
        for tag in memory.tags:
            if tag in self.tag_index:
                self.tag_index[tag].discard(memory_id)
                if not self.tag_index[tag]:
                    del self.tag_index[tag]
        
        if memory.memory_type in self.type_index:
            self.type_index[memory.memory_type].discard(memory_id)
            if not self.type_index[memory.memory_type]:
                del self.type_index[memory.memory_type]
        
        # 从其他记忆的相关项中移除
        for other_memory in self.memory_index.values():
            if memory_id in other_memory.related_items:
                other_memory.related_items.remove(memory_id)
        
        # 删除文件
        memory_file = self.memory_dir / f"{memory_id}.json"
        if memory_file.exists():
            memory_file.unlink()
        
        # 从内存中移除
        del self.memory_index[memory_id]
        if memory_id in self.access_counts:
            del self.access_counts[memory_id]
    
    def _calculate_storage_size(self) -> float:
        """计算存储大小（MB）"""
        total_bytes = 0
        for memory_file in self.memory_dir.glob("*.json"):
            total_bytes += memory_file.stat().st_size
        
        return round(total_bytes / (1024 * 1024), 2)

# 记忆系统工具函数
class MemoryUtils:
    """记忆工具类，提供高级功能"""
    
    @staticmethod
    def extract_memory_from_text(text: str, 
                                memory_type: MemoryType = MemoryType.FACT,
                                auto_tags: bool = True) -> MemoryItem:
        """从文本中提取记忆"""
        # 自动生成标签（简单实现）
        tags = []
        if auto_tags:
            # 提取关键词（简单实现）
            words = text.split()
            for word in words:
                if len(word) > 4 and word.isalpha():
                    tags.append(word.lower())
            tags = list(set(tags))[:5]  # 去重并限制数量
        
        memory = MemoryItem(
            content=text[:1000],  # 限制长度
            memory_type=memory_type,
            tags=tags,
            source="text_extraction"
        )
        
        return memory
    
    @staticmethod
    def create_solution_memory(solution_content: str, 
                              solution_type: str,
                              tags: List[str]) -> MemoryItem:
        """创建解决方案记忆"""
        memory = MemoryItem(
            content=solution_content,
            memory_type=MemoryType.SOLUTION,
            tags=["solution", solution_type] + tags,
            priority=MemoryPriority.HIGH,
            source="solution_generator",
            metadata={
                "solution_type": solution_type,
                "created_by": "multi_solution_generator"
            }
        )
        return memory
    
    @staticmethod
    def create_skill_memory(skill_name: str, 
                           skill_description: str,
                           triggers: List[str],
                           implementation: str) -> MemoryItem:
        """创建技能记忆"""
        memory = MemoryItem(
            content=f"技能: {skill_name}\n\n描述: {skill_description}\n\n实现:\n{implementation}",
            memory_type=MemoryType.SKILL,
            tags=["skill", skill_name] + triggers,
            priority=MemoryPriority.HIGH,
            source="skill_creator",
            metadata={
                "skill_name": skill_name,
                "triggers": triggers,
                "implementation_length": len(implementation)
            }
        )
        return memory

# 全局记忆管理器实例
_memory_manager_instance: Optional[MemoryManager] = None

def get_memory_manager() -> MemoryManager:
    """获取全局记忆管理器实例（单例模式）"""
    global _memory_manager_instance
    if _memory_manager_instance is None:
        _memory_manager_instance = MemoryManager()
    return _memory_manager_instance

def init_memory_system(migrate_legacy: bool = True):
    """初始化记忆系统"""
    manager = get_memory_manager()
    if migrate_legacy:
        migrated = manager.migrate_legacy_memories()
        print(f"迁移了 {migrated} 个旧版记忆项")
    
    stats = manager.get_statistics()
    print(f"记忆系统初始化完成，共 {stats['total_memories']} 个记忆项")
    
    return manager

if __name__ == "__main__":
    # 测试代码
    manager = init_memory_system()
    
    # 创建测试记忆
    test_memory = MemoryItem(
        content="用户偏好使用中文回复，喜欢表格形式展示分析结果",
        memory_type=MemoryType.PREFERENCE,
        tags=["user_preference", "language", "format"],
        priority=MemoryPriority.HIGH,
        source="observation"
    )
    
    memory_id = manager.save_memory(test_memory)
    print(f"创建记忆 ID: {memory_id}")
    
    # 搜索测试
    results = manager.search_memories(tags=["user_preference"])
    print(f"找到 {len(results)} 个相关记忆")
    
    # 显示统计信息
    stats = manager.get_statistics()
    print("记忆系统统计:", json.dumps(stats, ensure_ascii=False, indent=2))