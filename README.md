# LINE 贴图 AI 定制平台

🎨 **专业级 LINE 贴图定制服务** - 100% 符合 LINE Creators Market 标准，支持个人定制和商业服务。

## 🌟 **全新 LINE 贴图定制模式** 

### 🎯 **交互式贴图定制**
```bash
python line_sticker_generator.py --mode interactive
```
- **个性化设计** - 自定义角色、风格、短语
- **实时合规检查** - 自动避免版权风险
- **多种风格** - kawaii、minimal、chibi、mascot、emoji
- **透明定价** - 8张(¥3.3) / 16张(¥5.5) / 24张(¥7.8)

### 🤖 **智能批量生成**  
```bash
python line_sticker_generator.py --mode auto
```
- **基于热词** - 自动获取流行话题生成
- **批量处理** - 一次生成多套不同风格
- **质量保证** - AI优化提示词 + 多重验证

## ✨ 核心功能

### 🛡️ **LINE 兼容保证**
- **版权安全** - 自动检测并避免侵权内容
- **规格标准** - 完全符合 LINE 官方要求 (370×320, 240×240, 96×74)
- **格式优化** - PNG 透明背景，文件大小控制
- **AI 标注** - 自动标记 AI 生成内容

### 🎨 **专业图像生成**
- **智能提示词** - 针对 LINE 贴图优化的 AI 提示
- **多重重试** - 失败自动重试，质量保障机制
- **风格一致** - 同套贴图保持角色和风格统一
- **表情丰富** - 根据短语智能匹配表情动作

### 📦 **一键打包上传**
- **标准命名** - 01.png ~ 24.png + main.png + tab.png
- **ZIP 验证** - 多重检查确保 100% 兼容
- **元数据管理** - 自动记录创作信息和参数
- **直接上传** - 可直接提交到 LINE Creators Market

## 💰 **成本控制**

| 套装类型 | 贴图数量 | GPT-4成本 | DALL-E成本 | 总成本 | 人民币 |
|---------|---------|-----------|-----------|--------|--------|
| 基础版 | 8张 | $0.15 | $0.32 | $0.47 | ¥3.3 |
| 标准版 | 16张 | $0.15 | $0.64 | $0.79 | ¥5.5 |
| 豪华版 | 24张 | $0.15 | $0.96 | $1.11 | ¥7.8 |

## 🚀 **商业应用**

### 个人定制服务
- **情侣贴图** - 专属情侣角色和昵称
- **宠物贴图** - 根据宠物照片定制
- **家庭贴图** - 家庭成员卡通化

### 企业级应用  
- **品牌吉祥物** - 企业形象贴图化
- **员工福利** - 公司专属表情包
- **活动推广** - 节日/活动主题贴图

---

## 🔧 传统功能 (自动化生成)

- **🔥 热词抓取** - 自动获取 Google Trends、Twitter、LINE NEWS 热门话题
- **🤖 AI 创意** - 使用 GPT-4 生成原创角色和短语  
- **⏰ 定时任务** - GitHub Actions 每天自动生成
- **🌐 Web 预览** - 本地 Flask 界面预览和下载
- **📢 智能通知** - LINE Messaging API、Discord、Telegram、邮件多种通知方式

## 📋 系统要求

- Python 3.9+
- OpenAI API Key
- Twitter API Bearer Token (可选)
- LINE Messaging API 配置 (推荐) 或其他通知方式

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/FutureXR1995/sticker_autogen.git
cd sticker_autogen
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# OpenAI API Key (必需)
OPENAI_API_KEY=sk-your-openai-api-key

# Twitter API Bearer Token (可选)
TWITTER_BEARER_TOKEN=your-twitter-bearer-token

# LINE Messaging API (推荐)
LINE_CHANNEL_ACCESS_TOKEN=your-channel-access-token
LINE_USER_ID=your-user-id

# Discord Webhook URL (可选)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxx

# Telegram Bot Token (可选)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# Telegram Chat ID (可选)
TELEGRAM_CHAT_ID=your-chat-id

# 邮件通知配置 (可选)
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

### 5. 运行测试

```bash
PYTHONPATH=. pytest
```

### 6. 测试生成流程

```bash
# 测试模式（不调用真实 API）
python main.py --dry-run

# 本地预览模式
python main.py --local-preview
```

## 📖 使用方法

### 本地开发

```bash
# 完整流程（包含图像生成）
python main.py

# 仅测试模式
python main.py --dry-run

# 启动 Web 预览
python app.py
# 然后访问 http://localhost:5000
```

### GitHub Actions 部署

1. **Fork 项目**到你的 GitHub 账户

