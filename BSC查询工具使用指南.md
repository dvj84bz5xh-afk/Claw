# BSC 链上数据查询工具 - 使用指南

## ⚠️ 安全提醒

**API Key 是私密信息！**
- ✅ 在本地运行此脚本
- ✅ API Key 仅输入到脚本提示符（不会保存）
- ❌ 不要在网络上发送 API Key
- ❌ 不要将 API Key 写入代码文件

---

## 📦 安装依赖

```bash
pip install requests
```

---

## 🚀 使用方法

### 步骤1：获取 BSCScan API Key

1. 访问 https://bscscan.com/apis
2. 注册账号（免费）
3. 创建 API Key
4. **复制保存好 Key**

### 步骤2：运行脚本

```bash
python bsc_query_tool.py
```

### 步骤3：输入信息

脚本会依次提示输入：

```
1. 请输入 BSCScan API Key: 
   → 粘贴您的 API Key（输入时不显示，这是正常的）

2. 合约地址 (例如 0xD804569fAa84147690d77080AD7E8CbEe159932d): 
   → 输入：0xD804569fAa84147690d77080AD7E8CbEe159932d

3. 要查询的地址 (例如 0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2): 
   → 输入：0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2
```

---

## 📋 输出示例

```
============================================================
BSC 链上数据查询工具
============================================================

📝 使用前准备：
1. 访问 https://bscscan.com/apis 注册并获取 API Key
2. 在下方输入您的 API Key（不会保存，仅本次使用）

请输入 BSCScan API Key: [输入时不显示]

============================================================
请输入查询参数：
合约地址 (例如 0xD804569fAa84147690d77080AD7E8CbEe159932d): 0xD804569fAa84147690d77080AD7E8CbEe159932d
要查询的地址 (例如 0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2): 0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2

============================================================
开始查询...

[1/3] 获取合约 ABI...
✅ ABI 获取成功

📋 合约中的读取函数：
  - userInfo(address)
  - getInvite(address)
  - viewUserInfo(address)
  ...

[2/3] 分析交易记录...

📊 查询结果：
  - upLevel 调用次数（发展下线数）: 15
  - 合约交互次数: 23

  - 疑似下线地址：
    0x1234...abcd
    0x5678...ef01
    ...

[3/3] 获取详细信息...

💡 如需获取更详细的信息（如下线具体数量、等级等），请：
1. 访问: https://bscscan.com/address/0xD804569fAa84147690d77080AD7E8CbEe159932d#readContract
2. 找到类似以下名称的函数（不同合约命名可能不同）：
   - userInfo
   - getUserInfo
   - getInvite
   - getReferral
3. 输入地址: 0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2
4. 点击 Query 查看结果

============================================================
查询完成！
============================================================
```

---

## 🔍 手动查询指南（配合脚本使用）

### 步骤1：访问合约 Read Contract

```
https://bscscan.com/address/0xD804569fAa84147690d77080AD7E8CbEe159932d#readContract
```

### 步骤2：查找关键函数

在页面中找到以下函数（名称可能不同）：

| 可能的函数名 | 功能 | 返回信息 |
|--------------|------|----------|
| `userInfo` | 查询用户信息 | 等级、邀请数量、金额等 |
| `viewUserInfo` | 查看用户信息 | 同上 |
| `getUser` | 获取用户数据 | 同上 |
| `getInvite` | 查询邀请人 | 上级地址 |
| `getReferral` | 获取推荐关系 | 推荐人地址 |

### 步骤3：输入地址并查询

1. 点击函数名展开
2. 输入地址：`0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2`
3. 点击 **Query** 按钮

### 步骤4：解读返回结果

**典型返回格式：**

```
[0] isActive: true
[1] amount: 1000000000000000000
[2] amountUsdt: 5000000000000000000
[3] calMintReward: 0
[4] rewardMintDebt: 0
[5] level: 1                        ← 等级（0=普通,1=Node,2=Super,3=Top）
[6] inviteNum: 15                   ← 直接下线数量！
[7] inviteAmount: 5000000000000000000  ← 直接下线总金额
[8] invite2Amount: 2000000000000000000 ← 二级下线总金额
[9] nodeNum: 3                     ← 下级节点数
[10] superNum: 0                   ← 下级超级节点数
```

**关键字段：**
- `inviteNum` = **直接下线人数**
- `nodeNum` = 下级节点数（等级≥1）
- `superNum` = 下级超级节点数（等级≥2）
- `level` = 该地址的等级

---

## 📊 统计总下线数量

### 方法1：只看直接下线（快速）

从 `viewUserInfo` 结果中读取：
```
inviteNum = 15 人（直接下线）
```

### 方法2：统计所有下线（递归）

