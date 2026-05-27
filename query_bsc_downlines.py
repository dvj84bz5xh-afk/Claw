#!/usr/bin/env python3
"""
BSC 下线查询工具 - 本地运行版本
使用方法：
    1. 修改下面的 API_KEY 变量
    2. 运行：python query_bsc_downlines.py
"""

import requests
import json
import time
from typing import List, Dict, Set

# ============ 配置区域 ============
API_KEY = "HJE64MA9XFHXENI7RVN6C5IMX9RDHEA4M2"  # ← 替换成你的 BSCScan API key
TARGET_ADDRESS = "0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2"  # 要查询的地址
CONTRACT_ADDRESS = "0xD804569fAa84147690d77080AD7E8CbEe159932d"  # 合约地址
# ==================================


class BSCAPIClient:
    """BSCScan API V2 客户端"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.bscscan.com/api"
        
    def _call_api(self, params: Dict) -> Dict:
        """调用 BSCScan API"""
        params['apikey'] = self.api_key
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            data = response.json()
            
            if data.get('status') == '1':
                return {'success': True, 'data': data['result']}
            else:
                return {'success': False, 'error': data.get('message', '未知错误')}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_abi(self, contract_address: str) -> Dict:
        """获取合约 ABI"""
        params = {
            'module': 'contract',
            'action': 'getabi',
            'address': contract_address
        }
        return self._call_api(params)
    
    def get_transactions(self, address: str, start_block: int = 0, 
                        end_block: int = 99999999, page: int = 1, 
                        offset: int = 10000, sort: str = 'asc') -> Dict:
        """获取普通交易列表"""
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'startblock': start_block,
            'endblock': end_block,
            'page': page,
            'offset': offset,
            'sort': sort
        }
        return self._call_api(params)
    
    def get_internal_transactions(self, address: str, page: int = 1, 
                                  offset: int = 10000) -> Dict:
        """获取内部交易"""
        params = {
            'module': 'account',
            'action': 'txlistinternal',
            'address': address,
            'page': page,
            'offset': offset,
            'sort': 'asc'
        }
        return self._call_api(params)
    
    def get_token_transfers(self, address: str, page: int = 1,
                           offset: int = 10000) -> Dict:
        """获取 Token 转账记录"""
        params = {
            'module': 'account',
            'action': 'tokentx',
            'address': address,
            'page': page,
            'offset': offset,
            'sort': 'asc'
        }
        return self._call_api(params)


def analyze_downlines(api_client: BSCAPIClient, target_address: str, 
                       contract_address: str) -> Dict:
    """
    分析目标地址发展的下线数量
    
    逻辑：
    1. 获取目标地址的所有交易
    2. 筛选出与合约交互的交易（to = contract_address）
    3. 解析这些交易的 input data，找出 referrer 字段
    4. 如果 referrer == target_address，说明这是 target 发展的下线
    """
    
    print(f"\n{'='*60}")
    print(f"🔍 开始分析地址: {target_address}")
    print(f"📝 合约地址: {contract_address}")
    print(f"{'='*60}\n")
    
    # 步骤1：获取交易记录
    print("步骤 1/4: 获取交易记录...")
    result = api_client.get_transactions(target_address, offset=10000)
    
    if not result['success']:
        print(f"❌ 获取交易失败: {result['error']}")
        return {}
    
    transactions = result['data']
    print(f"✅ 找到 {len(transactions)} 笔交易\n")
    
    # 步骤2：筛选与合约相关的交易
    print("步骤 2/4: 筛选与合约相关的交易...")
    contract_txs = []
    
    for tx in transactions:
        to_address = tx.get('to', '').lower()
        if to_address == contract_address.lower():
            contract_txs.append(tx)
    
    print(f"✅ 找到 {len(contract_txs)} 笔与合约的交互\n")
    
    if not contract_txs:
        print("⚠️  未发现与合约的交互记录")
        print("可能原因：")
        print("  1. 该地址尚未与合约交互")
        print("  2. 交互是通过内部交易或代理合约进行的")
        print("  3. 需要查询更多历史区块\n")
        return {'total_transactions': len(transactions), 'contract_interactions': 0}
    
    # 步骤3：分析交易（需要解析 input data）
    print("步骤 3/4: 分析交易 Input Data...")
    print("=" * 60)
    
    downlines = set()
    analysis_results = []
    
    for i, tx in enumerate(contract_txs, 1):
        tx_hash = tx['hash']
        input_data = tx.get('input', '')
        from_addr = tx.get('from', '')
        block = tx.get('blockNumber', '')
        
        print(f"\n[{i}/{len(contract_txs)}] 交易: {tx_hash[:20]}...")
        print(f"  From: {from_addr}")
        print(f"  Block: {block}")
        print(f"  Input: {input_data[:66]}..." if len(input_data) > 66 else f"  Input: {input_data}")
        
        # 保存分析结果
        analysis_results.append({
            'tx_hash': tx_hash,
            'from': from_addr,
            'block': block,
            'input': input_data
        })
        
        # TODO: 解析 input data 找出 referrer
        # 这需要知道合约的 ABI 和函数签名
        # 暂时先记录交易
        
        # 简单的启发式判断：
        # 如果交易的 from 不是 target_address，可能是下线
        if from_addr.lower() != target_address.lower():
            downlines.add(from_addr)
    
    print(f"\n✅ 分析完成\n")
    
    # 步骤4：统计结果
    print("步骤 4/4: 生成统计报告...")
    print("=" * 60)
    
    report = {
        'target_address': target_address,
        'contract_address': contract_address,
        'total_transactions': len(transactions),
        'contract_interactions': len(contract_txs),
        'potential_downlines': len(downlines),
        'downline_addresses': list(downlines),
        'transactions': analysis_results
    }
    
    return report


def print_report(report: Dict):
    """打印分析报告"""
    print("\n" + "=" * 60)
    print("📊 下线分析报告")
    print("=" * 60)
    
    print(f"\n🎯 目标地址: {report['target_address']}")
    print(f"📝 合约地址: {report['contract_address']}")
    
    print(f"\n📈 统计数据:")
    print(f"  - 总交易数: {report['total_transactions']}")
    print(f"  - 合约交互数: {report['contract_interactions']}")
    print(f"  - 潜在下线条数: {report['potential_downlines']}")
    
    if report['downline_addresses']:
        print(f"\n🔗 潜在下线地址列表 (前10个):")
        for i, addr in enumerate(report['downline_addresses'][:10], 1):
            print(f"  {i}. {addr}")
        
        if len(report['downline_addresses']) > 10:
            print(f"  ... 还有 {len(report['downline_addresses']) - 10} 个")
    
    print("\n" + "=" * 60)
    print("⚠️  注意：这需要进一步解析 Input Data 才能准确判断")
    print("    建议使用 BSCScan 网页版手动验证")
    print("=" * 60)


def save_report(report: Dict, filename: str = "downline_analysis.json"):
    """保存报告到文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n✅ 报告已保存至: {filename}")


