#!/usr/bin/env python3
"""
BSC 链上数据查询工具 - 本地运行版
功能：查询合约下线数量、推荐关系、交易记录
⚠️ 重要：请在本地运行，不要公开 API Key
"""

import requests
import json
import sys
from typing import Dict, List, Optional

class BSCQueryTool:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.bscscan.com/api"
    
    def get_abi(self, contract_address: str) -> Optional[Dict]:
        """获取合约 ABI"""
        url = f"{self.base_url}?module=contract&action=getabi&address={contract_address}&apikey={self.api_key}"
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            if data["status"] == "1":
                return json.loads(data["result"])
            else:
                print(f"❌ 获取 ABI 失败: {data['result']}")
                return None
        except Exception as e:
            print(f"❌ 网络错误: {e}")
            return None
    
    def get_transactions(self, address: str, start_block: int = 0, end_block: str = "latest") -> List[Dict]:
        """获取地址的所有交易记录"""
        url = f"{self.base_url}?module=account&action=txlist&address={address}&startblock={start_block}&endblock={end_block}&sort=asc&apikey={self.api_key}"
        try:
            response = requests.get(url, timeout=15)
            data = response.json()
            if data["status"] == "1":
                return data["result"]
            else:
                if "No transactions found" in data["result"]:
                    return []
                print(f"⚠️ 获取交易记录失败: {data['result']}")
                return []
        except Exception as e:
            print(f"❌ 网络错误: {e}")
            return []
    
    def get_internal_transactions(self, address: str) -> List[Dict]:
        """获取内部交易记录（合约调用）"""
        url = f"{self.base_url}?module=account&action=txlistinternal&address={address}&apikey={self.api_key}"
        try:
            response = requests.get(url, timeout=15)
            data = response.json()
            if data["status"] == "1":
                return data["result"]
            else:
                if "No transactions found" in data["result"]:
                    return []
                print(f"⚠️ 获取内部交易失败: {data['result']}")
                return []
        except Exception as e:
            print(f"❌ 网络错误: {e}")
            return []
    
    def find_function_selector(self, abi: Dict, function_name: str) -> Optional[str]:
        """根据函数名查找选择器"""
        if not abi:
            return None
        
        for item in abi:
            if item.get("type") == "function" and item.get("name") == function_name:
                # 构建函数签名
                inputs = ",".join([inp["type"] for inp in item.get("inputs", [])])
                signature = f"{function_name}({inputs})"
                # 计算选择器（Keccak-256 前4字节）
                import hashlib
                selector = "0x" + hashlib.sha3_256(signature.encode()).hexdigest()[:8]
                return selector
        return None
    
    def decode_input_data(self, input_data: str, abi: Dict) -> Optional[Dict]:
        """尝试解码交易输入数据"""
        if not input_data or len(input_data) < 10:
            return None
        
        selector = input_data[:10]  # 0x + 8位
        
        # 在 ABI 中查找匹配的函数
        for item in abi:
            if item.get("type") == "function":
                inputs = ",".join([inp["type"] for inp in item.get("inputs", [])])
                signature = f"{item['name']}({inputs})"
                import hashlib
                calc_selector = "0x" + hashlib.sha3_256(signature.encode()).hexdigest()[:8]
                
                if calc_selector == selector:
                    return {
                        "function": item["name"],
                        "selector": selector,
                        "inputs": item.get("inputs", [])
                    }
        return None
    
    def count_downlines_by_transactions(self, address: str, contract_address: str, abi: Dict) -> Dict:
        """通过交易记录统计下线数量"""
        print(f"\n🔍 正在查询地址 {address} 的交易记录...")
        
        # 获取所有交易
        transactions = self.get_transactions(address)
        internal_txs = self.get_internal_transactions(address)
        
        result = {
            "upLevel_count": 0,
            "direct_downlines": [],
            "contract_interactions": 0
        }
        
        # 统计 upLevel 调用
        for tx in transactions + internal_txs:
            if tx.get("to", "").lower() == contract_address.lower():
                input_data = tx.get("input", "")
                decoded = self.decode_input_data(input_data, abi)
                
                if decoded and "upLevel" in decoded["function"]:
                    result["upLevel_count"] += 1
                    # 尝试提取参数（简化处理）
                    if len(input_data) > 10:
                        # 第一个参数通常是 address 类型（64字符 = 32字节）
                        try:
                            param = "0x" + input_data[10:74]
                            result["direct_downlines"].append(param)
                        except:
                            pass
                
                result["contract_interactions"] += 1
        
        return result
    
    def query_contract_function(self, contract_address: str, function_name: str, param_types: List[str], param_values: List[str]) -> Optional[str]:
        """调用合约的读取函数"""
        # 构建调用数据
        # 这里简化处理，实际需要按照 ABI 编码
        print(f"⚠️ 合约函数调用需要额外的库（如 web3.py）")
        print(f"   建议：直接在 BSCScan 网页上手动调用 {function_name} 函数")
        return None

