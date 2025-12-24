# Flash Models 整合与机器人场景配置设计文档

## 1. 项目概述

本项目旨在整合 `common.py` 和 `class_def.py` 两个文件，并实现一个机器人场景系统和 RobotFrame 定义。场景系统用于定义多个机器人之间的相对变换关系，RobotFrame 用于存储变换后的信息（如轨迹、机器人状态等）。

## 2. 当前问题分析

### 2.1 文件结构问题
- **common.py**: 包含 FreeCAD 路径配置和基础模型类（EdgeInfo, SeamInfo）
- **class_def.py**: 包含大量服务模型，但错误地从 `freecad` 模块导入 EdgeInfo 和 SeamInfo
- **依赖关系混乱**: class_def.py 应该从 common.py 导入，但实际导入路径不正确

### 2.2 代码组织问题
- 所有模型类都在一个文件中，缺乏模块化
- 没有明确的分类和组织结构
- 机器人相关配置分散在各个 Setting 类中

## 3. 整合方案

### 3.1 文件结构重组

```
flash-models/
├── __init__.py              # 统一导出接口
├── config.py                # 配置管理（FreeCAD路径等，按需从common.py提取）
├── types.py                 # 类型别名定义（从class_def.py提取）
├── base.py                  # 基础模型类（EdgeInfo, SeamInfo等，从common.py提取）
├── geometry.py              # 几何处理相关模型（从class_def.py按需提取）
├── perception.py            # 感知服务相关模型（从class_def.py按需提取）
├── robot.py                 # 机器人相关模型（从class_def.py按需提取）
├── scene.py                 # 机器人场景系统（新增核心模块）
└── frame.py                 # RobotFrame定义（新增核心模块）
```

### 3.2 模块划分

#### 3.2.1 config.py
- 配置管理
- 全局配置常量

#### 3.2.2 types.py
- tensor1f, tensor2f, tensor3f, tensor4f 类型别名
- 通用类型定义

#### 3.2.3 base.py
- EdgeInfo
- SeamInfo
- StpInfo
- 其他基础数据模型

#### 3.2.4 geometry.py
- STP 文件处理相关模型
- 网格处理相关模型
- 平面相交相关模型
- 点云处理相关模型

#### 3.2.5 perception.py
- 图像处理相关模型
- RGBD 相关模型
- 感知服务请求/响应

#### 3.2.6 robot.py
- 工具规划相关模型
- 6自由度机械臂相关模型
- 参数化运动相关模型

#### 3.2.7 scene.py（新增核心模块）
- 机器人场景系统
- 机器人之间的相对变换关系定义
- 坐标系变换管理

#### 3.2.8 frame.py（新增核心模块）
- RobotFrame定义
- 序列号管理
- 变换后的信息存储（轨迹、状态等）

## 4. 系统架构

### 4.1 整体架构

本系统采用分层架构设计，核心包含两个主要部分：

```
┌─────────────────────────────────────────────────────────┐
│                    Flash Models                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│              ┌──────────────────────┐                   │
│              │     DataBag          │                   │
│              │  (数据包容器)        │                   │
│              ├──────────────────────┤                   │
│              │ • scene: RobotScene │                   │
│              │ • frames: FrameSeq   │                   │
│              └──────────┬───────────┘                   │
│                         │                                │
│        ┌────────────────┴────────────────┐             │
│        │                                  │             │
│  ┌─────▼──────┐                  ┌───────▼──────┐      │
│  │ Scene 系统 │                  │ Frames 系统  │      │
│  │(场景配置)  │                  │(帧数据管理)  │      │
│  ├────────────┤                  ├───────────────┤      │
│  │• RobotScene│                  │• RobotFrame   │      │
│  │• RobotInfo │                  │• RobotState   │      │
│  │• ObjectInfo│                  │• Trajectory    │      │
│  │• Transform │                  │• FrameSequence│      │
│  │• Transform │                  │                │      │
│  │  OnFrame   │                  │                │      │
│  └────────────┘                  └────────────────┘      │
│        │                                  │             │
│        └──────────┬───────────────────────┘             │
│                   │                                     │
│          ┌────────▼────────┐                           │
│          │   基础模型层     │                           │
│          │ • EdgeInfo      │                           │
│          │ • SeamInfo      │                           │
│          │ • StpInfo       │                           │
│          │ • Types         │                           │
│          └─────────────────┘                           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**架构说明**：

1. **DataBag（数据包层）**
   - 顶层容器，组合场景和帧数据
   - 提供统一的数据包管理接口
   - 确保场景和帧数据的一致性
   - 支持数据包的序列化和传输

2. **Scene 系统（场景层）**
   - 负责定义机器人场景的静态配置
   - 管理机器人、物件及其相对变换关系
   - 提供坐标系变换查询功能
   - 场景配置是相对静态的，定义工作空间布局

3. **Frames 系统（帧数据层）**
   - 负责存储动态的帧数据
   - 包含机器人状态、轨迹等时序信息
   - 通过 `scene_id` 关联到特定场景
   - 支持序列化管理，便于追踪和回放

4. **基础模型层**
   - 提供通用的数据模型
   - 类型别名定义
   - 几何信息模型

### 4.2 数据流

```
场景定义 (Scene)
    ↓
