import json
import os
from datetime import datetime
from typing import Any, Dict, List


class MeshStorageService:
    def __init__(self, storage_dir: str = "samples/saved_meshes") -> None:
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def save(self, data: Dict[str, Any], filename_prefix: str = "mesh_result") -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.json"
        filepath = os.path.join(self.storage_dir, filename)

        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

        return filename

    def list_files(self) -> List[str]:
        files = [
            file_name
            for file_name in os.listdir(self.storage_dir)
            if file_name.endswith(".json")
        ]
        files.sort(reverse=True)
        return files

    def load(self, filename: str) -> Dict[str, Any]:
        filepath = os.path.join(self.storage_dir, filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No existe el archivo: {filename}")

        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)