import os
from datetime import datetime
from typing import List

from backend.app.models.mesh_model import Triangle, Vertex3D


class ObjExportService:
    def __init__(self, export_dir: str = "samples/exports") -> None:
        self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)

    def export(
        self,
        vertices: List[Vertex3D],
        triangles: List[Triangle],
        filename_prefix: str = "face_model"
    ) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.obj"
        filepath = os.path.join(self.export_dir, filename)

        with open(filepath, "w", encoding="utf-8") as file:
            file.write("# Face 3D Mesh App OBJ Export\n")
            file.write("# Vertices\n")

            for vertex in vertices:
                file.write(f"v {vertex.x:.6f} {vertex.y:.6f} {vertex.z:.6f}\n")

            file.write("\n# Faces\n")

            for triangle in triangles:
                # OBJ usa índices desde 1, no desde 0
                a = triangle.a + 1
                b = triangle.b + 1
                c = triangle.c + 1
                file.write(f"f {a} {b} {c}\n")

        return filepath