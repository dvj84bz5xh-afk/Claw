#!/usr/bin/env python3
"""
BSC 简单查询工具 - 语法 100% 正确
只使用 Python 标准库，无需安装依赖

使用方法：
    python bsc_simple.py
"""

import urllib.request
import urllib.parse
import json
import sys

# ============ 配置区域 ============
API_KEY = ""  # 在这里填入你的 BSCScan API key
TARGET = "0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2"
CONTRACT = "0xD804569fAa84147690d77080AD7E8CbEe159932d"
# ====================================


def call_bscscan_api(module, action, address, api_key, extra_params=None):
    """
    调用 BSCScan API（V1 格式，虽弃用但可能仍可用）
    """
    base_url = "https://api.bscscan.com/api"
    
    params = {
        'module': module,
        'action': action,
        'address': address,
        'apikey': api_key
    }
    
    if extra_params:
        params.update(extra_params)
    
    # 构建 URL
    query_string = urllib.parse.urlencode(params)
    url = f"{base_url}?{query_string}"
    
    try:
        # 发送请求
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Python BSC Query Tool')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        # 检查响应
        if data.get('status') == '1':
            return True, data.get('result', '')
        else:
            error_msg = data.get('message', '未知错误')
            result = data.get('result', '')
            
            # 如果是弃用警告，尝试使用返回的数据
            if 'deprecated' in error_msg.lower() and result:
                print(f"⚠️  API 警告: {error_msg}")
                print("   尝试使用返回的数据...")
                return True, result
            
            return False, f"{error_msg}\n详情: {result}"
    
    except urllib.error.URLError as e:
        return False, f"网络错误: {e}"
    except json.JSONDecodeError as e:
        return False, f"JSON 解析错误: {e}"
    except Exception as e:
        return False, f"未知错误: {e}"


def get_transactions(address, api_key):
    """获取地址的交易列表"""
    params = {
        'startblock': '0',
        'endblock': '99999999',
        'page': '1',
        'offset': '10000',
        'sort': 'asc'
    }
    
    success, result = call_bscscan_api('account', 'txlist', address, api_key, params)
    
    if success:
        return True, result
    else:
        return False, result


def analyze(target_addr, contract_addr, api_key):
    """分析目标地址的下线"""
    
    print("\n" + "="*70)
    print("  BSC 下线分析工具（简单版）")
    print("="*70 + "\n")
    
    print(f"🎯 目标地址: {target_addr}")
    print(f"📝 合约地址: {contract_addr}\n")
    
    # 步骤1：获取交易
    print("步骤 1/4: 获取交易记录...")
    success, result = get_transactions(target_addr, api_key)
    
    if not success:
        print(f"❌ 获取失败: {result}")
        print("\n💡 可能的原因：")
        print("  1. API key 无效或已过期")
        print("  2. BSCScan API V1 已弃用")
        print("  3. 地址无效或没有交易")
        print("\n📖 建议：")
        print("  1. 手动在 BSCScan 网页查询")
        print("  2. 或申请新的 API key 并修改脚本")
        return
    
    transactions = result
    print(f"✅ 找到 {len(transactions)} 笔交易\n")
    
    # 步骤2：筛选合约交易
    print("步骤 2/4: 筛选与合约的交互...")
    contract_txs = []
    
    for tx in transactions:
        to_addr = tx.get('to', '').lower()
        if to_addr == contract_addr.lower():
            contract_txs.append(tx)
    
    print(f"✅ 找到 {len(contract_txs)} 笔与合约相关的交易\n")
    
    if not contract_txs:
        print("⚠️  未发现与合约的直接交互")
        print("   可能该地址只是下线，没有发展他人\n")
        return
    
    # 步骤3：分析
    print("步骤 3/4: 分析交易...")
    print("="*70)
    
    downlines = set()
    
    for i, tx in enumerate(contract_txs[:100], 1):  # 限制前100笔
        tx_hash = tx.get('hash', '')
        from_addr = tx.get('from', '')
        
        print(f"\n[{i}/{min(len(contract_txs), 100)}]")
        print(f"  哈希: {tx_hash}")
        print(f"  发送方: {from_addr}")
        
        # 启发式判断
        if from_addr.lower() != target_addr.lower():
            downlines.add(from_addr)
            print(f"  ⚡ 潜在下线")
    
    print(f"\n✅ 分析完成\n")
    
    # 步骤4：输出结果
    print("步骤 4/4: 生成报告...")
    print("="*70)
    print(f"\n📊 统计结果：")
    print(f"  - 总交易数: {len(transactions)}")
    print(f"  - 合约交互数: {len(contract_txs)}")
    print(f"  - 潜在下线条数: {len(downlines)}")
    
    if downlines:
        print(f"\n🔗 潜在下线地址 (前20个):")
        for i, addr in enumerate(list(downlines)[:20], 1):
            print(f"  {i}. {addr}")
        
        remaining = len(downlines) - 20
        if remaining > 0:
            print(f"  ... 还有 {remaining} 个")
    
    print("\n" + "="*70)
    print("⚠️  注意：需要解析 Input Data 才能 100% 确定")
    print("    建议手动验证重点交易")
    print("="*70 + "\n")
    
    # 保存结果
    output_file = f"bsc_result_{target_addr[:8]}.json"
    output_data = {
        'target': target_addr,
        'contract': contract_addr,
        'total_txs': len(transactions),
        'contract_txs': len(contract_txs),
        'potential_downlines_count': len(downlines),
        'potential_downlines': list(downlines),
        'transactions': contract_txs[:100]  # 只保存前100笔
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 结果已保存至: {output_file}\n")


def main():
    print("="*70)
    print("  BSC 简单查询工具")
    print("="*70)
    
    # 检查配置
    if not API_KEY:
        print("\n❌ 错误：请先配置 API_KEY")
        print("\n📝 配置步骤：")
        print("  1. 访问 https://bscscan.com/apis")
        print("  2. 登录后创建 API key")
        print("  3. 用记事本打开此脚本")
        print("  4. 修改第 11 行的 API_KEY")
        print("  5. 保存后重新运行")
        print("\n⚠️  安全提示：不要在聊天中发送 API key！")
        return
    
    # 分析
    analyze(TARGET, CONTRACT, API_KEY)


if __name__ == "__main__":
    main()
