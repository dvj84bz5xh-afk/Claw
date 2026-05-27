#!/usr/bin/env python3
"""
BSC 下线查询完整工具 - V3 版本
修复了所有语法错误，添加详细注释

使用方法：
    1. 安装依赖：pip install requests
    2. 修改下面的配置区域
    3. 运行：python bsc_tool_v3.py
"""

import requests
import json
import time
from typing import Dict, List, Optional

# ============ 配置区域 ============
API_KEY = ""  # 在这里填入你的 BSCScan API key（不要在聊天中发送！）
TARGET_ADDRESS = "0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2"  # 要查询的地址
CONTRACT_ADDRESS = "0xD804569fAa84147690d77080AD7E8CbEe159932d"  # 合约地址
# ====================================


class BSCScanner:
    """BSCScan API 客户端（兼容 V1/V2）"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.bscscan.com/api"
        self.session = requests.Session()
        
    def _request(self, params: Dict) -> Optional[Dict]:
        """发送 API 请求"""
        params['apikey'] = self.api_key
        
        try:
            response = self.session.get(self.base_url, params=params, timeout=30)
            data = response.json()
            
            # 检查响应
            if data.get('status') == '1':
                return {'success': True, 'data': data.get('result', '')}
            else:
                error_msg = data.get('message', '未知错误')
                print(f"⚠️  API 返回错误: {error_msg}")
                
                # 如果是弃用警告，有些情况下仍能获取数据
                if 'deprecated' in error_msg.lower():
                    print("   尝试使用返回的数据（可能不完整）")
                    if data.get('result'):
                        return {'success': True, 'data': data['result']}
                
                return {'success': False, 'error': error_msg}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络错误: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            print(f"❌ 未知错误: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_transactions(self, address: str, limit: int = 10000) -> Optional[List[Dict]]:
        """获取地址的交易列表"""
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'startblock': 0,
            'endblock': 99999999,
            'page': 1,
            'offset': limit,
            'sort': 'asc'
        }
        
        result = self._request(params)
        if result and result.get('success'):
            return result['data']
        return None
    
    def get_internal_txs(self, address: str, limit: int = 10000) -> Optional[List[Dict]]:
        """获取内部交易"""
        params = {
            'module': 'account',
            'action': 'txlistinternal',
            'address': address,
            'page': 1,
            'offset': limit,
            'sort': 'asc'
        }
        
        result = self._request(params)
        if result and result.get('success'):
            return result['data']
        return None
    
    def get_token_transfers(self, address: str, limit: int = 10000) -> Optional[List[Dict]]:
        """获取 Token 转账记录"""
        params = {
            'module': 'account',
            'action': 'tokentx',
            'address': address,
            'page': 1,
            'offset': limit,
            'sort': 'asc'
        }
        
        result = self._request(params)
        if result and result.get('success'):
            return result['data']
        return None


def analyze_downlines(scanner: BSCScanner, target: str, contract: str) -> Dict:
    """
    分析目标地址发展的下线
    
    返回：
        {
            'target': 目标地址,
            'contract': 合约地址,
            'total_txs': 总交易数,
            'contract_txs': 与合约交互的交易数,
            'downlines': 下线地址集合,
            'details': 详细交易列表
        }
    """
    
    print(f"\n{'='*70}")
    print(f"  BSC 下线分析工具")
    print(f"{'='*70}\n")
    print(f"🎯 目标地址: {target}")
    print(f"📝 合约地址: {contract}\n")
    
    # 步骤1：获取交易
    print("步骤 1/5: 获取交易记录...")
    transactions = scanner.get_transactions(target)
    
    if transactions is None:
        print("❌ 无法获取交易记录")
        print("   可能原因：")
        print("   1. API key 无效或已过期")
        print("   2. API 限流（每天 5 次免费调用）")
        print("   3. 地址无效或没有交易")
        return {}
    
    print(f"✅ 找到 {len(transactions)} 笔交易\n")
    
    # 步骤2：筛选与合约相关的交易
    print("步骤 2/5: 筛选与合约的交互...")
    contract_txs = []
    
    for tx in transactions:
        to_addr = tx.get('to', '').lower()
        if to_addr == contract.lower():
            contract_txs.append(tx)
    
    print(f"✅ 找到 {len(contract_txs)} 笔与合约相关的交易\n")
    
    if not contract_txs:
        print("⚠️  未发现与合约的直接交互")
        print("   这可能意味着：")
        print("   1. 该地址尚未与合约交互")
        print("   2. 交互通过代理合约或内部交易进行")
        print("   3. 该地址只是下线，没有发展他人\n")
        
        # 尝试查询内部交易
        print("步骤 2.5: 尝试查询内部交易...")
        internal_txs = scanner.get_internal_txs(target)
        
        if internal_txs:
            print(f"✅ 找到 {len(internal_txs)} 笔内部交易")
            # 这里可以添加对内部交易的分析
        
        return {
            'target': target,
            'contract': contract,
            'total_txs': len(transactions),
            'contract_txs': 0,
            'downlines': set(),
            'details': []
        }
    
    # 步骤3：分析交易
    print("步骤 3/5: 分析交易 Input Data...")
    print(f"{'='*70}")
    
    downlines = set()
    details = []
    
    for i, tx in enumerate(contract_txs, 1):
        tx_hash = tx.get('hash', '')
        from_addr = tx.get('from', '')
        input_data = tx.get('input', '')
        block = tx.get('blockNumber', '')
        
        print(f"\n[{i}/{len(contract_txs)}] 交易哈希: {tx_hash[:30]}...")
        print(f"  发送方: {from_addr}")
        print(f"  区块号: {block}")
        
        # 显示 Input Data 的前 66 个字符（如果有）
        if input_data and input_data != '0x':
            print(f"  Input: {input_data[:66]}..." if len(input_data) > 66 else f"  Input: {input_data}")
        else:
            print(f"  Input: (空)")
        
        # 保存详情
        details.append({
            'hash': tx_hash,
            'from': from_addr,
            'block': block,
            'input': input_data
        })
        
        # 启发式判断：
        # 如果交易的 from != target，说明可能是他人通过 target 的推荐注册
        # 这只是初步判断，需要解析 input data 确认
        if from_addr.lower() != target.lower():
            downlines.add(from_addr)
            print(f"  ⚡ 潜在下线: {from_addr}")
    
    print(f"\n✅ 分析完成\n")
    
    # 步骤4：统计
    print("步骤 4/5: 生成统计...")
    result = {
        'target': target,
        'contract': contract,
        'total_txs': len(transactions),
        'contract_txs': len(contract_txs),
        'downlines': downlines,
        'details': details
    }
    
    return result
    
    # 步骤5：保存结果（在主函数中处理）
    print("步骤 5/5: 保存结果...")


def print_result(result: Dict):
    """打印分析结果"""
    if not result or 'target' not in result:
        return
    
    print("\n" + "="*70)
    print("  分析报告")
    print("="*70 + "\n")
    
    print(f"🎯 目标地址: {result['target']}")
    print(f"📝 合约地址: {result['contract']}")
    
    print(f"\n📊 统计数据:")
    print(f"  - 总交易数: {result['total_txs']}")
    print(f"  - 合约交互数: {result['contract_txs']}")
    print(f"  - 潜在下线条数: {len(result['downlines'])}")
    
    if result['downlines']:
        print(f"\n🔗 潜在下线地址列表 (前 20 个):")
        for i, addr in enumerate(list(result['downlines'])[:20], 1):
            print(f"  {i}. {addr}")
        
        remaining = len(result['downlines']) - 20
        if remaining > 0:
            print(f"  ... 还有 {remaining} 个地址（详见输出文件）")
    
    print("\n" + "="*70)
    print("⚠️  注意事项:")
    print("  1. 需要解析 Input Data 才能 100% 确定下线关系")
    print("  2. 建议手动验证重点地址")
    print("  3. 可以使用 BSCScan 网页版交叉验证")
    print("="*70 + "\n")


def save_result(result: Dict, filename: str):
    """保存结果到 JSON 文件"""
    # 转换 set 为 list（JSON 不支持 set）
    result_copy = result.copy()
    if isinstance(result_copy.get('downlines'), set):
        result_copy['downlines'] = list(result_copy['downlines'])
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result_copy, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 结果已保存至: {filename}")


def main():
    print("="*70)
    print("  BSC 下线查询工具 V3")
    print("="*70)
    
    # 检查配置
    if not API_KEY:
        print("\n❌ 错误：未配置 API_KEY")
        print("\n📝 配置步骤：")
        print("  1. 访问 https://bscscan.com/apis 并登录")
        print("  2. 进入 [My Account] → [API Keys]")
        print("  3. 点击 [Add] 创建新 key")
        print("  4. 复制 key，用记事本打开此脚本")
        print("  5. 修改第 12 行的 API_KEY = '你的key'")
        print("  6. 保存并重新运行")
        print("\n⚠️  安全提示：")
        print("  - 不要在聊天/邮件中发送 API key")
        print("  - 定期更换 key")
        print("  - 如果 key 已暴露，立即删除并创建新 key")
        return
    
    # 创建扫描器
    scanner = BSCScanner(API_KEY)
    
    # 分析
    result = analyze_downlines(scanner, TARGET_ADDRESS, CONTRACT_ADDRESS)
    
    if result and 'target' in result:
        # 打印结果
        print_result(result)
        
        # 保存结果
        output_file = f"bsc_analysis_{TARGET_ADDRESS[:8]}.json"
        save_result(result, output_file)
        
        # 生成手动验证指南
        print(f"\n📖 手动验证指南:")
        print(f"  1. 访问: https://bscscan.com/address/{TARGET_ADDRESS}#transactions")
        print(f"  2. 点击 [Advanced Filter]")
        print(f"  3. To Address 填入: {CONTRACT_ADDRESS}")
        print(f"  4. 点击 [Apply]")
        print(f"  5. 逐笔点击交易哈希，查看 Input Data")
        print(f"  6. 解码后查看 referrer 字段")
        print(f"  7. 如果 referrer == {TARGET_ADDRESS}，则是下线")
        
        print(f"\n💡 提高效率的技巧:")
        print(f"  - 使用 BSCScan API 批量获取（本脚本已实现）")
        print(f"  - 或编写智能合约调用脚本（需要合约 ABI）")
        print(f"  - 对于大量数据，考虑使用数据库存储")


if __name__ == "__main__":
    main()
