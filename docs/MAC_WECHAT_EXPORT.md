# Mac微信导出指南

Mac电脑导出"180K - 星球讨论群🪙"的完整方案。

---

## 🍎 方法1：WechatExporter（Mac专用，推荐）

### 优点
✅ Mac原生应用
✅ 支持导出图片、语音、视频
✅ 界面友好
✅ 开源免费

### 安装

#### 选项A：直接下载（最简单）

```bash
# 访问GitHub下载最新版本
# https://github.com/BlueMatthew/WechatExporter/releases

# 下载 WechatExporter-Mac.dmg
# 双击安装
```

#### 选项B：用Homebrew安装

```bash
# 安装Homebrew（如果还没有）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装WechatExporter
brew install --cask wechat-exporter
```

### 使用步骤

1. **运行WechatExporter**
   - 打开应用
   - 会自动检测微信数据位置

2. **选择群聊**
   - 左侧列表找到"180K - 星球讨论群🪙"
   - 点击选中

3. **选择导出格式**
   - 格式选择：**TXT** 或 **HTML**
   - 如果需要图片：勾选"导出图片"

4. **导出**
   - 选择保存位置：`~/Downloads/180k_export`
   - 点击"导出"
   - 等待完成

5. **转换格式（如果导出的是HTML）**
   ```bash
   # 我给你创建了转换脚本
   python tools/convert_wechat_html.py ~/Downloads/180k_export/chat.html
   # 会生成 chat.json 文件
   ```

---

## 🍎 方法2：手动复制粘贴（最简单）

### 步骤

#### 1. 在Mac微信复制消息

1. 打开微信Mac客户端
2. 进入"180K - 星球讨论群🪙"
3. 选择要导出的消息：
   - 按住 `Cmd` 键
   - 点击选择多条消息
4. 右键 → "复制"

#### 2. 粘贴并格式化

创建文件 `180k_today.txt`：

```bash
# 创建文件
cat > ~/Desktop/180k_today.txt << 'EOF'
[2025-01-17 10:30:00] 张三: 贵州茅台今天涨停了
[2025-01-17 10:35:00] 李四: 600519目标价2800
[2025-01-17 11:00:00] 王五: 看好白酒板块
EOF

# 然后用文本编辑器打开，粘贴你复制的内容
open -a TextEdit ~/Desktop/180k_today.txt
```

**格式要求**：
```
[YYYY-MM-DD HH:MM:SS] 昵称: 消息内容
```

#### 3. 导入系统

```bash
# 复制到监控目录
cp ~/Desktop/180k_today.txt ~/chattingclaire/data/wechat/auto_exports/
```

---

## 🍎 方法3：使用Python脚本直接读取

如果你的Mac可以访问微信数据库：

### 安装依赖

```bash
cd ~/chattingclaire
pip install pysqlite3 pandas
```

### 创建提取脚本

我已经为你准备了脚本：

```bash
# 运行微信数据库提取器
python tools/extract_wechat_mac.py "180K - 星球讨论群🪙"

# 会自动：
# 1. 读取微信数据库
# 2. 提取指定群的消息
# 3. 导出为JSON
# 4. 保存到 data/wechat/auto_exports/
```

---

## 🍎 方法4：通过iCloud同步（创新方法）

如果你有iPhone：

### 步骤

1. **在iPhone上导出**
   - 打开微信群聊
   - 长按消息 → "多选"
   - 选择要导出的消息
   - 点击分享 → "备忘录"
   - 保存到iCloud备忘录

2. **在Mac上访问**
   - 打开"备忘录"app
   - 找到刚才保存的内容
   - 复制粘贴到文本文件

3. **格式化并导入**
   ```bash
   # 整理格式后导入
   cp formatted_messages.txt ~/chattingclaire/data/wechat/auto_exports/
   ```

---

## 🎯 推荐方案（Mac）

### 日常使用（推荐）

**手动复制粘贴** - 最简单快速

```bash
# 每天晚上
# 1. Mac微信复制今天的讨论
# 2. 粘贴到文本文件
# 3. 简单格式化

cat > 180k_$(date +%Y%m%d).txt << 'EOF'
[2025-01-17 14:30:00] 张三: 消息内容
EOF

# 4. 导入
cp 180k_*.txt ~/chattingclaire/data/wechat/auto_exports/
```

### 批量历史数据

