"""DataBag - 包含场景和帧数据的容器"""

from pydantic import BaseModel

from .scene import RobotScene
from .frame import RobotFrame, RobotFrameSequence


class DataBag(BaseModel):
    """数据包，包含场景和帧数据"""

    # 场景配置
    scene: RobotScene

    # 帧数据（帧序列）
    frames: RobotFrameSequence | None = None

    # 元数据
    bag_id: str = ""  # 数据包ID
    bag_name: str = ""  # 数据包名称
    description: str = ""  # 描述
    created_at: str = ""
    updated_at: str = ""
    version: str = "1.0.0"

    def add_frame(self, frame: RobotFrame):
        """添加帧到数据包"""
        # 确保帧的 scene_id 与场景匹配
        if frame.scene_id and frame.scene_id != self.scene.scene_id:
            raise ValueError(
                f"Frame scene_id '{frame.scene_id}' does not match scene scene_id '{self.scene.scene_id}'"
            )
        frame.scene_id = self.scene.scene_id

        # 如果有帧序列，添加到序列中；否则创建新序列
        if self.frames is None:
            self.frames = RobotFrameSequence(
                sequence_id=f"{self.bag_id}_sequence",
                scene_id=self.scene.scene_id,
            )
        self.frames.add_frame(frame)

    def get_frames(self) -> list[RobotFrame]:
        """获取所有帧"""
        if self.frames:
            return self.frames.frames
        return []

    def get_frame_by_seq(self, seq: int) -> RobotFrame | None:
        """根据序列号获取帧"""
        if self.frames:
            return self.frames.get_frame_by_seq(seq)
        return None

    def get_frames_by_robot(self, robot_id: str) -> list[RobotFrame]:
        """获取包含指定机器人的所有帧"""
        if self.frames:
            return self.frames.get_frames_by_robot(robot_id)
        return []
