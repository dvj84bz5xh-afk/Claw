# BSCScan 手动查询下线完整指南

本指南将手把手教你如何使用 BSCScan 网页版查询某个地址发展了多少下线。

---

## 📍 准备工作

**目标：**
- 查询地址：`0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2` 发展了多少下线
- 合约地址：`0xD804569fAa84147690d77080AD7E8CbEe159932d`

---

## 步骤 1️⃣：打开目标地址页面

### 操作：
1. 打开浏览器
2. 访问：`https://bscscan.com/address/0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2`

### 预期结果：
- 页面显示地址详情
- 顶部有多个标签：[Overview] [Transactions] [Internal Txns] [ERC-20 Tokens] [Contract] 等

### 截图说明：
```
┌─────────────────────────────────────────────────┐
│  BscScan - Binance Smart Chain Explorer         │
├─────────────────────────────────────────────────┤
│  [Overview] [Transactions] [Internal Txns]...  │  ← 点击 [Transactions]
│                                               │
│  Address: 0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2 │
│  BNB Balance: X.XXXX BNB                      │
│  TxCount: XXX                                 │
│                                               │
│  [Transactions] 表格：                         │
│  TxHash | Block | Age | From | To | Value...  │
└─────────────────────────────────────────────────┘
```

---

## 步骤 2️⃣：使用高级筛选（重要！）

### 操作：
1. 在 [Transactions] 标签下，找到 **[Advanced Filter]** 按钮（蓝色按钮，在交易列表上方）
2. 点击它，会展开筛选面板

### 筛选面板设置：
```
┌─────────────────────────────────────┐
│  Advanced Filter                   │
├─────────────────────────────────────┤
│  From Address: [空]               │
│  To Address: [填入合约地址]        │  ← 填入 0xD804569fAa84147690d77080AD7E8CbEe159932d
│  Method: [All]                     │  ← 如果有 upLevel/register 选项，选择它们
│  Age: [Any]                       │
│  [Apply Filter] [Reset]           │  ← 点击 Apply
└─────────────────────────────────────┘
```

### 填入的内容：
- **To Address**: `0xD804569fAa84147690d77080AD7E8CbEe159932d`
- **Method**: 留空（或选择 `upLevel` / `register`）

3. 点击 **[Apply Filter]** 按钮

### 预期结果：
- 交易列表只显示与合约相关的交易
- 记录数量会大大减少

---

## 步骤 3️⃣：分析每笔交易

### 操作：
对**每一笔筛选后的交易**，执行以下操作：

#### 3.1 点击交易哈希（TxHash）
- 在交易列表中，找到 **TxHash** 列
- 点击第一个交易哈希（紫色链接，类似 `0x1234...abcd`）