如果需要统计**所有层级的下线总数**，需要：

1. 对 `inviteNum` 个直接下线，逐一查询他们的 `inviteNum`
2. 递归统计
3. 汇总总数

**示例：**
```
地址 A (level 2, inviteNum=3)
├── 下线1 (level 1, inviteNum=5)
│   ├── 下线1-1 (level 0, inviteNum=0)
│   ├── 下线1-2 (level 0, inviteNum=0)
│   └── 下线1-3 (level 0, inviteNum=0)
├── 下线2 (level 0, inviteNum=0)
└── 下线3 (level 1, inviteNum=2)
    ├── 下线3-1 (level 0, inviteNum=0)
    └── 下线3-2 (level 0, inviteNum=0)

总下线数 = 3 (A的直接) + 5 (下线1的) + 2 (下线3的) = 10 人
```

---

## 🛠️ 高级功能（需要编程）

### 使用 Web3.py 直接调用合约

**安装：**
```bash
pip install web3
```

**示例代码：**
```python
from web3 import Web3, HTTPProvider

# 连接 BSC
w3 = Web3(HTTPProvider('https://bsc-dataseed.binance.org/'))

# 合约 ABI（从 BSCScan 获取）
abi = [...]  # 从 API 获取

contract = w3.eth.contract(
    address='0xD804569fAa84147690d77080AD7E8CbEe159932d',
    abi=abi
)

# 调用 viewUserInfo
result = contract.functions.viewUserInfo(
    '0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2'
).call()

print(f"直接下线数量: {result[6]}")
print(f"等级: {result[5]}")
```

---

## 🔗 快速访问链接

### 1. 查询地址主页
```
https://bscscan.com/address/0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2
```

### 2. 查询地址内部交易（合约调用）
```
https://bscscan.com/address/0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2#internaltx
```

### 3. 读取合约函数
```
https://bscscan.com/address/0xD804569fAa84147690d77080AD7E8CbEe159932d#readContract
```

### 4. 查询上级推荐人（getInvite）
```
https://bscscan.com/address/0xD804569fAa84147690d77080AD7E8CbEe159932d#readContract
```
找到 `getInvite`，输入 `0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2`，点击 Query

---

## 📝 记录模板

```
=== 地址信息 ===
地址：0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2
等级：□ 0(普通) □ 1(Node) □ 2(Super) □ 3(Top)

=== 下线统计 ===
直接下线数量：______ 人
下级节点数：______ 个
下级超级节点数：______ 个
直接下线总金额：______ USDT
二级下线总金额：______ USDT

=== 推荐关系 ===
上级推荐人：0x...
下级列表：
  - 0x... (等级 ?, 下线 ?人)
  - 0x... (等级 ?, 下线 ?人)
  - ...

=== 交易统计 ===
总交易数：______
合约交互次数：______
upLevel 调用次数：______
```

---

## ❓ 常见问题

### Q1：脚本提示 "获取 ABI 失败" 怎么办？

**可能原因：**
- API Key 错误
- 合约未验证
- API 限流（免费版 5 次/秒）

**解决方案：**
- 检查 API Key 是否正确
- 如果合约未验证，只能使用交易记录分析
- 等待几秒后重试

### Q2：如何找到合约的所有函数？

**方法：**
1. 访问 `https://bscscan.com/address/[合约地址]#readContract`
2. 页面会列出所有公开的可读函数
3. 记录函数名称，用于脚本解析

### Q3：inviteNum 和 nodeNum 有什么区别？

| 字段 | 含义 | 说明 |
|------|------|------|
| `inviteNum` | **直接邀请人数** | 该地址直接推荐的用户数 |
| `nodeNum` | **下级节点数** | 该地址下，等级≥1 的下级数 |
| `superNum` | **下级超级节点数** | 该地址下，等级≥2 的下级数 |

**示例：**
```
地址 A (level 2, inviteNum=5, nodeNum=3, superNum=1)

说明：
- A 直接推荐了 5 个人
- 这 5 个人中，有 3 个达到了 Node 等级（level≥1）
- 这 3 个 Node 中，有 1 个达到了 Super 等级（level≥2）
```

---

## 🎯 下一步

**选项1：** 立即运行脚本
```bash
python bsc_query_tool.py
```

**选项2：** 手动在 BSCScan 查询
- 访问合约 Read Contract 页面
- 调用 `viewUserInfo` 或类似函数

**选项3：** 我帮您解读查询结果
- 把查询结果截图或复制文本发给我
- 我帮您分析下线数量、等级、资金流向

---

**准备好后，请告诉我：**
- ✅ "运行成功" / "运行失败（错误信息）"
- ✅ "手动查询完成，结果是..."
- ✅ "需要帮助解读结果"
