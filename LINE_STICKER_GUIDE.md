# LINE 贴图 AI 生成器 - 使用指南

## 🎯 项目概述

这是一个专门为 LINE Creators Market 优化的 AI 贴图生成工具，能够生成完全符合 LINE 官方标准的贴图套装，可直接上传到 LINE 贴图商店。

## ✨ 核心功能

### 🛡️ **LINE 合规保证**

- **自动版权检查**: 避免生成侵犯版权的内容
- **规格自动优化**: 自动调整尺寸、格式、透明背景
- **审核标准预检**: 按 LINE 官方审核指南预先筛选
- **AI 标注支持**: 自动标记 AI 生成内容

### 🎨 **专业贴图生成**

- **多风格支持**: kawaii、minimal、chibi、mascot、emoji
- **智能提示词**: 针对 LINE 贴图优化的 AI 提示词
- **质量控制**: 多层次的质量检查和重试机制
- **标准格式**: 完全符合 LINE 要求的文件结构

### 📦 **一键打包上传**

- **标准 ZIP 格式**: 01.png, 02.png, main.png, tab.png
- **元数据管理**: 自动生成创作记录和规格信息
- **大小优化**: 自动压缩确保符合 60MB 限制
- **验证系统**: 多重验证确保 100%兼容

## 🚀 快速开始

### 1. 环境设置

```bash
# 激活虚拟环境
source venv/bin/activate

# 确保所有依赖已安装
pip install -r requirements.txt

# 配置API密钥（复制.env.example为.env并填入）
cp .env.example .env
# 编辑.env文件，填入OPENAI_API_KEY
```

### 2. 运行方式

#### 🎯 **交互式模式（推荐）**

```bash
python line_sticker_generator.py --mode interactive
```

- 逐步引导用户输入需求
- 实时合规性检查
- 个性化定制选项
- 适合首次使用和精确控制

#### 🤖 **自动模式**

```bash
# 基于热词自动生成
python line_sticker_generator.py --mode auto

# 指定热词
python line_sticker_generator.py --mode auto --topics "可爱小猫" "快乐生活"

# 生成多套
python line_sticker_generator.py --mode auto --count 2
```

#### 🧪 **测试模式**

```bash
python line_sticker_generator.py --mode test
```

## 💰 成本估算

### API 调用成本

- **GPT-4 (创意生成)**: ~$0.15 每套
- **DALL-E-3 (图像生成)**:
  - 8 张贴图: ~$0.32
  - 16 张贴图: ~$0.64
  - 24 张贴图: ~$0.96

### 总成本估算

- **8 张套装**: ~$0.47 (约 3.3 元)
- **16 张套装**: ~$0.79 (约 5.5 元)
- **24 张套装**: ~$1.11 (约 7.8 元)

## 📝 使用流程详解

### 交互式模式流程

1. **角色设定**

   ```
   🐱 角色名称: 我家的橘猫
   📖 角色描述: 一只爱睡觉的胖橘猫，很温柔
   ```

2. **风格选择**

   ```
   1. kawaii - 可爱萌系
   2. minimal - 简约现代
   3. chibi - Q版萌化
   4. mascot - 吉祥物风
   5. emoji - 表情包风
   ```

3. **数量选择**

   ```
   1. 基础套装 - 8张贴图 (约3.3元)
   2. 标准套装 - 16张贴图 (约6.6元)
   3. 豪华套装 - 24张贴图 (约9.9元)
   ```

4. **短语定制** (可选)

   ```
   💬 可以添加你想要的专属短语
   例如: "早安喵", "我想睡觉", "肚子饿了"
   ```

5. **生成确认**
   ```
   🎯 预览后确认生成
   系统会自动处理所有技术细节
   ```

## 📋 文件结构说明

### 生成的文件

```
output/
├── LINE_角色名_8stickers_20250807_202159.zip  # 最终提交文件
└── line_stickers_角色名_20250807_202159/      # 源文件目录
    ├── 01.png          # 贴图1 (370×320)
    ├── 02.png          # 贴图2
    ├── ...
    ├── 08.png          # 贴图8
    ├── main.png        # 主图 (240×240)
    └── tab.png         # 标签图 (96×74)
```

### ZIP 包内容