创建场景配置 (RobotScene)
    ↓
添加机器人/物件 (RobotInfo/ObjectInfo)
    ↓
创建数据包 (DataBag)
    ↓
运行时生成帧数据 (RobotFrame)
    ↓
添加到数据包 (databag.add_frame)
    ↓
组织成序列 (RobotFrameSequence)
    ↓
完整数据包 (DataBag with Scene + Frames)
```

### 4.3 核心设计：场景系统和 RobotFrame

#### 4.3.1 设计理念

**场景系统**：定义多个机器人之间的相对变换关系，建立坐标系变换树。
- 每个机器人都有一个唯一的标识符
- 每个机器人可以相对于另一个机器人（或世界坐标系）定义变换
- 支持变换链的查询和计算

**RobotFrame**：存储经过变换后的信息
- 包含序列号（seq）用于排序和追踪
- 包含变换后的各种信息：轨迹、机器人状态、时间戳等
- 支持多机器人场景下的数据组织

### 4.4 场景系统设计

#### 4.4.1 Transform（变换定义）

```python
class Transform(BaseModel):
    """变换定义"""
    translation: tensor1f = [0.0, 0.0, 0.0]  # 平移 [x, y, z]
    rotation: tensor2f = []  # 旋转矩阵 3x3 或 4x4 齐次变换矩阵
    
    def to_matrix(self) -> tensor2f:
        """转换为4x4齐次变换矩阵"""
        # 实现转换逻辑，将translation和rotation组合成4x4齐次变换矩阵
        pass
    
    def to_quaternion(self) -> tensor1f:
        """转换为四元数 [x, y, z, w]"""
        # 从rotation矩阵转换为四元数
        pass
    
    def to_euler(self) -> tensor1f:
        """转换为欧拉角 [roll, pitch, yaw]"""
        # 从rotation矩阵转换为欧拉角
        pass
```

#### 4.4.2 TransformOnFrame（基于坐标系的变换）

```python
class TransformOnFrame(BaseModel):
    """基于坐标系的变换"""
    transform: Transform = Transform()  # 变换
    frame_id: str = "world"  # 坐标系ID
```

#### 4.4.3 BaseObjectInfo（基础物件信息）

```python
class BaseObjectInfo(BaseModel):
    """基础物件信息（抽象基类）"""
    name: str  # 物件唯一标识
    description: str = ""  # 描述
    pose: TransformOnFrame = TransformOnFrame()  # 位姿（包含变换和坐标系）
    frames: dict[str, TransformOnFrame] = {}  # 子坐标系 {frame_name: TransformOnFrame}
    movable: bool = False  # 是否可移动
```

#### 4.4.4 RobotInfo（机器人信息）

```python
class RobotInfo(BaseObjectInfo):
    """机器人信息"""
    robot_type: str = ""  # 机器人型号
```

#### 4.4.5 ObjectInfo（其他物件信息）

```python
class ObjectInfo(BaseObjectInfo):
    """其他物件信息（工件、夹具等）"""
    object_type: str = ""  # 物件类型
```

#### 4.4.6 RobotScene（机器人场景）

```python
class RobotScene(BaseModel):
    """机器人场景配置"""
    scene_id: str = ""  # 场景ID
    scene_name: str = ""  # 场景名称
    world_frame: str = "world"  # 世界坐标系名称
    
    # 机器人列表：每个机器人相对于某个参考系的变换
    robots: dict[str, RobotInfo] = {}  # {robot_name: RobotInfo}
    
    # 其他物件列表（工件、夹具等）
    objects: dict[str, ObjectInfo] = {}  # {object_name: ObjectInfo}
    
    # 元数据
    created_at: str = ""
    updated_at: str = ""
    version: str = "1.0.0"
    
    def get_transform(self, from_name: str, to_name: str) -> tensor2f:
        """获取从from_name到to_name的变换矩阵（通过world坐标系）"""
        # 实现变换链查找和计算：from_name -> world -> to_name
        pass
    
    def add_robot(self, robot: RobotInfo):
        """添加机器人到场景"""
        self.robots[robot.name] = robot
    
    def add_object(self, obj: ObjectInfo):
        """添加物件到场景"""
        self.objects[obj.name] = obj
