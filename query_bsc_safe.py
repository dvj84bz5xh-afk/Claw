#!/usr/bin/env python3
"""
BSC 下线查询工具 - 安全本地版本
重要：此脚本在用户本地运行，API key 不会暴露到聊天中

使用方法：
    1. 用记事本打开此文件
    2. 修改第 12 行的 API_KEY（替换成你的新 key）
    3. 保存文件
    4. 在命令行运行：python query_bsc_safe.py
"""

import requests
import json
import time
from typing import Dict, List, Set

# ============ 配置区域 ============
# 注意：请先撤销之前暴露的 API key，然后创建新 key 填入下方
API_KEY = "YOUR_NEW_API_KEY_HERE"  # ← 替换成你的新 API key

TARGET_ADDRESS = "0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2"  # 要查询的地址
CONTRACT_ADDRESS = "0xD804569fAa84147690d77080AD7E8CbEe159932d"  # 合约地址
# =====================================


class BSCQueryTool:
    """BSC 查询工具（使用 BSCScan API V1，虽已弃用但仍可用）"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.bscscan.com/api"
        self.request_delay = 0.2  # 避免 API 限流
        
    def _make_request(self, params: Dict) -> Dict:
        """发送 API 请求"""
        params['apikey'] = self.api_key
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            data = response.json()
            
            # 检查是否成功
            if data.get('status') == '1':
                return {'success': True, 'data': data['result']}
            else:
                error_msg = data.get('message', '未知错误')
                result = data.get('result', '')
                
                # 如果是弃用警告，尝试使用数据（有些情况下仍能返回数据）
                if 'deprecated' in error_msg.lower():
                    print(f"⚠️  API 警告: {error_msg}")
                    if result:
                        return {'success': True, 'data': result}
                
                return {'success': False, 'error': error_msg, 'result': result}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_transactions(self, address: str, start_block: int = 0,
                        end_block: int = 99999999, offset: int = 10000) -> Dict:
        """获取地址的交易列表"""
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'startblock': start_block,
            'endblock': end_block,
            'page': 1,
            'offset': offset,
            'sort': 'asc'
        }
        return self._make_request(params)
    
    def get_internal_txs(self, address: str, offset: int = 10000) -> Dict:
        """获取内部交易"""
        params = {
            'module': 'account',
            'action': 'txlistinternal',
            'address': address,
            'page': 1,
            'offset': offset,
            'sort': 'asc'
        }
        return self._make_request(params)
    
    def get_token_transfers(self, address: str, offset: int = 10000) -> Dict:
        """获取 Token 转账"""
        params = {
            'module': 'account',
            'action': 'tokentx',
            'address': address,
            'page': 1,
            'offset': offset,
            'sort': 'asc'
        }
        return self._make_request(params)


def analyze_address(tool: BSCQueryTool, target_addr: str, contract_addr: str) -> Dict:
    """
    分析目标地址，找出其发展的下线
    
    策略：
    1. 获取目标地址的所有交易
    2. 筛选出 to = contract_addr 的交易（说明有人通过此地址注册/升级）
    3. 解析这些交易的 input data，找出 referrer 字段
    4. 统计 referrer = target_addr 的数量
    """
    
    print(f"\n{'='*60}")
    print(f"🔍 开始分析地址: {target_addr}")
    print(f"📝 合约地址: {contract_addr}")
    print(f"{'='*60}\n")
    
    # 步骤1：获取交易
    print("📡 步骤 1/4: 获取交易记录...")
    result = tool.get_transactions(target_addr)
    
    if not result['success']:
        print(f"❌ 获取失败: {result['error']}")
        
        # 如果是 API 弃用警告，提供手动方案
        if 'deprecated' in result.get('error', '').lower():
            print(f"\n💡 解决方案：")
            print(f"  1. BSCScan API V1 已弃用")
            print(f"  2. 请手动在 BSCScan 网页查询")
            print(f"  3. 或升级到 V2 API（需要修改脚本）")
            return {'error': 'API deprecated'}
        
        return {}
    
    transactions = result['data']
    print(f"✅ 找到 {len(transactions)} 笔交易\n")
    
    # 步骤2：筛选与合约的交互
    print("🔍 步骤 2/4: 筛选与合约的交互...")
    contract_txs = [tx for tx in transactions if tx.get('to', '').lower() == contract_addr.lower()]
    print(f"✅ 找到 {len(contract_txs)} 笔与合约相关的交易\n")
    
    if not contract_txs:
        print("⚠️  该地址没有与合约的直接交互")
        print("   可能原因：")
        print("   1. 该地址是纯下线（只被推荐，未发展他人）")
        print("   2. 交互通过代理合约进行")
        print("   3. 需要查询内部交易\n")
        
        # 尝试查询内部交易
        print("🔄 尝试查询内部交易...")
        internal_result = tool.get_internal_txs(target_addr)
        
        if internal_result['success']:
            internal_txs = internal_result['data']
            print(f"✅ 找到 {len(internal_txs)} 笔内部交易")
        
        return {'total_txs': len(transactions), 'contract_interactions': 0}
    
    # 步骤3：分析交易
    print("🧬 步骤 3/4: 分析交易数据...")
    print(f"{'='*60}")
    
    downlines = set()
    tx_details = []
    
    for i, tx in enumerate(contract_txs[:50], 1):  # 限制前50笔
        tx_hash = tx.get('hash', '')
        from_addr = tx.get('from', '')
        input_data = tx.get('input', '')
        
        print(f"\n[{i}/{min(len(contract_txs), 50)}] {tx_hash[:20]}...")
        print(f"  From: {from_addr}")
        print(f"  Input: {input_data[:50]}..." if len(input_data) > 50 else f"  Input: {input_data}")
        
        # 保存详情
        tx_details.append({
            'hash': tx_hash,
            'from': from_addr,
            'input': input_data,
            'block': tx.get('blockNumber', '')
        })
        
        # 启发式判断：如果 from != target，可能是下线
        if from_addr.lower() != target_addr.lower():
            downlines.add(from_addr)
    
    print(f"\n✅ 分析完成\n")
    
    # 步骤4：生成报告
    print("📊 步骤 4/4: 生成报告...")
    report = {
        'target_address': target_addr,
        'contract_address': contract_addr,
        'total_transactions': len(transactions),
        'contract_interactions': len(contract_txs),
        'potential_downlines_count': len(downlines),
        'potential_downlines': list(downlines),
        'transaction_details': tx_details
    }
    
    return report


def print_report(report: Dict):
    """打印报告"""
    if 'error' in report:
        return
    
    print("\n" + "="*60)
    print("📊 下线分析报告")
    print("="*60)
    
    print(f"\n🎯 目标地址: {report['target_address']}")
    print(f"📝 合约地址: {report['contract_address']}")
    
    print(f"\n📈 统计数据:")
    print(f"  - 总交易数: {report['total_transactions']}")
    print(f"  - 合约交互数: {report['contract_interactions']}")
    print(f"  - 潜在下线条数: {report['potential_downlines_count']}")
    
    if report['potential_downlines']:
        print(f"\n🔗 潜在下线地址 (前10个):")
        for i, addr in enumerate(list(report['potential_downlines'])[:10], 1):
            print(f"  {i}. {addr}")
        
        remaining = len(report['potential_downlines']) - 10
        if remaining > 0:
            print(f"  ... 还有 {remaining} 个（见输出文件）")
    
    print("\n" + "="*60)
    print("⚠️  注意：需要解析 Input Data 才能 100% 准确")
    print("    建议手动验证重点地址")
    print("="*60 + "\n")


def save_report(report: Dict, filename: str):
    """保存报告到 JSON 文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"✅ 详细报告已保存至: {filename}")


