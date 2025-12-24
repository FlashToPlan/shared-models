"""机器人场景系统"""

from pydantic import BaseModel

from .types import tensor1f, tensor2f


class Transform(BaseModel):
    """变换定义"""

    translation: tensor1f = [0.0, 0.0, 0.0]  # 平移 [x, y, z]
    rotation: tensor1f = [0.0, 0.0, 0.0, 1.0]  # 四元数 [x, y, z, w] (RWT格式)

    def to_matrix(self) -> tensor2f:
        """转换为4x4齐次变换矩阵"""
        import numpy as np

        # 从四元数转换为旋转矩阵 (RWT格式: [x, y, z, w])
        if not self.rotation or len(self.rotation) != 4:
            rot_matrix = np.eye(3)
        else:
            x, y, z, w = self.rotation  # RWT格式: [x, y, z, w]
            # 归一化四元数
            norm = np.sqrt(w * w + x * x + y * y + z * z)
            if norm > 1e-6:
                w, x, y, z = w / norm, x / norm, y / norm, z / norm
            else:
                rot_matrix = np.eye(3)
                w, x, y, z = 1.0, 0.0, 0.0, 0.0

            # 从四元数转换为旋转矩阵
            rot_matrix = np.array(
                [
                    [
                        1 - 2 * (y * y + z * z),
                        2 * (x * y - w * z),
                        2 * (x * z + w * y),
                    ],
                    [
                        2 * (x * y + w * z),
                        1 - 2 * (x * x + z * z),
                        2 * (y * z - w * x),
                    ],
                    [
                        2 * (x * z - w * y),
                        2 * (y * z + w * x),
                        1 - 2 * (x * x + y * y),
                    ],
                ]
            )

        # 构建4x4齐次变换矩阵
        trans = np.array(self.translation)
        if len(trans) != 3:
            trans = np.array([0.0, 0.0, 0.0])

        matrix = np.eye(4)
        matrix[:3, :3] = rot_matrix
        matrix[:3, 3] = trans

        return matrix.tolist()

    def to_quaternion(self) -> tensor1f:
        """转换为四元数 [x, y, z, w] (RWT格式，直接返回rotation)"""
        if not self.rotation or len(self.rotation) != 4:
            return [0.0, 0.0, 0.0, 1.0]
        return list(self.rotation)

    def to_euler(self) -> tensor1f:
        """转换为欧拉角 [roll, pitch, yaw] (ZYX顺序)"""
        import numpy as np

        if not self.rotation or len(self.rotation) != 4:
            return [0.0, 0.0, 0.0]

        x, y, z, w = self.rotation  # RWT格式: [x, y, z, w]
        # 归一化四元数
        norm = np.sqrt(w * w + x * x + y * y + z * z)
        if norm > 1e-6:
            w, x, y, z = w / norm, x / norm, y / norm, z / norm
        else:
            return [0.0, 0.0, 0.0]

        # 从四元数转换为欧拉角 (ZYX顺序，即yaw-pitch-roll)
        # roll (x-axis rotation)
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = np.arctan2(sinr_cosp, cosr_cosp)

        # pitch (y-axis rotation)
        sinp = 2 * (w * y - z * x)
        if abs(sinp) >= 1:
            pitch = np.copysign(np.pi / 2, sinp)  # use 90 degrees if out of range
        else:
            pitch = np.arcsin(sinp)

        # yaw (z-axis rotation)
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = np.arctan2(siny_cosp, cosy_cosp)

        return [float(roll), float(pitch), float(yaw)]


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
