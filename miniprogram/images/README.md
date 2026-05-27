# 图片资源目录

请在此目录下添加以下图片文件:

## 必需图片

### TabBar图标 (24x24px, PNG格式)
- `home.png` - 首页未选中图标
- `home-active.png` - 首页选中图标
- `assistant.png` - 助手列表未选中图标
- `assistant-active.png` - 助手列表选中图标

### 助手头像 (100x100px, PNG格式)
- `medical.png` - 医疗咨询专家
- `legal.png` - 法律顾问
- `tech.png` - 技术专家
- `education.png` - 教育顾问
- `life.png` - 生活顾问
- `finance.png` - 理财顾问

## 图片建议

可以使用以下方式获取图标:

1. **使用在线图标库**:
   - [Iconfont](https://www.iconfont.cn/)
   - [Flaticon](https://www.flaticon.com/)
   - [Icons8](https://icons8.com/)

2. **使用AI生成**:
   - 使用AI绘图工具生成简单的头像图标

3. **使用Emoji代替**:
   - 在开发阶段,可以使用emoji作为临时头像

## 替代方案

如果不想添加图片,可以修改代码使用emoji或纯色背景代替:

```javascript
// 在app.js中修改助手配置
{
  id: 'medical',
  name: '医疗咨询专家',
  avatar: '', // 留空
  emoji: '🏥', // 使用emoji
  description: '提供医疗健康咨询和建议'
}
```
