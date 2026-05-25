from __future__ import annotations

import json
import os
from typing import Any, Optional

import pandas as pd


class DataExporter:
    def __init__(self, output_dir: str = "evacsim/data/output") -> None:
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export_csv(
        self, data: list[dict[str, Any]], filename: str
    ) -> str:
        filepath = os.path.join(self.output_dir, filename)
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        return filepath

    def export_json(
        self, data: list[dict[str, Any]], filename: str
    ) -> str:
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        return filepath

    def export_dataframe(
        self, data: list[dict[str, Any]]
    ) -> pd.DataFrame:
        return pd.DataFrame(data)

    def export_all(
        self,
        data: list[dict[str, Any]],
        base_name: str,
        formats: Optional[list[str]] = None,
    ) -> list[str]:
        if formats is None:
            formats = ["csv", "json"]

        paths = []
        for fmt in formats:
            if fmt == "csv":
                path = self.export_csv(data, f"{base_name}.csv")
            elif fmt == "json":
                path = self.export_json(data, f"{base_name}.json")
            else:
                continue
            paths.append(path)
        return paths
