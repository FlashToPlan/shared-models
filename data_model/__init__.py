"""Shared Models - 统一导出接口"""

# 基础模型
from .base import EdgeInfo, SeamInfo, StpInfo

# 场景系统
from .scene import (
    BaseObjectInfo,
    ObjectInfo,
    RobotInfo,
    RobotScene,
    Transform,
    TransformOnFrame,
)

# RobotFrame系统
from .frame import (
    ObjectAction,
    RobotFrame,
    RobotFrameSequence,
    RobotState,
    Trajectory,
)

# DataBag系统
from .databag import DataBag

# 类型别名
from .types import tensor1f, tensor2f, tensor3f, tensor4f

__all__ = [
    # 类型别名
    "tensor1f",
    "tensor2f",
    "tensor3f",
    "tensor4f",
    # 基础模型
    "EdgeInfo",
    "SeamInfo",
    "StpInfo",
    # 场景系统
    "Transform",
    "TransformOnFrame",
    "BaseObjectInfo",
    "RobotInfo",
    "ObjectInfo",
    "RobotScene",
    # RobotFrame系统
    "RobotState",
    "Trajectory",
    "ObjectAction",
    "RobotFrame",
    "RobotFrameSequence",
    # DataBag系统
    "DataBag",
]
