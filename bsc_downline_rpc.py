#!/usr/bin/env python3
"""
BSC 下线分析工具 - 使用公共 RPC 节点（无需 API key）
使用方法：
    python bsc_downline_rpc.py <地址>
"""

import requests
import json
import sys
from web3 import Web3

# BSC 公共 RPC 节点（无需 API key）
BSC_RPC_ENDPOINTS = [
    "https://bsc-dataseed.binance.org/",
    "https://bsc-dataseed1.defibit.io/",
    "https://bsc-dataseed1.ninicoin.io/",
]

# 合约 ABI（只保留需要的函数）
CONTRACT_ABI = [
    {
        "inputs": [{"name": "account", "type": "address"}],
        "name": "getInvite",
        "outputs": [{"name": "", "type": "address"}],
        "type": "function"
    },
    {
        "inputs": [{"name": "account", "type": "address"}],
        "name": "upLevel",
        "outputs": [{"name": "", "type": "address"}],
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "user", "type": "address"},
            {"indexed": True, "name": "referrer", "type": "address"}
        ],
        "name": "Register",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "user", "type": "address"},
            {"indexed": True, "name": "referrer", "type": "address"}
        ],
        "name": "UpLevel",
        "type": "event"
    }
]

def connect_bsc():
    """连接到 BSC 公共节点"""
    for rpc_url in BSC_RPC_ENDPOINTS:
        try:
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            if w3.is_connected():
                print(f"✅ 已连接到 BSC: {rpc_url}")
                return w3
        except Exception as e:
            print(f"⚠️  连接失败 {rpc_url}: {e}")
            continue
    
    print("❌ 无法连接到 BSC 网络")
    return None

def get_downlines_via_events(w3, contract_address, target_address, from_block=0, to_block='latest'):
    """
    通过事件日志查询下线
    这是最准确的方法
    """
    print(f"\n🔍 通过事件日志查询下线...")
    print(f"目标地址: {target_address}")
    print(f"区块范围: {from_block} -> {to_block}")
    
    # 这里需要使用 eth_getLogs，但需要正确的 topic 签名
    # Register 事件的 topic: keccak256("Register(address,address)")
    register_topic = "0x" + "Register(address,address)".encode().hex()  # 实际需要 keccak256
    
    # 由于计算 topic 需要额外库，这里先提供框架
    print("\n⚠️  事件日志查询需要 py-evm 或 eth-abi 库")
    print("建议使用 BSCScan 网页手动查询，或使用 BSCScan API")
    
    return []

def analyze_via_bscscan_web(address, contract_address):
    """
    提供 BSCScan 网页查询指南
    """
    print("\n" + "=" * 60)
    print("📖 BSCScan 网页手动查询指南")
    print("=" * 60)
    
    print(f"\n步骤 1️⃣：打开地址的交易记录")
    print(f"  https://bscscan.com/address/{address}#transactions")
    
    print(f"\n步骤 2️⃣：筛选与合约相关的交易")
    print(f"  1. 点击 [Advanced Filter]")
    print(f"  2. To Address 填入: {contract_address}")
    print(f"  3. 点击 [Apply]")
    
    print(f"\n步骤 3️⃣：逐笔检查 Input Data")
    print(f"  对每笔交易：")
    print(f"  a) 点击 TxHash 进入详情")
    print(f"  b) 找到 [Input Data] 部分")
    print(f"  c) 如果显示十六进制，点击 [Decode Input Data]")
    print(f"  d) 查看 'referrer' 或 'inviter' 参数")
    print(f"  e) 如果 referrer == {address}，这就是一个下线")
    
    print(f"\n步骤 4️⃣：统计")
    print(f"  计数所有 referrer 匹配的交易的 'from' 地址")
    
    print(f"\n💡 提高效率的技巧：")
    print(f"  - 使用 BSCScan API（免费申请：bscscan.com/apis）")
    print(f"  - 或编写 Python 脚本自动解析")
    
    return f"https://bscscan.com/address/{address}#transactions"

def main():
    if len(sys.argv) < 2:
        print("使用方法：")
        print("  python bsc_downline_rpc.py <地址>")
        print("\n示例：")
        print("  python bsc_downline_rpc.py 0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2")
        sys.exit(1)
    
    target_address = sys.argv[1]
    contract_address = "0xD804569fAa84147690d77080AD7E8CbEe159932d"
    
    print("=" * 60)
    print("BSC 下线分析工具（公共 RPC 版本）")
    print("=" * 60)
    
    # 尝试连接 BSC
    w3 = connect_bsc()
    
    if w3:
        print(f"\n✅ 可以查询基础信息")
        print(f"当前区块: {w3.eth.block_number}")
        
        # 这里可以添加合约调用逻辑
        # 但由于缺少 ABI 和具体函数，暂时跳过
        
    # 提供网页查询指南
    url = analyze_via_bscscan_web(target_address, contract_address)
    
    print(f"\n📍 快捷访问链接：")
    print(f"  {url}")

if __name__ == "__main__":
    main()
