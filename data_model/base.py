"""基础模型类"""

from pydantic import BaseModel

from .types import tensor1f, tensor2f


class EdgeInfo(BaseModel):
    """边信息"""

    class Samples(BaseModel):
        """采样点信息"""

        positions: list[list[float]] = []
        tangents: list[list[float]] = []
        rays: list[list[float]] = []

    group: int = -1
    type: str = ""
    length: float = 0
    samples: Samples = Samples()


class SeamInfo(BaseModel):
    """焊缝信息"""

    edges: list[EdgeInfo] = []
    stp_key: str = ""
    obj_key: str = ""
    parents: list[str] = []


class StpInfo(BaseModel):
    """STP文件信息"""

    key_stp: str = ""
    key_ply: str = ""

    volume: float = 0
    aabb: tensor1f = []
    obb: tensor2f = []
    tf_a2w: tensor2f = []
    nb_face: int = 0
    nb_edge: int = 0
    nb_wire: int = 0
    nb_vertex: int = 0
    intersects_aabb: list[str] = []
    is_mirror_obb: list[bool] = []