#### 3.2 查看交易详情页
页面会跳转到交易详情页，类似：
```
┌─────────────────────────────────────────────────┐
│  Transaction Details - BscScan                │
├─────────────────────────────────────────────────┤
│  TxHash: 0x1234...abcd                       │
│  Block: 12345678                             │
│  From: 0xAAAA...bbbb                        │
│  To: 0xD804569fAa84147690d77080AD7E8CbEe159932d │
│  Value: 0 BNB                               │
│                                               │
│  [Input Data]                                │  ← 找到这个部分
│  ┌─────────────────────────────────────────┐  │
│  │ 0x60806040...（十六进制数据）          │  │
│  │ [Decode Input Data]  ← 点击这个按钮   │  │
│  └─────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

#### 3.3 解码 Input Data
1. 向下滚动，找到 **[Input Data]** 部分
2. 如果显示的是十六进制（如 `0x60806040...`），点击 **[Decode Input Data]** 按钮
3. 等待解码完成

#### 3.4 查看解码后的参数
解码后会显示类似：
```
┌─────────────────────────────────────────────────┐
│  Decoded Input Data:                          │
├─────────────────────────────────────────────────┤
│  Function: upLevel(uint256 level)             │
│                                               │
│  Parameters:                                  │
│  - level: 1                                  │
│  - referrer: 0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2  │  ← 重点看这里！
│                                               │
│  (如果有 inviter 参数，也类似)                │
└─────────────────────────────────────────────────┘
```

#### 3.5 判断是否下线
- 如果 `referrer` 或 `inviter` == `0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2`（你的目标地址）
- **那么这就是一个下线！**
- 记录下 `From` 地址（这就是下线地址）

#### 3.6 返回交易列表
- 点击浏览器后退按钮
- 或点击顶部标签的 [Transactions]
- 继续分析下一笔交易

---

## 步骤 4️⃣：统计下线数量

### 方法A：手动计数
- 准备一个文本文件或 Excel 表格
- 每找到一个下线，记录：
  - 交易哈希
  - 下线地址（From 地址）
  - 区块号
  - 时间
- 最后统计唯一下线地址数量（去重）

### 方法B：使用浏览器控制台（半自动）

1. 在 BSCScan 交易列表页面，按 **F12** 打开开发者工具
2. 切换到 **[Console]** 标签
3. 粘贴以下脚本并回车：

```javascript
// BSCScan 下线自动统计脚本（简化版）
(function() {
    const TARGET = "0x53774c01a3EDD9890E3ea2D8861CBF3ac9E14d2".toLowerCase();
    const CONTRACT = "0xD804569fAa84147690d77080AD7E8CbEe159932d".toLowerCase();
    
    console.log("🔍 开始扫描交易...");
    
    // 获取交易表格行
    const rows = document.querySelectorAll('table.table tbody tr');
    let downlineCount = 0;
    let downlines = new Set();
    
    rows.forEach((row, index) => {
        const cells = row.querySelectorAll('td');
        if (cells.length < 8) return;
        
        const txHash = cells[1]?.textContent?.trim();
        const toAddr = cells[5]?.textContent?.trim().toLowerCase();
        
        // 筛选与合约相关的交易
        if (toAddr === CONTRACT) {
            console.log(`[${index}] 交易 ${txHash} 与合约交互`);
            // 需要打开详情页才能解析 input data
            // 这里只做初步筛选
        }
    });
    
    console.log(`\n📊 初步筛选完成：`);
    console.log(`与合约交互的交易数: ${downlineCount}`);
    console.log(`请手动打开每笔交易详情，查看 referrer 字段`);
})();
```

**注意**：由于 BSCScan 是动态加载的，这个脚本可能只能获取当前页面的交易（通常 25 笔）。

---

## 步骤 5️⃣：处理大量交易

如果你发现有很多页交易（>100 笔），手动查看不现实。

### 方案1：使用 BSCScan API（推荐）

1. 申请免费 API key：https://bscscan.com/apis
2. 使用我提供的 Python 脚本（需要修改以支持 V2 API）

### 方案2：联系专业人士
- 如果这是执法调查，可以考虑使用专业区块链分析工具（如 Chainalysis, Elliptic）
- 或聘请区块链分析师协助

---

## 📊 示例：完整的下线记录表

建议你创建一个 Excel 或 Markdown 表格，记录：

```markdown
| # | 交易哈希 | 下线地址 | 区块号 | 时间 | 等级 | 备注 |
|---|---------|---------|--------|------|------|------|
| 1 | 0x1234... | 0xAAAA... | 12345678 | 2026-01-01 | 1 | Node |
| 2 | 0x5678... | 0xBBBB... | 12345679 | 2026-01-02 | 2 | Super |
| ... | ... | ... | ... | ... | ... | ... |
```

---

## ⚠️ 常见问题

### Q1：看不到 [Advanced Filter] 按钮？
**A**：可能在页面上方，需要向下滚动一点。或者浏览器窗口太小，试试放大（Ctrl + +）。

### Q2：点击 [Decode Input Data] 没反应？
**A**：可能合约未在 BSCScan 验证，或 API 限流。等待几分钟再试。

### Q3：解码后看不到 referrer 字段？
**A**：可能函数名不是 `referrer`，而是 `inviter`, `upline`, `parent` 等。查看所有参数，找到类似"推荐人"的字段。

### Q4：交易太多，手动看不完？
**A**：使用 BSCScan API 批量获取。申请免费 key，然后运行自动化脚本。

---

## 🎯 快速检查清单

- [ ] 打开目标地址 BSCScan 页面
- [ ] 点击 [Transactions] 标签
- [ ] 点击 [Advanced Filter]
- [ ] To Address 填入合约地址
- [ ] 点击 [Apply Filter]
- [ ] 逐笔点击交易哈希
- [ ] 解码 Input Data
- [ ] 检查 referrer 字段
- [ ] 记录下线地址
- [ ] 统计总数

---

## 📞 需要帮助？

如果你在操作过程中遇到任何问题：
1. 截图当前页面
2. 描述你卡在哪一步
3. 把截图发给我，我帮你分析

---

**最后提醒**：
- 下线数量可能非常多（如果是传销盘，可能有成千上万）
- 手动查询只适合少量数据（<100 笔）
- 大量数据必须使用 API 或专业工具
