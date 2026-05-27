# RAG-Anything 部署测试指南

**项目地址**：https://github.com/HKUDS/RAG-Anything  
**Star 数**：2,622+（本周新增）  
**论文**：*RAG-Anything: All-in-One Multimodal RAG System*（arXiv:2510.12323）  
**核心特点**：全栈多模态 RAG 框架，支持 PDF/Office/图像/表格/公式，完全本地化部署

---

## 一、核心设计哲学

传统 RAG 系统只能处理纯文本，而现代文档包含大量非文本内容：
- 技术文档中的**流程图、架构图**
- 财报中的**数据表格**
- 学术论文中的**数学公式**
- 演示文稿中的**图表、截图**

RAG-Anything 的核心价值：**一个框架处理所有内容类型**，不需要多个专门工具拼接。

---

## 二、系统架构详解

### 完整流水线（5 个阶段）

```
[文档输入]
    ↓
[1. 文档解析] → MinerU/Docling/PaddleOCR 解析
    ↓
[2. 多模态内容理解] → 图像分析、表格解释、公式解析
    ↓
[3. 多模态知识图谱] → 跨模态实体提取、关系映射
    ↓
[4. 模态感知检索] → 向量+图谱混合检索
    ↓
[查询结果输出]
```

### 阶段1：文档解析

**支持三种解析器**：

| 解析器 | 优势 | 适用场景 |
|---------|------|----------|
| **MinerU** | 高保真结构提取、复杂布局支持 | PDF 论文、技术报告 |
| **Docling** | Office 文档优化、格式保留好 | DOCX/PPTX/XLSX |
| **PaddleOCR** | OCR 能力强 | 扫描版 PDF、图像 |

**关键功能**：
- 自适应内容分解：自动分割文本块、视觉元素、表格、公式
- 文档层次提取：保留章节结构（"belongs_to" 关系链）
- 通用格式支持：PDF/Office/图像

---

### 阶段2：多模态内容理解

**四个专门分析器**：

| 分析器 | 功能 | 输出 |
|---------|------|------|
| **Visual Content Analyzer** | 图像分析、空间关系提取 | 上下文感知描述说明 |
| **Structured Data Interpreter** | 表格数据解释、趋势识别 | 统计模式识别结果 |
| **Mathematical Expression Parser** | LaTeX 公式解析 | 概念映射关系 |
| **Extensible Modality Handler** | 自定义内容类型处理 | 可插拔处理器 |

**VLM 增强查询**（新增功能）：
- 当文档包含图像时，系统自动调用 VLM 进行深度分析
- 支持 GPT-4o、Claude 3.5 Sonnet 等视觉语言模型
- 图像 + 文本上下文联合理解

---

### 阶段3：多模态知识图谱

**核心创新**：将非文本内容也作为知识图谱的一等公民。

传统知识图谱：
```
(实体1) --[关系]--> (实体2)
  文本         文本          文本
```

RAG-Anything 知识图谱：
```
(文本实体) --[关系]--> (文本实体)
(图像实体) --[包含]--> (文本实体)
(表格实体) --[引用]--> (图像实体)
(公式实体) --[推导]--> (表格实体)
```

**加权关系评分**：
- 根据语义接近度和上下文重要性分配量化相关性分数
- 影响检索排序结果

---

### 阶段4：模态感知检索

**混合检索机制**：
1. **向量相似度搜索**：嵌入模型将查询和文档块转为向量
2. **图谱遍历算法**：通过实体关系扩展检索范围
3. **模态感知排序**：根据查询意图调整不同内容类型的权重

**四种查询模式**：
```python
# 1. 纯文本查询（基础）
result = await rag.aquery("问题", mode="hybrid")

# 2. VLM 增强查询（自动分析检索到的图像）
result = await rag.aquery("分析文档中的图表", mode="hybrid")
# 自动启用 vision_model_func

# 3. 多模态内容查询（指定多模态内容）
result = await rag.aquery_with_multimodal(
    "解释这个公式",
    multimodal_content=[{
        "type": "equation",
        "latex": "P(d|q) = \\frac{P(q|d) \\cdot P(d)}{P(q)}",
        "equation_caption": "文档相关性概率"
    }],
    mode="hybrid"
)

# 4. 原生 LightRAG 查询（直接访问底层）
result = rag.query("问题", mode="naive")  # 无图遍历
```

---

## 三、与您的诈骗调查工作的结合点

### 应用点1：诈骗案例文档库

**当前问题**：
- 诈骗案例文档格式多样（PDF 报告、Word 陈述、Excel 交易记录、截图证据）
- 传统 RAG 只能处理文本内容，图像证据、表格数据被忽略

**使用 RAG-Anything 优化**：
1. 将所有案例文档（PDF/Word/Excel/图像）导入 RAG-Anything
2. 系统自动解析文本、表格、图像、公式
3. 构建跨模态知识图谱（"这张截图" 关联到 "这份交易记录"）
4. 查询时：可以同时搜索文本内容、图像视觉内容、表格数据

