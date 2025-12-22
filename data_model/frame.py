"""RobotFrame系统"""

from pydantic import BaseModel
from typing import Any

from .types import tensor1f, tensor2f
from .scene import TransformOnFrame


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


class Trajectory(BaseModel):
    """轨迹信息"""

    robot_id: str  # 机器人ID
    waypoints: list[tensor2f] = []  # 路径点列表（每个是4x4变换矩阵）
    joint_trajectory: list[tensor1f] = []  # 关节空间轨迹
    velocities: list[tensor1f] = []  # 速度列表
    accelerations: list[tensor1f] = []  # 加速度列表
    timestamps: list[float] = []  # 时间戳列表
    frame_id: str = ""  # 坐标系ID


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


class RobotFrameSequence(BaseModel):
    """RobotFrame序列，用于存储一系列帧"""

    sequence_id: str = ""  # 序列ID
    scene_id: str = ""  # 关联的场景ID
    frames: list[RobotFrame] = []  # 帧列表

    def add_frame(self, frame: RobotFrame):
        """添加帧到序列"""
        # 自动设置seq（如果未设置）
        if frame.seq == 0 and len(self.frames) > 0:
            # 如果seq为0且已有帧，自动分配下一个序列号
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
