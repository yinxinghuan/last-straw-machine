# 《Today's Last Straw》技术文档

## 1. 技术栈

- TypeScript 5 + Vite 5，`base: './'`，构建输出 `dist/`。
- Matter.js 0.20 负责头像筹码、静态钉、边墙和结果分隔板的真实碰撞。
- Canvas 2D 只绘制钉阵和分隔线；头像筹码、吊槽、HUD、警报与结果层使用 DOM/CSS。
- 三个结果视频均由 Aigram 首尾帧视频接口生成，显式使用 `video_time: 10`，H.264/AAC、768×1024、时长 10.041667 秒。
- Web Audio API 合成投放、碰钉、警报和反转音，不依赖额外音频文件。

## 2. 目录结构

- `src/main.ts`：身份加载、i18n、Matter 世界、主循环、结果映射、视频演出和 QA 调试口。
- `src/style.css`：事故预测机器的完整视觉系统、响应式布局和状态动效。
- `src/reveal.css`：末拍后才允许结语与重试按钮出现的揭晓时序。
- `public/aigram-bridge.js`：平台资料接口桥接；通过正式用户资料接口读取 `name / head_url`。
- `public/generated/`：三个分支的首帧、末帧与 10 秒 MP4。
- `_production/`：图片/视频生成脚本、请求 manifest、正式海报和明确被拒的失败素材。
- `_qa/`：双尺寸真实下落、三个结果视频、末拍时序与 external guest 自动验证。

## 3. 核心模块

### 状态与主循环

状态为 `loading → ready → dropping → alarm → result`。`requestAnimationFrame` 每帧推进 Matter 引擎并把刚体位置同步到 DOM 头像筹码；高频位置不进入框架状态更新。

### 身份与回退

调试覆盖顺序为 `?avatar_url / ?user_name`；平台内通过 `/note/telegram/user/get/info/by/telegram_id` 读取当前玩家；头像为空使用 `public/default-avatar.png`，平台外用户名为 `AlterU`。头像是真正参与碰撞和决定落袋的筹码，不是角落装饰。

### 命运判定

舞台根据实时尺寸重建 5–6 行错位钉。筹码进入底部阈值后按 `x` 三等分映射 `boss / reply / coffee`，冻结刚体并播放 900ms 警报。`?outcome=` 只用于确定性 QA，不改变正常入口的物理判定。

### 结果影像

三个分支各有独立首帧、末帧和 MP4。结果层先播放完整视频，不显示反转结语；只有 `ended` 事件后添加 `.resolved`，结语与 `DROP AGAIN` 才进入。媒体错误时显示本分支末帧，绝不借用其他分支影像。

### 适配与输入

所有普通 DOM 内部响应式适配，390×844 与 320×568 都不做整页缩放。高度低于 700px 时隐藏眉题并压缩机器间距；触控目标至少 44px。投放使用 `pointerdown`，键盘支持 Space/Enter，iOS 长按防护位于 `index.html`。

## 4. 扩展点

- 改 Plinko 手感：调整 `src/main.ts` 的筹码半径、恢复系数、重力、行数和钉布局。
- 增加命运结果：扩展 `Fate`、底部 gate、`media` 映射和对应 i18n；新结果必须有独立首尾帧与视频。
- 换演员或题材：修改 `_production/generate_*` 的演员锚点与三拍提示词，重新生成并复验中央 70% 安全区。
- 改揭晓节奏：调整 alarm 的 900ms 与 `src/reveal.css`，但不得在视频结束前泄露反转结语。
- 加后台统计：使用 meta 中永久 UUID 接入 session-scoped 事件；不得阻塞第一层投放反馈。
