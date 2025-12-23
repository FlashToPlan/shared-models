"""机器人场景系统"""

from pydantic import BaseModel
import numpy as np

from .types import tensor1f, tensor2f


class Transform(BaseModel):
    """变换定义"""

    translation: tensor1f = [0.0, 0.0, 0.0]  # 平移 [x, y, z]
    rotation: tensor2f = []  # 旋转矩阵 3x3 或 4x4 齐次变换矩阵

    def to_matrix(self) -> tensor2f:
        """转换为4x4齐次变换矩阵"""
        if not self.rotation:
            # 如果没有旋转矩阵，创建单位矩阵
            rot = np.eye(3).tolist()
        else:
            rot = np.array(self.rotation)
            if rot.shape == (3, 3):
                # 3x3矩阵，扩展为4x4
                pass
            elif rot.shape == (4, 4):
                # 已经是4x4矩阵
                return rot.tolist()
            else:
                raise ValueError(f"Invalid rotation matrix shape: {rot.shape}")

        # 构建4x4齐次变换矩阵
        trans = np.array(self.translation)
        if len(trans) != 3:
            trans = np.array([0.0, 0.0, 0.0])

        matrix = np.eye(4)
        matrix[:3, :3] = rot
        matrix[:3, 3] = trans

        return matrix.tolist()

    def to_quaternion(self) -> tensor1f:
        """转换为四元数 [x, y, z, w]"""
        if not self.rotation:
            return [0.0, 0.0, 0.0, 1.0]

        rot = np.array(self.rotation)
        if rot.shape == (4, 4):
            rot = rot[:3, :3]
        elif rot.shape != (3, 3):
            return [0.0, 0.0, 0.0, 1.0]

        # 从旋转矩阵转换为四元数
        trace = np.trace(rot)
        if trace > 0:
            s = np.sqrt(trace + 1.0) * 2
            w = 0.25 * s
            x = (rot[2, 1] - rot[1, 2]) / s
            y = (rot[0, 2] - rot[2, 0]) / s
            z = (rot[1, 0] - rot[0, 1]) / s
        else:
            if rot[0, 0] > rot[1, 1] and rot[0, 0] > rot[2, 2]:
                s = np.sqrt(1.0 + rot[0, 0] - rot[1, 1] - rot[2, 2]) * 2
                w = (rot[2, 1] - rot[1, 2]) / s
                x = 0.25 * s
                y = (rot[0, 1] + rot[1, 0]) / s
                z = (rot[0, 2] + rot[2, 0]) / s
            elif rot[1, 1] > rot[2, 2]:
                s = np.sqrt(1.0 + rot[1, 1] - rot[0, 0] - rot[2, 2]) * 2
                w = (rot[0, 2] - rot[2, 0]) / s
                x = (rot[0, 1] + rot[1, 0]) / s
                y = 0.25 * s
                z = (rot[1, 2] + rot[2, 1]) / s
            else:
                s = np.sqrt(1.0 + rot[2, 2] - rot[0, 0] - rot[1, 1]) * 2
                w = (rot[1, 0] - rot[0, 1]) / s
                x = (rot[0, 2] + rot[2, 0]) / s
                y = (rot[1, 2] + rot[2, 1]) / s
                z = 0.25 * s

        return [float(x), float(y), float(z), float(w)]

    def to_euler(self) -> tensor1f:
        """转换为欧拉角 [roll, pitch, yaw] (ZYX顺序)"""
        if not self.rotation:
            return [0.0, 0.0, 0.0]

        rot = np.array(self.rotation)
        if rot.shape == (4, 4):
            rot = rot[:3, :3]
        elif rot.shape != (3, 3):
            return [0.0, 0.0, 0.0]

        # 从旋转矩阵提取欧拉角 (ZYX顺序，即yaw-pitch-roll)
        sy = np.sqrt(rot[0, 0] * rot[0, 0] + rot[1, 0] * rot[1, 0])
        singular = sy < 1e-6

        if not singular:
            x = np.arctan2(rot[2, 1], rot[2, 2])
            y = np.arctan2(-rot[2, 0], sy)
            z = np.arctan2(rot[1, 0], rot[0, 0])
        else:
            x = np.arctan2(-rot[1, 2], rot[1, 1])
            y = np.arctan2(-rot[2, 0], sy)
            z = 0

        return [float(x), float(y), float(z)]


class TransformOnFrame(BaseModel):
    """基于坐标系的变换"""

    transform: Transform = Transform()
    frame_id: str = "world"  # 坐标系ID


class BaseObjectInfo(BaseModel):
    """基础物件信息（抽象基类）"""

    name: str  # 物件唯一标识
    description: str = ""  # 描述
    pose: TransformOnFrame = TransformOnFrame()  # 位姿（包含变换和坐标系）
    frames: dict[str, TransformOnFrame] = {}  # 子坐标系 {frame_name: TransformOnFrame}
    movable: bool = False  # 是否可移动


class RobotInfo(BaseObjectInfo):
    """机器人信息"""

    robot_type: str = ""  # 机器人型号


class ObjectInfo(BaseObjectInfo):
    """其他物件信息（工件、夹具等）"""

    object_type: str = ""  # 物件类型


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
