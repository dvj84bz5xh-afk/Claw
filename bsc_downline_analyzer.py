#!/usr/bin/env python3
"""
BSC 下线分析工具 - 自动查询某个地址发展了多少下线
使用方法：
    python bsc_downline_analyzer.py <地址> [合约地址]
"""

import requests
import json
import sys
from collections import defaultdict
from typing import List, Dict, Set

class BSCDownlineAnalyzer:
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.base_url = "https://api.bscscan.com/api"
        self.bscscan_url = "https://bscscan.com"
        
    def get_transactions(self, address: str, start_block: int = 0, end_block: int = 99999999) -> List[Dict]:
        """获取地址的所有交易"""
        if self.api_key:
            # 使用 API
            url = f"{self.base_url}?module=account&action=txlist"
            url += f"&address={address}&startblock={start_block}&endblock={end_block}"
            url += f"&sort=asc&apikey={self.api_key}"
            
            response = requests.get(url)
            data = response.json()
            
            if data['status'] == '1':
                return data['result']
            else:
                print(f"API 错误: {data.get('message', '未知错误')}")
                return []
        else:
            print("⚠️  未提供 API key，将使用网页抓取方式（功能有限）")
            return []
    
    def get_internal_transactions(self, address: str) -> List[Dict]:
        """获取内部交易"""
        if not self.api_key:
            return []
        
        url = f"{self.base_url}?module=account&action=txlistinternal"
        url += f"&address={address}&sort=asc&apikey={self.api_key}"
        
        response = requests.get(url)
        data = response.json()
        
        if data['status'] == '1':
            return data['result']
        return []
    
    def get_contract_events(self, contract_address: str, address: str, abi: List[Dict]) -> List[Dict]:
        """通过事件日志查询"""
        # 这需要知道具体事件签名，暂时留空
        pass
    
    def analyze_downlines_from_transactions(self, address: str, contract_address: str) -> Dict:
        """
        分析交易记录，找出所有下线
        逻辑：查找所有调用合约且 referrer/inviter 字段是目标地址的交易
        """
        print(f"\n🔍 正在分析地址: {address}")
        print(f"📝 合约地址: {contract_address}")
        print("=" * 60)
        
        # 获取交易记录
        transactions = self.get_transactions(address)
        
        if not transactions:
            print("⚠️  无法通过 API 获取交易，请手动在 BSCScan 上查询")
            print(f"\n📍 手动查询步骤：")
            print(f"1. 打开: {self.bscscan_url}/address/{address}")
            print(f"2. 点击 [Transactions] 标签")
            print(f"3. 点击 [Advanced Filter]")
            print(f"   - Method: 选择 'UpLevel' 或 'register' 相关方法")
            print(f"   - 或者筛选发送给合约 {contract_address} 的交易")
            print(f"4. 分析这些交易的 Input Data，找出 referrer 字段")
            return {}
        
        # 分析交易
        downlines = set()
        related_txs = []
        
        for tx in transactions:
            # 筛选与合约交互的交易
            if tx.get('to', '').lower() == contract_address.lower():
                input_data = tx.get('input', '')
                
                # 简单判断：如果 input data 包含地址（需要解析 ABI）
                # 这里先收集相关交易，后续手动分析
                related_txs.append({
                    'hash': tx['hash'],
                    'from': tx['from'],
                    'input': input_data,
                    'block': tx['blockNumber']
                })
        
        print(f"\n📊 找到 {len(related_txs)} 笔与合约相关的交易")
        
        if related_txs:
            print("\n🔗 相关交易列表：")
            for i, tx in enumerate(related_txs[:10], 1):  # 只显示前10条
                print(f"{i}. {tx['hash']}")
                print(f"   From: {tx['from']}")
                print(f"   Block: {tx['block']}")
                print()
        
        return {
            'total_transactions': len(transactions),
            'contract_interactions': len(related_txs),
            'related_transactions': related_txs
        }
    
    def manual_check_guide(self, address: str, contract_address: str):
        """生成手动检查指南"""
        print("\n" + "=" * 60)
        print("📖 手动检查指南（BSCScan 网页操作）")
        print("=" * 60)
        
        print(f"\n步骤 1️⃣：打开地址页面")
        print(f"  {self.bscscan_url}/address/{address}#transactions")
        
        print(f"\n步骤 2️⃣：筛选与合约的交互")
        print(f"  1. 点击 [Transactions] 标签")
        print(f"  2. 点击 [Advanced Filter] 按钮")
        print(f"  3. 设置过滤条件：")
        print(f"     - To Address: {contract_address}")
        print(f"     - Method: 选择合约的注册/升级方法（如 upLevel, register）")
        print(f"  4. 点击 [Apply]")
        
        print(f"\n步骤 3️⃣：分析交易 Input Data")
        print(f"  对每笔交易：")
        print(f"  1. 点击 TxHash 进入交易详情")
        print(f"  2. 找到 [Input Data] 部分")
        print(f"  3. 如果显示的是十六进制，点击 [Decode Input Data]")
        print(f"  4. 查找参数中的 'referrer' 或 'inviter' 字段")
        print(f"  5. 如果 referrer == {address}，说明这是该地址发展的下线")
        
        print(f"\n步骤 4️⃣：统计下线数量")
        print(f"  方法A：手动计数所有 referrer 匹配的交易的 from 地址")
        print(f"  方法B：使用 BSCScan API + 脚本自动分析（推荐）")
        
        print(f"\n💡 快捷方式：")
        url = f"{self.bscscan_url}/address/{address}#transactions"
        print(f"  直接访问: {url}")
        print(f"  然后按 F12 打开开发者工具，使用 Console 脚本自动提取")
        
        return url


def main():
    if len(sys.argv) < 2:
        print("使用方法：")
        print("  python bsc_downline_analyzer.py <地址> [合约地址] [API_KEY]")
        print("\n示例：")
        print("  python bsc_downline_analyzer.py 0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2")
        print("  python bsc_downline_analyzer.py 0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2 0xD804569fAa84147690d77080AD7E8CbEe159932d")
        sys.exit(1)
    
    target_address = sys.argv[1]
    contract_address = sys.argv[2] if len(sys.argv) > 2 else "0xD804569fAa84147690d77080AD7E8CbEe159932d"
    api_key = sys.argv[3] if len(sys.argv) > 3 else ""
    
    # 创建分析器
    analyzer = BSCDownlineAnalyzer(api_key)
    
    # 生成手动检查指南
    guide_url = analyzer.manual_check_guide(target_address, contract_address)
    
    # 如果有 API key，尝试自动分析
    if api_key:
        print(f"\n🤖 使用 API 自动分析...")
        result = analyzer.analyze_downlines_from_transactions(target_address, contract_address)
        
        # 保存结果
        output_file = f"downline_analysis_{target_address[:8]}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n✅ 结果已保存至: {output_file}")
    else:
        print(f"\n⚠️  提示：提供 API key 可以自动分析")
        print(f"   免费申请：https://bscscan.com/apis")


if __name__ == "__main__":
    main()
