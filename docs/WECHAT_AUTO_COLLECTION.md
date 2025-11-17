# 微信自动化接收方案

如何自动化地从微信群聊和公众号获取内容，无需手动导出。

---

## ⚠️ 重要提示

**合规性说明**：
- ✅ **企业微信API**：官方支持，完全合规
- ⚠️ **个人微信机器人**：可能违反微信服务条款，有封号风险
- ✅ **公众号RSS**：合规，但功能有限
- ⚠️ **第三方工具**：谨慎使用，注意安全

**推荐顺序**：企业微信 > 定时自动导出 > 个人微信机器人

---

## 方案1：企业微信API（推荐）

### 优点
✅ 官方支持，完全合规
✅ 稳定可靠
✅ 支持群聊、应用消息
✅ 可以发送消息

### 缺点
❌ 需要企业认证
❌ 需要加入企业微信群
❌ 不支持个人微信群

### 实现步骤

#### 1. 创建企业微信应用

1. 注册企业微信：https://work.weixin.qq.com/
2. 创建自建应用
3. 获取 `corp_id`, `agent_id`, `secret`

#### 2. 实现企业微信接收器

```python
# tools/datasources/wecom_receiver.py
"""企业微信消息接收器"""

import requests
from typing import List, Dict, Any
from loguru import logger


class WeComReceiver:
    """企业微信消息接收器"""

    def __init__(self, corp_id: str, agent_id: str, secret: str):
        self.corp_id = corp_id
        self.agent_id = agent_id
        self.secret = secret
        self.access_token = None

    def get_access_token(self) -> str:
        """获取access_token"""
        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        params = {
            "corpid": self.corp_id,
            "corpsecret": self.secret
        }

        resp = requests.get(url, params=params)
        data = resp.json()

        if data.get("errcode") == 0:
            self.access_token = data["access_token"]
            return self.access_token
        else:
            raise Exception(f"Failed to get token: {data}")

    def receive_messages(self) -> List[Dict[str, Any]]:
        """接收新消息"""
        if not self.access_token:
            self.get_access_token()

        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/get"
        params = {"access_token": self.access_token}

        resp = requests.get(url, params=params)
        data = resp.json()

        messages = []
        for msg in data.get("messages", []):
            messages.append({
                "message_id": msg["msgid"],
                "sender": msg.get("from_user"),
                "content": msg.get("text", {}).get("content", ""),
                "timestamp": msg["time"],
                "chat_id": msg.get("to_user"),
                "message_type": msg.get("msgtype", "text")
            })

        return messages

    def send_message(self, user_id: str, content: str):
        """发送消息（可用于推送交易信号）"""
        if not self.access_token:
            self.get_access_token()

        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send"
        params = {"access_token": self.access_token}

        data = {
            "touser": user_id,
            "msgtype": "text",
            "agentid": self.agent_id,
            "text": {"content": content}
        }

        resp = requests.post(url, params=params, json=data)
        return resp.json()
```

#### 3. 配置并使用

```python
# .env
WECOM_CORP_ID=ww1234567890abcdef
WECOM_AGENT_ID=1000001
WECOM_SECRET=your_secret_here

# 使用
from tools.datasources.wecom_receiver import WeComReceiver
import os

receiver = WeComReceiver(
    corp_id=os.getenv("WECOM_CORP_ID"),
    agent_id=os.getenv("WECOM_AGENT_ID"),
    secret=os.getenv("WECOM_SECRET")
)

# 定时接收消息
while True:
    messages = receiver.receive_messages()

    if messages:
        # 索引到系统
        from memory.enhanced_context import get_enhanced_context_manager
        ctx = get_enhanced_context_manager()
        ctx.index_wechat_messages(messages)

        print(f"接收并索引了 {len(messages)} 条消息")

    time.sleep(60)  # 每分钟检查一次
```

---

## 方案2：个人微信机器人（有风险）

### 优点
✅ 支持个人微信群
✅ 可以接收所有群消息
✅ 实时接收

### 缺点
❌ 可能违反微信ToS
❌ 有封号风险
❌ 不稳定

### 选项A：使用itchat（已停止维护）

