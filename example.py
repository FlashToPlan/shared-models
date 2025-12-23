"""使用示例"""

from data_model import (
    DataBag,
    RobotScene,
    RobotInfo,
    ObjectInfo,
    Transform,
    TransformOnFrame,
    RobotFrame,
    RobotState,
    Trajectory,
    RobotFrameSequence,
)


def example_scene():
    """创建场景示例"""
    # 创建场景
    scene = RobotScene(scene_id="scene_001", scene_name="双机器人焊接场景", world_frame="world")

    # 添加第一个机器人（相对于世界坐标系）
    robot1 = RobotInfo(
        name="robot_1",
        robot_type="abb_irb6700_150_320",
        pose=TransformOnFrame(
            transform=Transform(
                translation=[0, 0, 0],
                rotation=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
            ),
            frame_id="world",
        ),
        movable=True,
    )
    # 添加机器人的子坐标系（如TCP坐标系和tool0）
    robot1.frames["tcp"] = TransformOnFrame(
        transform=Transform(translation=[0, 0, 100]), frame_id="robot_1"
    )
    robot1.frames["tool0"] = TransformOnFrame(
        transform=Transform(translation=[0, 0, 50]), frame_id="robot_1"
    )
    scene.robots[robot1.name] = robot1

    # 添加第二个机器人（相对于世界坐标系）
    robot2 = RobotInfo(
        name="robot_2",
        robot_type="abb_irb6700_150_320",
        pose=TransformOnFrame(
            transform=Transform(
                translation=[2000, 0, 0],  # 在世界坐标系的X方向2米处
                rotation=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
            ),
            frame_id="world",
        ),
        movable=True,
    )
    scene.robots[robot2.name] = robot2

    # 添加工具头（吸附到 robot_1 的 tool0 上）
    tool_head = ObjectInfo(
        name="tool_head_001",
        object_type="welding_torch",
        pose=TransformOnFrame(
            transform=Transform(
                translation=[0, 0, 150],  # 在 tool0 的 Z 方向 150mm
                rotation=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
            ),
            frame_id="robot_1/tool0",  # 相对于 robot_1 的 tool0 坐标系
        ),
        movable=True,
        description="焊接工具头",
    )
    scene.objects[tool_head.name] = tool_head

    # 添加工件（吸附到工具头上）
    workpiece = ObjectInfo(
        name="workpiece_001",
        object_type="welding_part",
        pose=TransformOnFrame(
            transform=Transform(
                translation=[0, 0, 200],  # 在工具头的 Z 方向 200mm
                rotation=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
            ),
            frame_id="tool_head_001",  # 相对于工具头
        ),
        movable=False,
        description="待焊接工件",
    )
    scene.objects[workpiece.name] = workpiece

    return scene


def example_frame():
    """创建RobotFrame示例"""
    # 创建RobotFrame
    frame = RobotFrame(seq=1, timestamp=1234567890.0, frame_id="frame_001", scene_id="scene_001")

    # 添加机器人状态
    robot_state = RobotState(
        robot_id="robot_1",
        joints=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
        tcp_pose=[[1, 0, 0, 100], [0, 1, 0, 200], [0, 0, 1, 300], [0, 0, 0, 1]],
        timestamp=1234567890.0,
    )
    frame.robot_states["robot_1"] = robot_state

    # 添加轨迹信息
    trajectory = Trajectory(
        robot_id="robot_1",
        waypoints=[
            [[1, 0, 0, 100], [0, 1, 0, 200], [0, 0, 1, 300], [0, 0, 0, 1]],
            [[1, 0, 0, 150], [0, 1, 0, 250], [0, 0, 1, 350], [0, 0, 0, 1]],
        ],
        timestamps=[1234567890.0, 1234567900.0],
        frame_id="world",
    )
    frame.trajectories["robot_1"] = trajectory

    # 添加物件更新（变换后的几何、点云、网格等）
    # frame_id 指向对应的坐标系，transform 是相对于该坐标系的变换

    # robot_1 的 tool0 坐标系更新
    frame.object_updates["robot_1/tool0"] = TransformOnFrame(
        transform=Transform(
            translation=[0, 0, 50],  # tool0 相对于 robot_1 的变换
            rotation=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
        ),
        frame_id="robot_1",  # 相对于 robot_1 坐标系
    )

    # 工具头的更新（相对于 tool0）
    frame.object_updates["tool_head_001"] = TransformOnFrame(
        transform=Transform(
            translation=[0, 0, 150],  # tool_head 相对于 robot_1/tool0 的变换
            rotation=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
        ),
        frame_id="robot_1/tool0",  # 相对于 robot_1/tool0 坐标系
    )

    # 工件的更新（相对于工具头）
    frame.object_updates["workpiece_001"] = TransformOnFrame(
        transform=Transform(
            translation=[0, 0, 200],  # workpiece 相对于 tool_head_001 的变换
            rotation=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
        ),
        frame_id="tool_head_001",  # 相对于 tool_head_001 坐标系
    )

    return frame


def example_sequence():
    """创建RobotFrameSequence示例"""
    # 创建帧序列
    sequence = RobotFrameSequence(sequence_id="seq_001", scene_id="scene_001")

    # 添加多个帧
    for i in range(10):
        frame = RobotFrame(seq=i, timestamp=1234567890.0 + i * 0.1, scene_id="scene_001")
        sequence.add_frame(frame)

    # 查询帧（示例用法）
    _ = sequence.get_frame_by_seq(5)
    _ = sequence.get_frames_by_robot("robot_1")

    return sequence


def example_databag():
    """创建DataBag示例"""
    # 创建场景
    scene = example_scene()

    # 创建DataBag
    databag = DataBag(
        bag_id="bag_001",
        bag_name="焊接任务数据包",
        description="包含场景和帧数据的完整数据包",
        scene=scene,
    )

    # 添加多个帧
    for i in range(5):
        frame = RobotFrame(
            seq=i,
            timestamp=1234567890.0 + i * 0.1,
            scene_id=scene.scene_id,
        )
        databag.add_frame(frame)

    return databag


if __name__ == "__main__":
    # 运行示例
    scene = example_scene()
    frame = example_frame()
    sequence = example_sequence()
    databag = example_databag()

    print(scene.model_dump_json(indent=2))
    print(frame.model_dump_json())
    print(sequence.model_dump_json())
    print(databag.model_dump_json(indent=2))

    open("databag.json", "w").write(databag.model_dump_json(indent=2))

    print("示例运行成功！")
