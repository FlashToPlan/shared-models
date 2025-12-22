# Shared Models

定义所有后端-前端数据模型，提供统一的机器人场景配置和帧数据管理。

## 文件结构

```
shared-models/
├── __init__.py          # 项目根导出接口
├── data_model/          # 数据模型模块
│   ├── __init__.py      # 模块导出接口
│   ├── types.py         # 类型别名定义
│   ├── config.py        # 配置管理
│   ├── base.py          # 基础模型类（EdgeInfo, SeamInfo, StpInfo）
│   ├── scene.py         # 机器人场景系统（核心模块）
│   └── frame.py         # RobotFrame系统（核心模块）
├── example.py           # 使用示例
└── DESIGN.md            # 设计文档
```

## 核心模块

### 场景系统 (`scene.py`)

用于定义多个机器人之间的相对变换关系：

- `Transform`: 变换定义（平移+旋转）
- `TransformOnFrame`: 基于坐标系的变换
- `BaseObjectInfo`: 基础物件信息（抽象基类）
- `RobotInfo`: 机器人信息
- `ObjectInfo`: 其他物件信息（工件、夹具等）
- `RobotScene`: 机器人场景配置

### RobotFrame 系统 (`frame.py`)

用于存储变换后的信息：

- `RobotState`: 机器人状态
- `Trajectory`: 轨迹信息
- `RobotFrame`: 机器人帧数据（包含seq序列号）
- `RobotFrameSequence`: 帧序列管理

## 快速开始

```python
from data_model import (
    RobotScene,
    RobotInfo,
    Transform,
    TransformOnFrame,
    RobotFrame,
)

# 创建场景
scene = RobotScene(
    scene_id="scene_001",
    scene_name="双机器人焊接场景",
    world_frame="world"
)

# 添加机器人
robot = RobotInfo(
    name="robot_1",
    robot_type="abb_irb6700_150_320",
    pose=TransformOnFrame(
        transform=Transform(translation=[0, 0, 0]),
        frame_id="world"
    )
)
scene.add_robot(robot)

# 创建RobotFrame
frame = RobotFrame(
    seq=1,
    timestamp=1234567890.0,
    scene_id="scene_001"
)
```

## 详细示例

查看 `example.py` 文件获取完整的使用示例。

## 设计文档

详细的设计说明请参考 `DESIGN.md`。