**示例查询**：
```
"找出所有涉及'bet365'的案例中，转账金额超过 50 万的，
 并且附件截图中有银行 LOGO 的案例"
```

---

### 应用点2：加密货币交易路径分析

**当前问题**：
- 交易路径图（PDF 报告）包含大量流程图、表格
- 传统工具只能提取文本，丢失可视化信息

**使用 RAG-Anything 优化**：
1. 导入交易路径分析报告（PDF）
2. 系统解析流程图（图像）、交易表格（表格）、描述文本
3. 查询："展示从地址 A 到地址 B 的资金流向图"
4. 系统返回：相关文本描述 + 流程图 + 交易表格

---

### 应用点3：培训课程材料管理

**当前问题**：
- 加密货币洗钱课程包含大量图表、公式、案例表格
- 传统 RAG 无法有效检索图像和表格内容

**使用 RAG-Anything 优化**：
1. 导入课程所有材料（PPTX、PDF、DOCX）
2. 系统构建完整知识图谱
3. 学员查询："解释 UTXO 模型和账户模型的区别"
4. 系统返回：公式解释（LaTeX）+ 对比表格 + 架构图

---

## 四、部署指南（为您的工作环境定制）

### 方案A：基础安装（推荐优先尝试）

```powershell
# 1. 进入已克隆的仓库目录
cd c:\Users\10127\WorkBuddy\Claw\RAG-Anything

# 2. 创建虚拟环境（可选但推荐）
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. 使用 uv 安装（比 pip 更快）
# 先安装 uv（如果未安装）
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 4. 安装 RAG-Anything（基础版本）
uv pip install -e .

# 5. 安装可选依赖（图像格式支持）
uv pip install -e ".[image]"

# 6. 安装可选依赖（文本格式支持）
uv pip install -e ".[text]"

# 7. 安装所有可选依赖
uv pip install -e ".[all]"
```

---

### 方案B：LibreOffice 集成（Office 文档支持）

如果需要处理 DOCX/PPTX/XLSX 文件：

```powershell
# 1. 下载安装 LibreOffice
# 访问：https://www.libreoffice.org/download/download/
# 安装到默认位置

# 2. 验证 LibreOffice 安装
& "C:\Program Files\LibreOffice\program\soffice.exe" --version

# 3. 安装 RAG-Anything（包含 Office 支持）
cd c:\Users\10127\WorkBuddy\Claw\RAG-Anything
uv pip install -e ".[all]"
```

---

### 方案C：使用 PyPI 安装（不克隆仓库）

```powershell
# 1. 直接安装（无需克隆）
pip install raganything

# 2. 安装可选依赖
pip install "raganything[all]"

# 3. 下载示例代码
# 需要从仓库克隆示例代码
git clone https://github.com/HKUDS/RAG-Anything.git
cd RAG-Anything
```

---

## 五、测试步骤（验证安装是否成功）

### 测试1：MinerU 安装验证

```powershell
# 验证 MinerU 是否正确安装
mineru --version

# 如果报错，手动检查
python -c "from raganything import RAGAnything; rag = RAGAnything(); print('✅ MinerU installed properly' if rag.check_parser_installation() else '❌ MinerU installation issue')"
```

---

### 测试2：Office 文档解析测试（无需 API Key）

```powershell
cd c:\Users\10127\WorkBuddy\Claw\RAG-Anything
python examples\office_document_test.py --file "path\to\your\document.docx"
```

---

### 测试3：图像格式解析测试（无需 API Key）

```powershell
cd c:\Users\10127\WorkBuddy\Claw\RAG-Anything
python examples\image_format_test.py --file "path\to\your\image.jpg"
```

---

### 测试4：完整端到端测试（需要 OpenAI API Key）

```python
# 创建 test_raga.py
import asyncio
from raganything import RAGAnything, RAGAnythingConfig
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc
from functools import partial

async def main():
    # 配置 API（需要 OpenAI 或兼容接口）
    api_key = "your-api-key"
    base_url = "https://api.openai.com/v1"  # 或您的自定义端点

    # 创建配置
    config = RAGAnythingConfig(
        working_dir="./rag_storage",
        parser="mineru",
        parse_method="auto",
        enable_image_processing=True,
        enable_table_processing=True,
        enable_equation_processing=True,
    )

    # 定义 LLM 模型函数
    def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
        return openai_complete_if_cache(
            "gpt-4o-mini",
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key=api_key,
            base_url=base_url,
            **kwargs,
        )

    # 定义视觉模型函数（用于图像分析）
    def vision_model_func(prompt, system_prompt=None, history_messages=[], image_data=None, messages=None, **kwargs):
        if messages:
            return openai_complete_if_cache(
                "gpt-4o",
                "",
                system_prompt=None,
                history_messages=[],
                messages=messages,
                api_key=api_key,
                base_url=base_url,
                **kwargs,
            )
        else:
            return llm_model_func(prompt, system_prompt, history_messages, **kwargs)

    # 定义嵌入函数
    embedding_func = EmbeddingFunc(
        embedding_dim=3072,
        max_token_size=8192,
        func=partial(
            openai_embed.func,
            model="text-embedding-3-large",
            api_key=api_key,
            base_url=base_url,
        ),
    )

    # 初始化 RAG-Anything
    rag = RAGAnything(
        config=config,
        llm_model_func=llm_model_func,
        vision_model_func=vision_model_func,
        embedding_func=embedding_func,
    )

    # 处理文档
    await rag.process_document_complete(
        file_path="path\to\your\document.pdf",
        output_dir="./output",
        parse_method="auto"
    )

    # 查询
    result = await rag.aquery(
        "文档的主要内容是什么？",
        mode="hybrid"
    )
    print("查询结果:", result)

if __name__ == "__main__":
    asyncio.run(main())
```

