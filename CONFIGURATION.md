# 配置说明文档

## ✅ 已配置项

### 1. 数据库（Supabase）
```
✅ SUPABASE_URL: https://fftkazutsznpjvkqctvy.supabase.co
✅ SUPABASE_KEY: 已配置
✅ SUPABASE_SERVICE_KEY: 已配置
⚠️  DATABASE_URL: 需要补充数据库密码
```

**获取数据库密码：**
1. 访问：https://supabase.com/dashboard/project/fftkazutsznpjvkqctvy
2. 点击 Settings → Database
3. 找到 "Connection string" 部分
4. 复制完整的 `postgresql://` 连接字符串
5. 更新 `.env` 文件中的 `DATABASE_URL`

### 2. LLM API
```
✅ ANTHROPIC_API_KEY: 已配置
⚠️  OPENAI_API_KEY: 需要配置（用于向量嵌入）
```

**重要说明：Anthropic vs OpenAI**

您已配置 Anthropic API（用于所有 Agent 的推理），这完全没问题！但有一个关键点：

- **Anthropic Claude**: 用于 Agent 推理、决策、文本生成 ✅
- **OpenAI Embeddings**: 用于语义搜索的向量嵌入 ⚠️

**为什么需要 OpenAI？**

系统使用 **语义搜索** 来检索相关的 WeChat 消息、新闻等。这需要将文本转换为向量（embeddings）。

目前支持的 embedding 提供商：
- OpenAI: `text-embedding-3-large` (推荐)
- Anthropic: ❌ 暂无 embedding API

**解决方案：**

**选项 1：添加 OpenAI API Key（推荐）**
```bash
OPENAI_API_KEY=sk-xxxxx  # 仅用于 embedding，成本低
```
- 成本：~$0.13/百万tokens（非常便宜）
- 用途：仅用于生成向量，不用于文本生成
- 获取：https://platform.openai.com/api-keys

**选项 2：禁用语义搜索功能**
```bash
ENABLE_SEMANTIC_SEARCH=false  # 添加此行到 .env
```
- 系统仍可运行，但无法使用语义搜索
- 影响：无法智能检索历史消息和上下文

**选项 3：使用本地 Embedding 模型**
```bash
EMBEDDING_PROVIDER=local  # 使用 sentence-transformers
```
- 完全免费，但需要本地计算资源
- 速度较慢，质量略低于 OpenAI

### 3. 金融数据源
```
⚠️  TUSHARE_TOKEN: 需要配置
✅ 数据源策略：仅使用 Tushare（已移除 AKShare）
```

**获取 Tushare Token：**
1. 注册：https://tushare.pro/register
2. 实名认证（需要身份证）
3. 获取 Token：https://tushare.pro/user/token
4. 更新 `.env`：`TUSHARE_TOKEN=your_token_here`

**Tushare 积分说明：**
- 注册即可获得 100 积分（基础接口可用）
- 日线数据、基本面数据：免费
- 高级数据（实时行情、分钟线）：需要积分
- 积分获取：社区互动、捐赠

**当前系统使用的接口（免费）：**
- ✅ `stock_basic` - 股票列表
- ✅ `daily` - 日线行情
- ✅ `income` - 利润表
- ✅ `balancesheet` - 资产负债表
- ✅ `cashflow` - 现金流量表
- ✅ `fina_indicator` - 财务指标
- ✅ `stock_company` - 公司信息

## 📋 待配置项（可选）

### 社交媒体（外部信号源）
```
⚠️  TWITTER_BEARER_TOKEN: 可选（需要付费 $100/月）
⚠️  REDDIT_CLIENT_ID: 可选（免费）
⚠️  REDDIT_CLIENT_SECRET: 可选（免费）
```

**建议：**
- 初期可以跳过 Twitter（成本高）
- Reddit 免费但需要申请
- 专注 WeChat 信号（系统核心）

### 其他数据源
```
⚠️  ALPHAVANTAGE_API_KEY: 可选（美股数据）
```

## 🚀 快速启动步骤