```

### 4.5 RobotFrame 设计

#### 4.3.1 RobotState（机器人状态）

```python
class RobotState(BaseModel):
    """机器人状态"""
    robot_id: str  # 机器人ID
    joints: tensor1f = []  # 关节角度
    joint_velocities: tensor1f = []  # 关节速度
    joint_accelerations: tensor1f = []  # 关节加速度
    tcp_pose: tensor2f = []  # TCP位姿（4x4变换矩阵）
    tcp_velocity: tensor1f = []  # TCP速度 [vx, vy, vz, wx, wy, wz]
    is_moving: bool = False  # 是否在运动
    error_code: int = 0  # 错误码
    timestamp: float = 0.0  # 时间戳
```

#### 4.3.2 Trajectory（轨迹）

```python
class Trajectory(BaseModel):
    """轨迹信息"""
    robot_id: str  # 机器人ID
    waypoints: list[tensor2f] = []  # 路径点列表（每个是4x4变换矩阵）
    joint_trajectory: list[tensor1f] = []  # 关节空间轨迹
    velocities: list[tensor1f] = []  # 速度列表
    accelerations: list[tensor1f] = []  # 加速度列表
    timestamps: list[float] = []  # 时间戳列表
    frame_id: str = ""  # 坐标系ID
```

#### 4.3.3 RobotFrame（核心类）

```python
class RobotFrame(BaseModel):
    """机器人帧数据，包含变换后的信息"""
    seq: int  # 序列号，用于排序和追踪
    
    # 时间信息
    timestamp: float = 0.0  # 时间戳
    frame_id: str = ""  # 帧ID
    
    # 机器人状态（可选，可以有多个机器人）
    robot_states: dict[str, RobotState] = {}  # {robot_id: RobotState}
    
    # 轨迹信息（可选）
    trajectories: dict[str, Trajectory] = {}  # {robot_id: Trajectory}
    
    # 物件更新（可选，包含变换后的几何、点云、网格等）
    object_updates: dict[str, TransformOnFrame] = {}  # {object_name: TransformOnFrame}
    
    # 自定义数据（可选）
    custom_data: dict[str, Any] = {}  # 自定义数据字典
    
    # 元数据
    scene_id: str = ""  # 关联的场景ID
```

#### 4.5.4 RobotFrameSequence（帧序列）

```python
class RobotFrameSequence(BaseModel):
    """RobotFrame序列，用于存储一系列帧"""
    sequence_id: str = ""  # 序列ID
    scene_id: str = ""  # 关联的场景ID
    frames: list[RobotFrame] = []  # 帧列表
    
    def add_frame(self, frame: RobotFrame):
        """添加帧到序列"""
        # 自动设置seq
        if not frame.seq:
            frame.seq = len(self.frames)
        self.frames.append(frame)
    
    def get_frame_by_seq(self, seq: int) -> RobotFrame | None:
        """根据序列号获取帧"""
        for frame in self.frames:
            if frame.seq == seq:
                return frame
        return None
    
    def get_frames_by_robot(self, robot_id: str) -> list[RobotFrame]:
        """获取包含指定机器人的所有帧"""
        return [f for f in self.frames if robot_id in f.robot_states]
```

## 5. 机器人场景配置设计（简化版，保留作为参考）

### 5.1 场景配置需求（保留作为参考，实际使用场景系统）

## 6. 实施计划

### 6.1 第一阶段：核心模块实现
1. 创建 `types.py` - 类型别名
2. 创建 `base.py` - 基础模型（从common.py按需提取）
3. 创建 `scene.py` - 场景系统实现
4. 创建 `frame.py` - RobotFrame实现

### 6.2 第二阶段：现有代码整合
1. 从 `class_def.py` 按需提取需要的模型到对应模块
2. 修复导入关系
3. 保持向后兼容（通过 `__init__.py` 导出）

### 6.3 第三阶段：文档和示例
1. 更新 README
2. 编写场景和 RobotFrame 使用示例
3. 编写 API 文档

## 7. 向后兼容性

为了保持向后兼容性：

1. 在 `__init__.py` 中导出所有原有类
2. 保持原有的导入路径可用
3. 添加废弃警告（如需要）

## 8. 示例用法

### 8.1 创建场景

```python
from data_model import RobotScene, RobotInfo, ObjectInfo, Transform, TransformOnFrame

# 创建场景
scene = RobotScene(
    scene_id="scene_001",
    scene_name="双机器人焊接场景",
    world_frame="world"
)

# 添加第一个机器人（相对于世界坐标系）
robot1 = RobotInfo(
    name="robot_1",
    robot_type="abb_irb6700_150_320",
    pose=TransformOnFrame(
        transform=Transform(
            translation=[0, 0, 0],
            rotation=[[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]]
        ),
        frame_id="world"
    ),
    movable=True
)
# 添加机器人的子坐标系（如TCP坐标系）
robot1.frames["tcp"] = TransformOnFrame(
    transform=Transform(translation=[0, 0, 100]),
    frame_id="robot_1"
)
scene.add_robot(robot1)

