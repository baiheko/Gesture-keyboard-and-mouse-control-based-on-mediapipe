# GestureControl: 基于手势的电脑控制工具

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Dependencies](https://img.shields.io/badge/Dependencies-MediaPipe%20%7C%20OpenCV%20%7C%20PyAutoGUI-orange)

一个基于 MediaPipe 和 OpenCV 开发的手势控制工具，支持通过手部动作控制鼠标移动、点击/长按，以及键盘方向键/F/J 键操作。内置可视化配置界面，可自定义灵敏度、阈值等参数，适配不同用户的使用习惯。

## 🌟 功能特点

- **鼠标控制**：右手追踪控制鼠标移动，捏指（拇指与食指并拢）触发点击/长按
- **键盘控制**：
  - 模式1：左手控制方向键（食指上下左右指示方向）
  - 模式2：左手捏指触发 F 键，右手捏指触发 J 键（适合游戏/快捷操作）
- **操作优化**：
  - 自适应平滑过滤（快速移动时弱平滑，静止时强平滑）
  - 120Hz 插帧算法，减少鼠标抖动，提升跟手度
- **可视化配置**：内置图形界面，支持调整参数

## 📋 环境要求

- Python 3.8 及以上 3.10 以下版本
- 支持的操作系统：Windows
- 硬件要求：带摄像头的设备

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/baiheko/Gesture-keyboard-and-mouse-control-based-on-mediapipe
cd GestureControl
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

> 注意：
> - Windows 系统若安装 PyAutoGUI 失败，需先安装 `pywin32`：`pip install pywin32`

### 3. 运行程序

```bash
python main.py
```

## 📖 使用说明

### 第一步：参数配置

程序启动后会先打开配置界面，可调整以下核心参数（建议保持默认值，如需调整请参考提示）：

| 配置分类 | 核心参数 | 说明 |
|----------|----------|------|
| 摄像头设置 | 摄像头索引 | 默认为1，画面异常时可尝试0/1/2 |
| 鼠标设置 | 鼠标速度 | 0.1~5.0，数值越大移动越快 |
| 鼠标设置 | 平滑度 | 0.0~1.0，数值越大移动越平滑 |
| 判定设置 | 捏指阈值 | 0.0~0.01，数值越大越容易触发捏指判定 |
| 插帧设置 | 跟手度 | 0.0~1.0，数值越大鼠标越跟手 |

- 点击「恢复默认」可重置为初始配置
- 调整完成后点击「保存」，自动启动摄像头并进入主程序

### 第二步：手势操作指南

| 手部 | 操作 | 功能 |
|------|------|------|
| 右手 | 移动 | 控制鼠标光标移动 |
| 右手 | 拇指+食指并拢（捏指） | 鼠标点击/长按（取决于模式） |
| 左手 | 上下左右摆动 | 方向键控制（模式1） |
| 左手 | 捏指 | 触发 F 键（模式2） |
| 右手 | 捏指 | 触发 J 键（模式2） |

### 第三步：快捷键控制

主程序运行时，可通过键盘快捷键切换模式：

| 快捷键 | 功能 |
|--------|------|
| Q | 启用/关闭手势控制（屏幕左上角显示状态） |
| W | 切换键盘模式（方向键 ↔ F/J 键） |
| E | 切换鼠标操作模式（点击 ↔ 长按） |
| ESC | 退出程序 |

## ⚙️ 核心配置说明

配置文件 `config.py` 包含所有可自定义参数，也可通过可视化界面修改：

```python
class Config:
    camera_index = 1          # 摄像头索引
    mouse_speed = 1.2         # 鼠标灵敏度
    smoothing = 0.7           # 移动平滑度（0~1）
    fist_threshold = 0.0025   # 捏指判定阈值（越小越灵敏）
    direction_threshold = 0.1 # 方向键触发阈值
    interp_hz = 120           # 插帧频率
    follow_gain = 1.0         # 跟手度（0~1）
    fjkeys = True             # 是否启用 F/J 键控制（False 为方向键）
    select_click = False      # 鼠标模式：False=长按，True=点击
    enable_control = False    # 是否启用手势控制（运行时用Q键切换）
```

## ❗ 常见问题

### 1. 摄像头无法打开/画面黑屏
- 检查摄像头索引是否正确（尝试切换0/1/2）
- 确保摄像头未被其他程序占用
- 验证依赖安装：`pip install opencv-python mediapipe`

### 2. 手势识别不灵敏
- 增大「捏指阈值」参数
- 确保光线充足，手部无遮挡
- 调整摄像头角度，让手部完全进入画面

### 3. 鼠标移动卡顿/抖动
- 碍于摄像头，CPU等硬件限制，属于正常现象
  
### 4. 键盘/鼠标无响应
- 检查是否已按 Q 键启用手势控制（屏幕显示 Control: ON）
- 确认手部左右识别正确（程序会区分左右手功能）

## 🛠️ 项目结构

```
GestureControl/
├── config.py          # 主配置文件
├── config_saved.py    # 默认配置备份
├── controller.py      # 手势控制核心逻辑（鼠标/键盘操作）
├── filters.py         # 平滑过滤算法（低通滤波/自适应滤波）
├── hand_tracker.py    # 手部追踪（基于MediaPipe）
├── main.py            # 主程序入口
├── UIcontrol.py       # 可视化配置界面
└── requirements.txt   # 依赖列表
```

## 🙏 致谢

- [MediaPipe](https://mediapipe.dev/)：谷歌开源的手部追踪库
- [OpenCV](https://opencv.org/)：计算机视觉处理库
- [PyAutoGUI](https://pyautogui.readthedocs.io/)：跨平台键鼠控制库

如果觉得项目有用，欢迎点亮 ⭐️ 支持一下！
