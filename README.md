# Bob Gemini 翻译插件

这是一个用于 [Bob](https://bobtranslate.com/) 的谷歌 Gemini AI 翻译插件，支持流式翻译。

## 功能特点

- 使用谷歌最新的 Gemini 大语言模型进行高质量翻译
- 支持流式翻译（实时展示翻译结果）
- 支持多种语言之间的互译
- 可自定义模型参数如 temperature 和 top_p

## 安装方法

1. 下载最新的插件版本 [bob-plugin-gemini-translate.bobplugin](https://github.com/coulsontl/bob-plugin-gemini-translate/releases)
2. 安装 Bob (至少 1.8.0 版本)
3. 双击下载的 `.bobplugin` 文件安装插件

## 配置说明

首次使用前，需要进行以下配置：

1. 获取 Gemini API Key：
   - 访问 [Google AI Studio](https://ai.google.dev/)
   - 注册并创建 API Key

2. 在 Bob 偏好设置中配置插件：
   - API Key: 填入上一步获取的 API Key
   - API Base URL: 默认为 `https://generativelanguage.googleapis.com/v1beta`
   - 模型选择: 可选 Gemini 2.0 Flash 或 Gemini 2.5 Pro
   - Temperature: 设置模型温度参数 (0-1)，默认为0
   - Top P: 设置模型 top_p 参数 (0-1)，默认为0.95

## 使用方法

1. 在 Bob 的偏好设置中启用该插件
2. 使用 Bob 的快捷键调出翻译窗口
3. 输入或选择需要翻译的文本
4. 选择源语言和目标语言
5. 等待翻译结果（支持流式输出）

## 问题排查

如果遇到"插件未返回有效结果"错误，请尝试以下解决方法：

1. 检查 API Key 是否正确
2. 确认网络连接稳定
3. 检查 API 调用限制是否已达上限
4. 尝试更换模型或调整参数
5. 响应格式问题：此插件已优化处理SSE格式(Server-Sent Events)响应
6. 查看Bob日志以获取更详细的错误信息

### 常见错误
- **JSON解析失败**: 可能是由于API返回的数据格式不符合预期。该插件已支持处理常见的Gemini API响应格式，包括普通JSON和SSE格式
- **空响应**: 如果模型没有返回有效内容，尝试降低temperature参数值，推荐使用0

## 支持的模型

- Gemini 2.0 Flash (推荐，响应速度快)
- Gemini 2.5 Pro (更高质量，但可能较慢)
- 其他可兼容模型

## 注意事项

- 该插件需要连接互联网才能使用
- Gemini API 可能有每日使用限制，详情请参考 Google AI Studio 的服务条款
- 如遇到问题，请检查 API Key 是否正确，网络连接是否正常 