运行测试：
```powershell
cd c:\Users\10127\WorkBuddy\Claw\RAG-Anything
python test_raga.py
```

---

## 六、与类似工具对比

| 特性 | RAG-Anything | LangChain | LlamaIndex | RAGFlow |
|------|----------|-----------|--------------|----------|
| 多模态支持 | ✅ 原生支持 | ⚠️ 有限 | ⚠️ 有限 | ✅ 支持 |
| 知识图谱 | ✅ 多模态图谱 | ✅ 文本图谱 | ✅ 文本图谱 | ❌ 无 |
| Office 文档 | ✅ 原生支持 | ⚠️ 需要转换 | ⚠️ 需要转换 | ❌ 有限 |
| 本地部署 | ✅ 完全本地 | ✅ | ✅ | ✅ |
| 依赖外部 API | ❌ 可选 | ✅ 通常需要 | ✅ 通常需要 | ❌ 可选 |
| 复杂度 | 中 | 高 | 中 | 中 |

---

## 七、下一步行动

### 立即行动（今天）

1. **完成基础安装**
   ```powershell
   cd c:\Users\10127\WorkBuddy\Claw\RAG-Anything
   uv pip install -e ".[all]"
   ```

2. **运行解析测试（无需 API Key）**
   ```powershell
   python examples\office_document_test.py --file "your-file.docx"
   ```

3. **准备测试文档**
   - 收集您的诈骗案例文档（PDF/Word/Excel）
   - 确保 LibreOffice 已安装（如果需要处理 Office 文档）

### 本周行动

4. **配置 API Key**（如果需要 LLM 功能）
   - 创建 `.env` 文件
   - 填入 OPENAI_API_KEY 或兼容接口的 Key

5. **导入第一批文档**
   - 选择 5-10 个典型诈骗案例文档
   - 运行 `process_document_complete`
   - 测试多模态查询效果

6. **评估效果**
   - 对比传统文本 RAG 的检索效果
   - 检查图像、表格内容是否被正确检索

### 长期行动（本月内）

7. **构建完整案例库**
   - 将所有历史案例导入 RAG-Anything
   - 构建跨案例的知识图谱

8. **集成到调查工作流**
   - 将 RAG-Anything 查询封装为 Skill（用于 GenericAgent）
   - 实现"输入案例编号 → 返回相似历史案例"的功能

9. **优化查询效果**
   - 调整解析器参数（MinerU/Docling）
   - 优化嵌入模型选择
   - 调整混合检索权重

---

## 八、常见问题排查

### 问题1：MinerU 安装失败

**解决方案**：
```powershell
# 使用清华镜像源
pip install magic-pdf -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或手动下载模型
# 参考：https://github.com/opendatalab/MinerU/blob/master/README.md#model-source-configuration
```

---

### 问题2：LibreOffice 找不到

**解决方案**：
- 确保 LibreOffice 安装到默认路径
- 或设置环境变量 `LIBREOFFICE_PATH`
- 检查 `soffice.exe` 是否在 PATH 中

---

### 问题3：API 调用失败

**解决方案**：
- 检查 `.env` 文件中的 API Key 是否正确
- 如果使用代理，设置 `no_proxy = {'http': None, 'https': None}`
- 或切换到本地模型（Ollama + nomic-embed）

---

### 问题4：内存不足

**解决方案**：
- 减小 `max_token_size`（默认 8192）
- 使用更小的嵌入模型（如 `text-embedding-3-small`）
- 分批处理大型文档

---

## 九、学习资源

| 资源 | 链接 |
|------|------|
| 官方仓库 | https://github.com/HKUDS/RAG-Anything |
| 论文（arXiv） | https://arxiv.org/abs/2510.12323 |
| LightRAG（基础框架） | https://github.com/HKUDS/LightRAG |
| MinerU 文档 | https://github.com/opendatalab/MinerU |
| Discord 社区 | https://discord.gg/yF2MmDJyGJ |
| 微信交流群 | 见 README 中的二维码 |

---

**部署总结**：RAG-Anything 的核心价值在于**统一处理多模态内容**。对您的诈骗调查工作，最直接的收益是：**将案例文档（PDF 报告 + Word 陈述 + Excel 交易记录 + 截图证据）统一导入，构建跨模态知识库，实现"一句话检索所有相关内容"**。

**下一步**：完成基础安装 → 运行测试脚本 → 导入第一批诈骗案例文档 → 评估效果
