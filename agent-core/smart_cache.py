#!/usr/bin/env python3
"""
Smart Cache - 智能缓存系统
自动缓存频繁访问的数据，提升响应速度
"""

import json
import hashlib
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from functools import wraps
import threading


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int
    last_accessed: datetime
    size_bytes: int


class SmartCache:
    """智能缓存管理器"""
    
    def __init__(self, cache_dir: Path = None, max_size_mb: int = 100, default_ttl_seconds: int = 3600):
        self.cache_dir = cache_dir or (Path.home() / ".claw" / "cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_size_mb = max_size_mb
        self.default_ttl_seconds = default_ttl_seconds
        
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.cache_index_file = self.cache_dir / "cache_index.json"
        
        self._lock = threading.RLock()
        self._load_index()
        
        # 统计
        self.hits = 0
        self.misses = 0
    
    def _load_index(self):
        """加载缓存索引"""
        if self.cache_index_file.exists():
            with open(self.cache_index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 只加载未过期的条目
                for key, entry_data in data.items():
                    expires = datetime.fromisoformat(entry_data['expires_at']) if entry_data['expires_at'] else None
                    if expires is None or expires > datetime.now():
                        self.memory_cache[key] = CacheEntry(
                            key=key,
                            value=None,  # 磁盘缓存，使用时加载
                            created_at=datetime.fromisoformat(entry_data['created_at']),
                            expires_at=expires,
                            access_count=entry_data['access_count'],
                            last_accessed=datetime.fromisoformat(entry_data['last_accessed']),
                            size_bytes=entry_data['size_bytes']
                        )
    
    def _save_index(self):
        """保存缓存索引"""
        with self._lock:
            index = {}
            for key, entry in self.memory_cache.items():
                index[key] = {
                    'created_at': entry.created_at.isoformat(),
                    'expires_at': entry.expires_at.isoformat() if entry.expires_at else None,
                    'access_count': entry.access_count,
                    'last_accessed': entry.last_accessed.isoformat(),
                    'size_bytes': entry.size_bytes
                }
            with open(self.cache_index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
    
    def _get_cache_file(self, key: str) -> Path:
        """获取缓存文件路径"""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self._lock:
            entry = self.memory_cache.get(key)
            
            if entry is None:
                self.misses += 1
                return None
            
            # 检查是否过期
            if entry.expires_at and entry.expires_at < datetime.now():
                self._evict(key)
                self.misses += 1
                return None
            
            # 从磁盘加载值
            cache_file = self._get_cache_file(key)
            if not cache_file.exists():
                self._evict(key)
                self.misses += 1
                return None
            
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    value = json.load(f)
            except Exception:
                self._evict(key)
                self.misses += 1
                return None
            
            # 更新访问统计
            entry.access_count += 1
            entry.last_accessed = datetime.now()
            
            self.hits += 1
            return value
    
    def set(self, key: str, value: Any, ttl_seconds: int = None) -> bool:
        """设置缓存值"""
        ttl = ttl_seconds or self.default_ttl_seconds
        
        with self._lock:
            # 序列化值
            try:
                value_json = json.dumps(value, ensure_ascii=False)
                size_bytes = len(value_json.encode('utf-8'))
            except Exception:
                return False
            
            # 检查是否需要清理空间
            self._ensure_space(size_bytes)
            
            # 保存到磁盘
            cache_file = self._get_cache_file(key)
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    f.write(value_json)
            except Exception:
                return False
            
            # 更新内存索引
            now = datetime.now()
            self.memory_cache[key] = CacheEntry(
                key=key,
                value=None,  # 值存储在磁盘
                created_at=now,
                expires_at=now + timedelta(seconds=ttl) if ttl > 0 else None,
                access_count=0,
                last_accessed=now,
                size_bytes=size_bytes
            )
            
            self._save_index()
            return True
    
    def _evict(self, key: str):
        """驱逐缓存条目"""
        with self._lock:
            if key in self.memory_cache:
                del self.memory_cache[key]
            cache_file = self._get_cache_file(key)
            if cache_file.exists():
                cache_file.unlink()
    
    def _ensure_space(self, required_bytes: int):
        """确保有足够空间"""
        with self._lock:
            total_size = sum(e.size_bytes for e in self.memory_cache.values())
            max_bytes = self.max_size_mb * 1024 * 1024
            
            while total_size + required_bytes > max_bytes and self.memory_cache:
                # LRU淘汰策略
                lru_key = min(self.memory_cache.keys(), 
                             key=lambda k: self.memory_cache[k].last_accessed)
                total_size -= self.memory_cache[lru_key].size_bytes
                self._evict(lru_key)
    
    def clear(self):
        """清空所有缓存"""
        with self._lock:
            for key in list(self.memory_cache.keys()):
                self._evict(key)
            self.hits = 0
            self.misses = 0
    
    def get_stats(self) -> Dict:
        """获取缓存统计"""
        with self._lock:
            total_size = sum(e.size_bytes for e in self.memory_cache.values())
            total_requests = self.hits + self.misses
            hit_rate = self.hits / total_requests if total_requests > 0 else 0
            
            return {
                "entries": len(self.memory_cache),
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "max_size_mb": self.max_size_mb,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": round(hit_rate * 100, 2),
                "utilization": round((total_size / (self.max_size_mb * 1024 * 1024)) * 100, 2)
            }
    
    def cached(self, ttl_seconds: int = None):
        """装饰器：缓存函数结果"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 生成缓存key
                cache_key = f"{func.__module__}.{func.__name__}:{str(args)}:{str(kwargs)}"
                
                # 尝试从缓存获取
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # 执行函数
                result = func(*args, **kwargs)
                
                # 缓存结果
                self.set(cache_key, result, ttl_seconds)
                
                return result
            
            return wrapper
        return decorator


# 全局缓存实例
global_cache = SmartCache()


def main():
    """测试智能缓存"""
    cache = SmartCache()
    
    # 测试基本操作
    cache.set("test_key", {"data": "test_value"}, ttl_seconds=300)
    value = cache.get("test_key")
    
    print("=" * 60)
    print("Smart Cache 测试报告")
    print("=" * 60)
    print(f"设置值: {value}")
    print(f"缓存统计: {json.dumps(cache.get_stats(), indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