2. **配置 Secrets**：

   - 进入仓库 Settings → Secrets and variables → Actions
   - 添加以下 secrets：
     - `OPENAI_API_KEY`
     - `TWITTER_BEARER_TOKEN` (可选)
     - `LINE_CHANNEL_ACCESS_TOKEN` (推荐)
     - `LINE_USER_ID` (推荐)
     - `DISCORD_WEBHOOK_URL` (可选)
     - `TELEGRAM_BOT_TOKEN` (可选)
     - `TELEGRAM_CHAT_ID` (可选)
     - `EMAIL_USER` (可选)
     - `EMAIL_PASSWORD` (可选)

3. **启用 Actions**：

   - 进入 Actions 页面
   - 手动触发一次工作流测试

4. **定时运行**：
   - 默认每天 00:00 JST 自动运行
   - 可在 `.github/workflows/generate.yml` 中修改时间

## 📁 项目结构

```
sticker_autogen/
├── data_scraper.py          # 热词抓取模块
├── idea_generator.py        # GPT-4 创意生成
├── image_generator.py       # DALL·E 图像生成
├── packager.py              # ZIP 打包模块
├── notifier.py              # 通知模块
├── app.py                   # Flask Web 界面
├── main.py                  # 主流程入口
├── requirements.txt         # Python 依赖
├── .env.example            # 环境变量模板
├── .github/workflows/      # GitHub Actions
│   └── generate.yml
├── tests/                  # 单元测试
│   ├── test_data_scraper.py
│   ├── test_idea_generator.py
│   ├── test_image_generator.py
│   ├── test_packager.py
│   ├── test_notifier.py
│   └── test_app.py
└── templates/              # Flask 模板
    └── index.html
```

## 🔧 配置说明

### API 密钥获取

#### OpenAI API Key

1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 注册账户并创建 API Key
3. 复制 Key 到 `.env` 文件

#### Twitter API Bearer Token (可选)

1. 访问 [Twitter Developer Portal](https://developer.twitter.com/)
2. 创建应用并获取 Bearer Token
3. 复制到 `.env` 文件

#### LINE Messaging API (推荐)

1. **创建 LINE Official Account**：

   - 访问 [LINE Official Account Manager](https://account.line.biz/)
   - 登录并创建新的 Official Account
   - 填写账户信息（名称、描述、头像等）

2. **启用 Messaging API**：

   - 在 Official Account 设置中启用 Messaging API
   - 获取 Channel Access Token
   - 配置 Webhook URL（可选，用于接收消息）

3. **获取 User ID**：

   - 方法 1：通过 LINE Login 获取
   - 方法 2：用户先加你的 Official Account 为好友，然后通过 API 获取

4. **配置环境变量**：
   ```env
   LINE_CHANNEL_ACCESS_TOKEN=your-channel-access-token
   LINE_USER_ID=your-user-id
   ```

**注意**：根据最新规范，需要先创建 LINE Official Account，然后在该账户下启用 Messaging API 功能。

#### Discord Webhook URL (可选)

1. 在 Discord 服务器中创建 Webhook
2. 复制 Webhook URL 到 `.env` 文件

#### Telegram Bot Token (可选)

1. 通过 [@BotFather](https://t.me/botfather) 创建 Bot
2. 获取 Bot Token 和 Chat ID
3. 复制到 `.env` 文件

### 自定义配置

- **生成数量**：修改 `main.py` 中的 `pick_two()` 函数
- **定时时间**：修改 `.github/workflows/generate.yml` 中的 cron 表达式
- **图像风格**：修改 `idea_generator.py` 中的 prompt 模板

## 🧪 测试

运行所有测试：

```bash
PYTHONPATH=. pytest
```

运行特定模块测试：

```bash
PYTHONPATH=. pytest tests/test_data_scraper.py
```

## 📊 输出文件

生成的贴图文件保存在 `output/` 目录：

```
output/
├── set_1/           # 第一套贴图
│   ├── 01.png
│   ├── 02.png
│   ├── main.png
│   └── tab.png
├── set_2/           # 第二套贴图
│   ├── 01.png
│   ├── 02.png
│   ├── main.png
│   └── tab.png
└── *.zip            # 打包后的 ZIP 文件
```

## 🐛 常见问题

### Q: OpenAI API 报错 "content_policy_violation"

A: 修改 `idea_generator.py` 中的 prompt，避免侵权或不当内容

### Q: 生成的 PNG 文件过大

A: 检查 `image_generator.py` 中的尺寸设置，确保 ≤ 370×320

### Q: GitHub Actions 超时

A: 减少生成数量或分步缓存输出

### Q: 日文字体显示异常

A: 下载 NotoSansCJK JP 字体到 `assets/fonts/` 目录

### Q: LINE Messaging API 配置问题

A: 确保 Channel Access Token 和 User ID 正确配置

### Q: 通知不工作

A: 检查 LINE Messaging API、Discord Webhook 或 Telegram Bot Token 配置

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- OpenAI GPT-4 & DALL·E-3
- LINE Creators Market & Messaging API
- Flask & Bootstrap
- GitHub Actions

---

**注意**：请确保生成的内容符合 LINE Creators Market 的制作规范，避免侵权和不当内容。