```
LINE_角色名_8stickers_时间戳.zip
├── 01.png ~ 08.png     # 按序号命名的贴图
├── main.png            # 主图（商店显示）
├── tab.png             # 标签图（聊天列表显示）
└── metadata.json       # 元数据（创作记录）
```

## 🔧 高级功能

### 自定义配置

#### 风格模板扩展

在 `line_compliance.py` 中添加新风格：

```python
self.style_templates = {
    "your_style": "your style description, visual characteristics",
    # ...
}
```

#### 短语库定制

在 `line_sticker_generator.py` 中修改默认短语：

```python
def _generate_default_phrases(self, count: int) -> List[str]:
    custom_phrases = [
        "你的专属短语1", "你的专属短语2", ...
    ]
    return custom_phrases[:count]
```

### 批量生成

```bash
# 同时生成多个不同风格的套装
for style in kawaii minimal chibi; do
    python line_sticker_generator.py --mode auto --style $style
done
```

## 📊 质量控制

### 自动检查项目

- ✅ 版权合规性（避免侵权角色）
- ✅ 图片规格（尺寸、格式、透明度）
- ✅ 文件大小（单张<1MB，ZIP<60MB）
- ✅ 命名规范（01.png 格式）
- ✅ 必需文件（main.png, tab.png）
- ✅ 内容适宜性（无不当内容）

### 手动优化建议

1. **角色一致性**: 确保所有贴图中角色造型一致
2. **表情清晰**: 表情要在小尺寸下依然清楚可见
3. **色彩和谐**: 使用协调的色彩搭配
4. **实用性**: 选择日常聊天中常用的表达

## 🎯 LINE 上传指南

### 1. 账号准备

- 注册 LINE 账号
- 访问 [LINE Creators Market](https://creator.line.me/)
- 完成创作者注册

### 2. 上传步骤

1. 登录 LINE Creators Market
2. 点击 "New Submission"
3. 选择 "Stickers"
4. 上传生成的 ZIP 文件
5. 填写贴图信息：
   - Title: 贴图套装名称
   - Description: 简短描述
   - Copyright: 你的名字
   - ✅ 选择 "AI was used" （重要！）

### 3. 审核要点

- **AI 标注**: 必须标明使用了 AI
- **原创性**: 确保角色是原创的
- **实用性**: 贴图适合日常对话使用
- **清晰度**: 在手机上清楚可见

## 🔧 故障排除

### 常见问题

#### Q: 提示版权风险怎么办？

A: 修改角色设定，避免使用知名角色名称，创造完全原创的角色。

#### Q: 生成的图片不够清晰？

A: 在角色描述中添加"清晰线条"、"高对比度"等关键词。

#### Q: ZIP 包大小超限？

A: 系统会自动优化，如果仍超限请联系开发者。

#### Q: 上传被拒绝？

A: 检查是否正确标注 AI 使用，确保内容符合 LINE 审核标准。

### 调试模式

```bash
# 查看详细错误信息
python line_sticker_generator.py --mode interactive --verbose

# 仅生成不调用API（测试用）
python line_sticker_generator.py --mode test
```

## 📈 商业建议

### 定价策略

- **个人定制**: ¥39-129/套
- **商业定制**: ¥199-499/套
- **批量服务**: 优惠价格

### 市场定位

- 个人用户（情侣、宠物主、学生）
- 小企业（餐厅、工作室）
- 内容创作者（缺乏技术技能）

### 差异化优势

- 100% LINE 合规保证
- 一键式完整流程
- 专业质量控制
- 技术门槛低

## 🔄 更新计划

### 近期功能

- [ ] 动态贴图支持 (APNG)
- [ ] 弹出特效贴图
- [ ] 批量风格生成
- [ ] 用户界面优化

### 长期规划

- [ ] 语音贴图支持
- [ ] 主题套装生成
- [ ] 自动上架工具
- [ ] 收益统计分析

## 📞 支持与联系

如有问题或建议，请：

1. 查看本文档的故障排除部分
2. 运行测试模式检查系统状态
3. 查看生成的日志文件
4. 提交详细的错误报告

---

## 🎉 开始你的 LINE 贴图创作之旅吧！

现在你已经拥有了一个完整的、专业的 LINE 贴图生成系统。无论是为自己创作个性化贴图，还是提供商业定制服务，这个工具都能帮你轻松实现目标！

**立即开始：**

```bash
python line_sticker_generator.py --mode interactive
```