```python
# tools/datasources/itchat_receiver.py
"""个人微信机器人（itchat）"""

import itchat
from itchat.content import TEXT, IMAGE, LINK
from memory.enhanced_context import get_enhanced_context_manager


class WeChatBot:
    """个人微信机器人"""

    def __init__(self):
        self.ctx = get_enhanced_context_manager()
        self.monitored_groups = []  # 监控的群聊ID

    def start(self):
        """启动机器人"""

        @itchat.msg_register([TEXT], isGroupChat=True)
        def handle_group_message(msg):
            """处理群消息"""
            # 只处理监控的群
            if msg['FromUserName'] not in self.monitored_groups:
                return

            # 转换为标准格式
            message = {
                "message_id": msg['MsgId'],
                "content": msg['Text'],
                "sender": msg['ActualNickName'],
                "timestamp": msg['CreateTime'],
                "chat_id": msg['FromUserName'],
                "chat_name": itchat.search_chatrooms(userName=msg['FromUserName'])['NickName']
            }

            # 实时索引
            self.ctx.index_wechat_messages([message])
            print(f"接收消息: [{message['sender']}] {message['content'][:50]}")

        # 登录
        itchat.auto_login(hotReload=True)

        # 获取所有群聊
        chatrooms = itchat.get_chatrooms()
        print(f"找到 {len(chatrooms)} 个群聊")

        # 选择要监控的群
        for room in chatrooms:
            if "股票" in room['NickName'] or "交易" in room['NickName']:
                self.monitored_groups.append(room['UserName'])
                print(f"监控群聊: {room['NickName']}")

        # 开始运行
        itchat.run()


# 使用
if __name__ == "__main__":
    bot = WeChatBot()
    bot.start()
```

### 选项B：使用WeChatFerry（更新但复杂）

```bash
# 安装
pip install wcferry

# 需要在Windows PC微信环境下运行
```

---

## 方案3：定时自动导出（推荐）

### 优点
✅ 安全可靠
✅ 不违反微信ToS
✅ 可以控制频率

### 缺点
❌ 需要配置定时任务
❌ 不是真正实时
❌ 需要PC端微信运行

### 实现步骤

#### 1. 安装WeChatMsg工具

```bash
# 下载WeChatMsg
git clone https://github.com/LC044/WeChatMsg.git
cd WeChatMsg
pip install -r requirements.txt
```

#### 2. 创建自动导出脚本

```python
# tools/auto_export_wechat.py
"""自动导出微信消息"""

import subprocess
import time
from pathlib import Path
from datetime import datetime
from loguru import logger


class WeChatAutoExporter:
    """微信自动导出器"""

    def __init__(self,
                 export_dir: str = "data/wechat/auto_exports",
                 wechatmsg_path: str = "/path/to/WeChatMsg"):
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self.wechatmsg_path = Path(wechatmsg_path)

    def export_today_messages(self) -> Path:
        """导出今天的消息"""
        today = datetime.now().strftime("%Y-%m-%d")
        output_file = self.export_dir / f"messages_{today}.json"

        logger.info(f"导出今天的消息到 {output_file}")

        # 调用WeChatMsg导出
        # 这里需要根据WeChatMsg的实际命令调整
        cmd = [
            "python",
            str(self.wechatmsg_path / "main.py"),
            "--export-format", "json",
            "--output", str(output_file),
            "--date", today
        ]

        subprocess.run(cmd, check=True)

        return output_file

    def process_exported_file(self, file_path: Path):
        """处理导出的文件"""
        from agents.wx_source.agent import WxSourceAgent

        logger.info(f"处理文件: {file_path}")

        wx_agent = WxSourceAgent()
        results = wx_agent.run(
            wechat_export_path=str(file_path),
            export_type="json"
        )

        logger.info(f"处理完成: {results['processed_messages']} 条消息")
        return results


# 创建定时任务脚本
def run_auto_export():
    """运行自动导出"""
    exporter = WeChatAutoExporter()

    while True:
        try:
            # 导出今天的消息
            file_path = exporter.export_today_messages()

            # 处理消息
            exporter.process_exported_file(file_path)

            logger.info("等待下次导出...")

            # 每小时导出一次
            time.sleep(3600)

        except Exception as e:
            logger.error(f"自动导出失败: {e}")
            time.sleep(300)  # 失败后5分钟重试


if __name__ == "__main__":
    run_auto_export()
```