**WechatExporter** - 导出完整历史

```bash
# 1. 安装WechatExporter
brew install --cask wechat-exporter

# 2. 导出群聊（选择TXT或HTML格式）

# 3. 转换并导入
python tools/convert_wechat_export.py ~/Downloads/180k_export
```

---

## 🛠️ 创建Mac专用转换工具

我给你创建了几个Mac专用的辅助脚本：

### 1. HTML转JSON转换器

```bash
# 如果WechatExporter导出的是HTML
python tools/convert_wechat_html.py input.html

# 生成 input.json
```

### 2. 微信数据库直接读取

```bash
# 直接从Mac微信数据库读取
python tools/extract_wechat_mac.py "180K - 星球讨论群🪙" --days 7

# 提取最近7天的消息
```

### 3. 快速格式化工具

```bash
# 粘贴原始内容，自动格式化
python tools/format_wechat_paste.py

# 按提示粘贴内容
# 自动生成格式化的文件
```

---

## 📝 Mac微信数据库位置

如果需要直接访问数据库：

```bash
# 微信数据库位置
~/Library/Containers/com.tencent.xinWeChat/Data/Library/Application\ Support/com.tencent.xinWeChat/2.0b4.0.9/

# 消息数据库
message.db

# 联系人数据库
contact.db
```

**注意**：直接读取数据库需要关闭微信客户端。

---

## 🎬 完整Mac工作流

### 每日快速流程（5分钟）

```bash
# === 早上 ===
# 启动自动收集器（后台运行）
cd ~/chattingclaire
nohup ./start_auto_collector.sh > logs/collector.log 2>&1 &

# === 晚上 ===
# 1. 打开Mac微信
# 2. 进入"180K - 星球讨论群🪙"
# 3. Cmd+A 全选今天的消息
# 4. Cmd+C 复制

# 5. 粘贴并格式化
cat > ~/Desktop/today.txt
# 粘贴 (Cmd+V)
# 简单整理格式：
# [时间] 昵称: 内容

# 6. 保存并导入
mv ~/Desktop/today.txt ~/chattingclaire/data/wechat/auto_exports/180k_$(date +%Y%m%d).txt

# 7. 完成！等几分钟查看结果
```

---

## 🔧 故障排除

### 问题1：WechatExporter找不到微信数据

**解决**：
```bash
# 手动指定微信数据路径
open /Applications/WechatExporter.app
# 在设置中指定：
# ~/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/
```

### 问题2：权限不足

**解决**：
```bash
# 给予完全磁盘访问权限
# 系统偏好设置 → 安全性与隐私 → 完全磁盘访问权限
# 添加：WechatExporter 和 Terminal
```

### 问题3：导出的格式不对

**解决**：
```bash
# 使用转换脚本
python tools/convert_wechat_export.py input.html
# 或
python tools/convert_wechat_export.py input.txt
```

---

## 📚 Mac专用脚本

我为Mac创建了这些辅助脚本：

1. **tools/extract_wechat_mac.py** - 直接读取Mac微信数据库
2. **tools/convert_wechat_html.py** - HTML转JSON
3. **tools/format_wechat_paste.py** - 格式化粘贴内容

使用方法：
```bash
# 查看帮助
python tools/extract_wechat_mac.py --help
```

---

## ✨ Mac最简单方法总结

```bash
# 1. Mac微信 → 选择消息 → Cmd+C 复制

# 2. 粘贴到文件
cat > 180k_today.txt
# 粘贴并简单整理格式

# 3. 导入
cp 180k_today.txt ~/chattingclaire/data/wechat/auto_exports/

# 完成！
```

**不需要安装任何工具，只要会复制粘贴就行！**

---

## 🎯 推荐给Mac用户

| 方法 | 难度 | 速度 | 数据量 | 推荐度 |
|-----|------|------|--------|--------|
| 手动复制 | ⭐ | 快 | 少量 | ⭐⭐⭐⭐⭐ 最推荐 |
| WechatExporter | ⭐⭐ | 中 | 大量 | ⭐⭐⭐⭐ |
| 直接读数据库 | ⭐⭐⭐ | 快 | 大量 | ⭐⭐⭐ |
| iCloud同步 | ⭐⭐ | 慢 | 少量 | ⭐⭐ |

**Mac用户最佳选择**：手动复制粘贴！

开始使用吧！🚀
