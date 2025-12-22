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
    # 添加机器人的子坐标系（如TCP坐标系）
    robot1.frames["tcp"] = TransformOnFrame(
        transform=Transform(translation=[0, 0, 100]), frame_id="robot_1"
    )
    scene.add_robot(robot1)

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
    scene.add_robot(robot2)

    # 添加工件（相对于世界坐标系）
    workpiece = ObjectInfo(
        name="workpiece_001",
        object_type="welding_part",
        pose=TransformOnFrame(
            transform=Transform(
                translation=[1000, 0, 500],
                rotation=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
            ),
            frame_id="world",
        ),
        movable=False,
        description="待焊接工件",
    )
    scene.add_object(workpiece)

    # 查询变换（通过world坐标系）
    transform_matrix = scene.get_transform("robot_1", "robot_2")
    print(f"从robot_1到robot_2的变换矩阵: {transform_matrix}")

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
    frame.object_updates["workpiece_001"] = TransformOnFrame(
        transform=Transform(
            translation=[1000, 0, 500],
            rotation=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
        ),
        frame_id="world",
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

    print("示例运行成功！")