#### 3. 配置系统定时任务

**Linux/Mac (crontab)**:
```bash
# 编辑crontab
crontab -e

# 添加任务：每小时运行一次
0 * * * * cd /path/to/chattingclaire && python tools/auto_export_wechat.py
```

**Windows (任务计划程序)**:
```powershell
# 创建任务
$action = New-ScheduledTaskAction -Execute "python" -Argument "tools\auto_export_wechat.py" -WorkingDirectory "C:\path\to\chattingclaire"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)
Register-ScheduledTask -TaskName "WeChatAutoExport" -Action $action -Trigger $trigger
```

---

## 方案4：公众号RSS订阅

### 优点
✅ 完全合规
✅ 简单可靠

### 缺点
❌ 只支持公众号
❌ 不支持群聊
❌ 更新有延迟

### 实现

```python
# tools/datasources/wechat_rss_collector.py
"""微信公众号RSS收集器"""

import feedparser
from typing import List, Dict, Any
from loguru import logger


class WeChatRSSCollector:
    """微信公众号RSS收集器"""

    def __init__(self):
        # 使用第三方RSS服务，如WeRSS
        self.rss_feeds = [
            "https://werss.app/feed/xxx",  # 你订阅的公众号RSS
        ]

    def collect_articles(self) -> List[Dict[str, Any]]:
        """收集公众号文章"""
        articles = []

        for feed_url in self.rss_feeds:
            try:
                feed = feedparser.parse(feed_url)

                for entry in feed.entries:
                    articles.append({
                        "source_id": entry.get("id"),
                        "source": "wechat_mp",
                        "title": entry.get("title"),
                        "content": entry.get("summary"),
                        "url": entry.get("link"),
                        "published_at": entry.get("published"),
                        "author": feed.feed.get("title")
                    })

                logger.info(f"收集了 {len(feed.entries)} 篇文章 from {feed_url}")

            except Exception as e:
                logger.error(f"收集RSS失败 {feed_url}: {e}")

        return articles

    def index_articles(self, articles: List[Dict[str, Any]]):
        """索引文章到系统"""
        from memory.enhanced_context import get_enhanced_context_manager

        ctx = get_enhanced_context_manager()
        indexed = ctx.index_external_items(articles)

        logger.info(f"索引了 {indexed} 篇文章")
        return indexed


# 定时运行
import time

collector = WeChatRSSCollector()

while True:
    articles = collector.collect_articles()
    if articles:
        collector.index_articles(articles)

    time.sleep(3600)  # 每小时检查一次
```

---

## 方案5：混合方案（最实用）

结合多种方法，获得最佳效果：

```python
# tools/auto_collector.py
"""混合自动收集器"""

import asyncio
from datetime import datetime
from loguru import logger


class MixedAutoCollector:
    """混合自动收集器"""

    def __init__(self):
        # 企业微信（如果有）
        self.wecom = None
        if os.getenv("WECOM_CORP_ID"):
            from tools.datasources.wecom_receiver import WeComReceiver
            self.wecom = WeComReceiver(...)

        # 公众号RSS
        from tools.datasources.wechat_rss_collector import WeChatRSSCollector
        self.rss = WeChatRSSCollector()

        # 定时导出
        from tools.auto_export_wechat import WeChatAutoExporter
        self.exporter = WeChatAutoExporter()

        # Context manager
        from memory.enhanced_context import get_enhanced_context_manager
        self.ctx = get_enhanced_context_manager()

    async def run_collection_cycle(self):
        """运行一次收集周期"""
        logger.info("=" * 60)
        logger.info(f"开始收集周期: {datetime.now().isoformat()}")
        logger.info("=" * 60)

        total_messages = 0

        # 1. 收集企业微信消息
        if self.wecom:
            try:
                messages = self.wecom.receive_messages()
                if messages:
                    indexed = self.ctx.index_wechat_messages(messages)
                    total_messages += indexed
                    logger.info(f"✓ 企业微信: {indexed} 条")
            except Exception as e:
                logger.error(f"✗ 企业微信收集失败: {e}")

        # 2. 收集公众号文章
        try:
            articles = self.rss.collect_articles()
            if articles:
                indexed = self.ctx.index_external_items(articles)
                total_messages += indexed
                logger.info(f"✓ 公众号RSS: {indexed} 篇")
        except Exception as e:
            logger.error(f"✗ RSS收集失败: {e}")

        # 3. 导出个人微信（每天一次）
        hour = datetime.now().hour
        if hour == 23:  # 每天23点导出
            try:
                file_path = self.exporter.export_today_messages()
                results = self.exporter.process_exported_file(file_path)
                total_messages += results['processed_messages']
                logger.info(f"✓ 个人微信导出: {results['processed_messages']} 条")
            except Exception as e:
                logger.error(f"✗ 导出失败: {e}")

        logger.info(f"本周期共收集: {total_messages} 条")
        return total_messages

    async def run_forever(self, interval_minutes: int = 30):
        """持续运行"""
        logger.info("混合自动收集器启动")
        logger.info(f"收集间隔: {interval_minutes} 分钟")

        while True:
            try:
                await self.run_collection_cycle()
            except Exception as e:
                logger.error(f"收集周期出错: {e}")

            # 等待下次收集
            await asyncio.sleep(interval_minutes * 60)


# 启动
if __name__ == "__main__":
    collector = MixedAutoCollector()
    asyncio.run(collector.run_forever(interval_minutes=30))
```