def main():
    print("=" * 60)
    print("BSC 下线查询工具")
    print("=" * 60)
    
    # 检查配置
    if API_KEY == "YOUR_API_KEY_HERE":
        print("\n❌ 错误：请先配置 API_KEY")
        print("   1. 打开本脚本")
        print("   2. 修改第 10 行的 API_KEY 变量")
        print("   3. 保存后重新运行")
        print("\n💡 免费申请 API key: https://bscscan.com/apis")
        return
    
    # 创建 API 客户端
    api_client = BSCAPIClient(API_KEY)
    
    # 分析下线
    report = analyze_downlines(api_client, TARGET_ADDRESS, CONTRACT_ADDRESS)
    
    if report:
        # 打印报告
        print_report(report)
        
        # 保存报告
        output_file = f"downline_analysis_{TARGET_ADDRESS[:8]}.json"
        save_report(report, output_file)
        
        # 生成手动验证指南
        print(f"\n📖 手动验证指南:")
        print(f"  1. 访问: https://bscscan.com/address/{TARGET_ADDRESS}#transactions")
        print(f"  2. 点击 [Advanced Filter]")
        print(f"  3. To Address 填入: {CONTRACT_ADDRESS}")
        print(f"  4. 点击 [Apply]")
        print(f"  5. 逐笔点击交易哈希，查看 Input Data")
        print(f"  6. 解码后查看 referrer 字段是否为 {TARGET_ADDRESS}")


if __name__ == "__main__":
    main()