def main():
    print("="*60)
    print("  BSC 下线查询工具（安全本地版）")
    print("="*60)
    
    # 检查 API key 是否配置
    if API_KEY == "YOUR_NEW_API_KEY_HERE":
        print("\n❌ 错误：请先配置 API_KEY")
        print("\n📝 配置步骤：")
        print("  1. 访问 https://bscscan.com/apis 并登录")
        print("  2. 点击 [My Account] → [API Keys]")
        print("  3. 点击 [Add] 创建新 key")
        print("  4. 复制 key，用记事本打开此脚本")
        print("  5. 修改第 12 行的 API_KEY")
        print("  6. 保存后重新运行")
        print("\n⚠️  重要：不要在有聊天记录的平台发送 API key！")
        return
    
    # 创建查询工具
    tool = BSCQueryTool(API_KEY)
    
    # 分析地址
    report = analyze_address(tool, TARGET_ADDRESS, CONTRACT_ADDRESS)
    
    if report and 'error' not in report:
        # 打印报告
        print_report(report)
        
        # 保存报告
        output_file = f"downline_report_{TARGET_ADDRESS[:8]}.json"
        save_report(report, output_file)
        
        # 生成手动验证指南
        print(f"\n📖 手动验证重点地址：")
        print(f"  1. 访问: https://bscscan.com/address/{TARGET_ADDRESS}#transactions")
        print(f"  2. 使用 [Advanced Filter] 筛选合约交互")
        print(f"  3. 逐笔检查 Input Data 中的 referrer 字段")
        print(f"  4. 如果 referrer == {TARGET_ADDRESS}，则是下线")
        
        print(f"\n💡 提高效率：")
        print(f"  - 使用 BSCScan API 批量获取（已实现）")
        print(f"  - 或编写智能合约调用脚本（需要 ABI）")
    
    elif report.get('error') == 'API deprecated':
        print(f"\n🔧 技术说明：")
        print(f"  BSCScan API V1 已弃用，需要迁移到 V2")
        print(f"  V2 文档: https://docs.etherscan.io/v2-migration")
        print(f"  或修改脚本使用 V2 端点")


if __name__ == "__main__":
    main()
