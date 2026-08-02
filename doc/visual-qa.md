# 视觉 QA 记录

## 已验证状态

- 390×844 platform-layout：ready、真实物理下落、boss 视频播放中、boss 末拍、reply 播放中/末拍、coffee 播放中/末拍。
- 320×568 platform-layout：ready、真实物理下落、boss 视频播放中、boss 末拍。
- 390×844 external-guest：生产访客栏高度 54px；顶部标题部分被覆盖，但核心指令、完整机器和投放按钮仍可使用，未据此修改平台内构图。
- 两个尺寸 `scrollWidth === clientWidth` 且 `scrollHeight === clientHeight`；结果按钮高度 48px。
- 三支 MP4 均为 768×1024、10.041667 秒，视频末拍前结语不可见，结束后 240ms 进入。

## 素材门禁

- 第一版海报因右上角中文/假字被拒；第二、三版因装置标签和警告假字被拒；第四版因伪注册符号被拒。
- 正式版通过 Aigram img2img 仅移除伪注册符号，最终只保留 `TODAY'S LAST STRAW`，160×160 下标题、红发主角、下落冲突仍清晰。
- 咖啡分支第一版假发像白色线条，第二版产生重复人物/断肢，均保存到 `_production/rejected/`；第三版改为单一老板滑坐地面并通过关键帧检查。
- 正式海报 SHA-256：`677416efaebc8c2e33c51381df5c80bc7cfc2e980f230d85e4f3d50c6ab72312`。

## 当前判断

该产品已经可以用于验证 E 类“物理悬念→命运命名→10 秒情绪反转”的方法，但仍是第一样本，不足以直接沉淀正式 Skill。