# 添加第二个机器人（相对于世界坐标系）
robot2 = RobotInfo(
    name="robot_2",
    robot_type="abb_irb6700_150_320",
    pose=TransformOnFrame(
        transform=Transform(
            translation=[2000, 0, 0],  # 在世界坐标系的X方向2米处
            rotation=[[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]]
        ),
        frame_id="world"
    ),
    movable=True
)
scene.add_robot(robot2)

# 添加工件（相对于世界坐标系）
workpiece = ObjectInfo(
    name="workpiece_001",
    object_type="welding_part",
    pose=TransformOnFrame(
        transform=Transform(
            translation=[1000, 0, 500],
            rotation=[[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]]
        ),
        frame_id="world"
    ),
    movable=False,
    description="待焊接工件"
)
scene.add_object(workpiece)

# 查询变换（通过world坐标系）
transform_matrix = scene.get_transform("robot_1", "robot_2")
```

### 8.2 创建和使用 RobotFrame

```python
from data_model import RobotFrame, RobotState, Trajectory

# 创建RobotFrame
frame = RobotFrame(
    seq=1,
    timestamp=1234567890.0,
    frame_id="frame_001",
    scene_id="scene_001"
)

# 添加机器人状态
robot_state = RobotState(
    robot_id="robot_1",
    joints=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
    tcp_pose=[[1,0,0,100], [0,1,0,200], [0,0,1,300], [0,0,0,1]],
    timestamp=1234567890.0
)
frame.robot_states["robot_1"] = robot_state

# 添加轨迹信息
trajectory = Trajectory(
    robot_id="robot_1",
    waypoints=[
        [[1,0,0,100], [0,1,0,200], [0,0,1,300], [0,0,0,1]],
        [[1,0,0,150], [0,1,0,250], [0,0,1,350], [0,0,0,1]]
    ],
    timestamps=[1234567890.0, 1234567900.0],
    frame_id="world"
)
frame.trajectories["robot_1"] = trajectory

# 添加物件更新（变换后的几何、点云、网格等）
frame.object_updates["workpiece_001"] = TransformOnFrame(
    transform=Transform(
        translation=[1000, 0, 500],
        rotation=[[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]]
    ),
    frame_id="world"
)
```

### 8.3 创建 RobotFrameSequence

```python
from data_model import RobotFrameSequence

# 创建帧序列
sequence = RobotFrameSequence(
    sequence_id="seq_001",
    scene_id="scene_001"
)

# 添加多个帧
for i in range(10):
    frame = RobotFrame(
        seq=i,
        timestamp=1234567890.0 + i * 0.1,
        scene_id="scene_001"
    )
    sequence.add_frame(frame)

# 查询帧
frame_5 = sequence.get_frame_by_seq(5)
robot1_frames = sequence.get_frames_by_robot("robot_1")
```

### 8.4 查询变换

```python
# 直接使用场景的方法查询变换
transform_matrix = scene.get_transform("robot_1", "robot_2")
print(f"从robot_1到robot_2的变换矩阵: {transform_matrix}")

# 查询到世界坐标系的变换
world_transform = scene.get_transform("robot_1", "world")
```

## 9. 总结

本设计文档提出了一个清晰的整合方案，核心是 **DataBag**、**场景系统**和 **RobotFrame** 定义。

**DataBag（数据包）**：
- 顶层容器，组合场景和帧数据
- 提供统一的数据包管理接口
- 确保场景和帧数据的一致性
- 便于数据包的序列化、传输和存储

**场景系统（Scene）**：
- 定义多个机器人之间的相对变换关系
- 支持变换链的查询和计算
- 建立清晰的坐标系变换树
- 管理静态的场景配置

**RobotFrame 系统（Frames）**：
- 包含序列号（seq）用于排序和追踪
- 存储变换后的各种信息：轨迹、机器人状态、几何信息等
- 支持多机器人场景下的数据组织
- 通过 `scene_id` 关联到特定场景

**架构优势**：
- 清晰的职责分离：DataBag 负责组合，场景负责静态配置，帧负责动态数据
- 灵活的扩展性：可以轻松添加新的场景或帧类型
- 统一的数据模型：为多机器人应用提供了标准化的接口
- 完整的数据包：DataBag 将场景和帧数据组合在一起，便于整体管理

通过模块化设计，按需从现有文件中提取需要的代码，提高了代码的可维护性和可扩展性。DataBag、场景和 RobotFrame 系统为多机器人应用提供了统一的数据模型和配置管理接口。