### 步骤 1：补充必需配置
```bash
# 编辑 .env 文件
nano .env

# 必须填写：
1. DATABASE_URL（从 Supabase 获取完整连接字符串）
2. TUSHARE_TOKEN（从 Tushare 获取）
3. OPENAI_API_KEY（用于 embedding）或设置 ENABLE_SEMANTIC_SEARCH=false
```

### 步骤 2：初始化数据库
```bash
# 方案 A：使用 psql
psql $DATABASE_URL < database/schema.sql

# 方案 B：使用 Supabase Dashboard
# 1. 访问 https://supabase.com/dashboard/project/fftkazutsznpjvkqctvy
# 2. 点击 SQL Editor
# 3. 复制 database/schema.sql 内容
# 4. 点击 Run
```

### 步骤 3：安装依赖
```bash
pip install -r requirements.txt
```

### 步骤 4：测试配置
```bash
# 测试数据库连接
python -c "from database import get_db; db = get_db(); print('✅ Database connected')"

# 测试 Tushare
python -c "from tools.datasources.tushare_tool import tushare_api; print('✅ Tushare connected' if tushare_api.pro else '❌ Tushare token missing')"

# 测试 Anthropic
python -c "from anthropic import Anthropic; c = Anthropic(); print('✅ Anthropic connected')"
```

### 步骤 5：运行系统
```bash
# 查看系统状态
python orchestrator.py --status

# 运行完整流程（需要 WeChat 导出文件）
python orchestrator.py --mode full --wechat-export /path/to/export

# 仅执行策略（不收集新信号）
python orchestrator.py --mode execution_only
```

## ⚙️ 配置文件说明

### `.env` - 环境变量
- API 密钥和敏感信息
- 不要提交到 Git
- 已在 `.gitignore` 中

### `config/model_config.yaml` - LLM 模型配置
```yaml
models:
  primary:
    provider: "anthropic"
    model: "claude-sonnet-4-20250514"  # 您的模型
    temperature: 0.7
```

### `config/strategy_config.yaml` - 策略配置
```yaml
strategy:
  signal_weights:
    wechat: 0.65       # WeChat 权重 ≥ 0.6
    external: 0.20     # 外部源 ≤ 0.4
```

### `config/agent_tools.yaml` - 工具分配
- 定义每个 Agent 可使用的工具
- 已配置 Tushare 工具

## 📊 成本估算

### 当前配置（最小成本）
| 服务 | 用途 | 成本 |
|------|------|------|
| Supabase | 数据库 | 免费额度（500MB） |
| Anthropic Claude | Agent 推理 | 按使用付费 |
| OpenAI Embeddings | 语义搜索 | ~$1-5/月 |
| Tushare | 中国股市数据 | 免费（基础） |
| Yahoo Finance | 全球股市数据 | 完全免费 |

**预估月成本：$5-20**（取决于使用量）

### 优化建议
1. 使用 Claude 的 Prompt Caching（已启用）- 节省 90% token 成本
2. Embedding 使用批处理 - 减少 API 调用
3. Tushare 优先使用免费接口
4. 暂不启用 Twitter（$100/月）

## 🔧 故障排查

### 问题 1：数据库连接失败
```bash
# 检查 DATABASE_URL 格式
echo $DATABASE_URL

# 应该类似：
# postgresql://postgres.fftkazutsznpjvkqctvy:PASSWORD@aws-0-us-west-1.pooler.supabase.com:6543/postgres
```

### 问题 2：Tushare Token 无效
```bash
# 测试 token
python -c "import tushare as ts; ts.set_token('YOUR_TOKEN'); pro = ts.pro_api(); print(pro.stock_basic())"
```

### 问题 3：Anthropic API 报错
```bash
# 测试 API
curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data '{"model": "claude-sonnet-4-20250514", "max_tokens": 1024, "messages": [{"role": "user", "content": "Hello"}]}'
```

## ✅ 配置清单

完成以下配置后系统即可运行：

- [x] Supabase URL 和 Keys ✅
- [ ] DATABASE_URL（需要密码）⚠️
- [x] ANTHROPIC_API_KEY ✅
- [ ] OPENAI_API_KEY（用于 embedding）⚠️
- [ ] TUSHARE_TOKEN ⚠️
- [ ] 数据库 Schema 初始化
- [ ] Python 依赖安装

**3 个待办事项即可启动！** 🎯