def main():
    print("=" * 60)
    print("BSC 链上数据查询工具")
    print("=" * 60)
    
    # 提示用户输入 API Key
    print("\n📝 使用前准备：")
    print("1. 访问 https://bscscan.com/apis 注册并获取 API Key")
    print("2. 在下方输入您的 API Key（不会保存，仅本次使用）\n")
    
    api_key = input("请输入 BSCScan API Key: ").strip()
    
    if not api_key:
        print("❌ API Key 不能为空")
        return
    
    tool = BSCQueryTool(api_key)
    
    print("\n" + "=" * 60)
    print("请输入查询参数：")
    
    contract_address = input("合约地址 (例如 0xD804569fAa84147690d77080AD7E8CbEe159932d): ").strip()
    target_address = input("要查询的地址 (例如 0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2): ").strip()
    
    if not contract_address or not target_address:
        print("❌ 地址不能为空")
        return
    
    print("\n" + "=" * 60)
    print("开始查询...")
    
    # 1. 获取合约 ABI
    print("\n[1/3] 获取合约 ABI...")
    abi = tool.get_abi(contract_address)
    
    if abi:
        print("✅ ABI 获取成功")
        # 列出所有可读函数
        print("\n📋 合约中的读取函数：")
        for item in abi:
            if item.get("type") == "function":
                if "view" in item.get("stateMutability", "") or "pure" in item.get("stateMutability", ""):
                    inputs = ",".join([f"{inp['type']} {inp['name']}" for inp in item.get("inputs", [])])
                    print(f"  - {item['name']}({inputs})")
    else:
        print("⚠️ 无法获取 ABI，将使用交易记录分析")
    
    # 2. 统计下线数量
    print("\n[2/3] 分析交易记录...")
    result = tool.count_downlines_by_transactions(target_address, contract_address, abi)
    
    print(f"\n📊 查询结果：")
    print(f"  - upLevel 调用次数（发展下线数）: {result['upLevel_count']}")
    print(f"  - 合约交互次数: {result['contract_interactions']}")
    
    if result["direct_downlines"]:
        print(f"  - 疑似下线地址：")
        for addr in set(result["direct_downlines"]):  # 去重
            print(f"    {addr}")
    
    # 3. 提示手动操作
    print("\n[3/3] 获取详细信息...")
    print("\n💡 如需获取更详细的信息（如下线具体数量、等级等），请：")
    print(f"1. 访问: https://bscscan.com/address/{contract_address}#readContract")
    print(f"2. 找到类似以下名称的函数（不同合约命名可能不同）：")
    print(f"   - userInfo")
    print(f"   - getUserInfo")
    print(f"   - getInvite")
    print(f"   - getReferral")
    print(f"3. 输入地址: {target_address}")
    print(f"4. 点击 Query 查看结果")
    
    print("\n" + "=" * 60)
    print("查询完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