---

## 🚀 快速启动

### 最简单的方式（推荐）

1. **配置企业微信** （如果有企业）
2. **订阅公众号RSS**
3. **设置定时导出个人微信**

```bash
# 1. 配置环境变量
echo "WECOM_CORP_ID=your_corp_id" >> .env
echo "WECOM_SECRET=your_secret" >> .env

# 2. 启动混合收集器
python tools/auto_collector.py

# 3. 配置定时任务（可选）
crontab -e
# 添加：0 */2 * * * cd /path/to/chattingclaire && python tools/auto_collector.py
```

---

## ⚙️ 配置文件

```yaml
# config/auto_collection.yaml
auto_collection:
  # 收集间隔（分钟）
  interval_minutes: 30

  # 企业微信
  wecom:
    enabled: true
    corp_id: "${WECOM_CORP_ID}"
    agent_id: "${WECOM_AGENT_ID}"
    secret: "${WECOM_SECRET}"

  # 公众号RSS
  rss:
    enabled: true
    feeds:
      - "https://werss.app/feed/your_subscription_1"
      - "https://werss.app/feed/your_subscription_2"
    check_interval: 3600  # 每小时

  # 个人微信导出
  personal_wechat:
    enabled: true
    export_time: "23:00"  # 每天23点导出
    wechatmsg_path: "/path/to/WeChatMsg"

  # 通知设置
  notifications:
    enabled: true
    notify_on_error: true
    notify_on_new_signals: true
```

---

## 📊 监控和日志

```python
# 查看收集统计
from database.supabase_client import get_supabase_client

db = get_supabase_client()

# 今天收集的消息数
from datetime import date
today = date.today().isoformat()

count = db.table("wx_raw_messages")\
    .select("*", count="exact")\
    .gte("created_at", f"{today}T00:00:00")\
    .execute()

print(f"今天收集了 {count.count} 条消息")
```

---

## ⚠️ 注意事项

1. **个人微信机器人风险**：
   - 可能导致封号
   - 建议只用于测试
   - 生产环境使用企业微信

2. **数据安全**：
   - 妥善保管API密钥
   - 定期备份数据
   - 注意敏感信息

3. **合规性**：
   - 遵守微信服务条款
   - 不要用于商业爬虫
   - 尊重用户隐私

4. **稳定性**：
   - 添加错误重试逻辑
   - 监控服务运行状态
   - 设置告警通知

---

## 📚 相关文档

- [手动导入指南](./WECHAT_USAGE.md)
- [快速参考](../WECHAT_QUICKREF.md)
- [系统架构](../README.md)

---

## 🎯 推荐配置

**小型个人使用**：
```
方案3（定时导出） + 方案4（公众号RSS）
安全、可靠、简单
```

**中型团队使用**：
```
方案1（企业微信） + 方案4（公众号RSS）
官方支持、稳定、功能完整
```

**大型机构使用**：
```
方案5（混合方案）
多数据源、高可用、完整监控
```

开始自动化收集吧！🚀
