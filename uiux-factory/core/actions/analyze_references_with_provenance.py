from __future__ import annotations

import hashlib
import json
from pathlib import Path

from metagpt.actions import Action

from core.actions.analyze_references_with_motion import AnalyzeReferencesWithMotion
from core.contracts.design_context_schema import ReferenceBoard


class AnalyzeReferencesWithProvenance(Action):
    """Publish deep browser evidence path + digest into the compact ReferenceBoard lineage."""

    name: str = "AnalyzeReferencesWithProvenance"

    async def run(self, instruction: str) -> str:
        board_raw = await AnalyzeReferencesWithMotion().run(instruction)
        payload = json.loads(instruction)
        run_dir = Path(payload["run_dir"])
        evidence_path = run_dir / "reference-evidence.v1.json"
        board = ReferenceBoard.model_validate_json(board_raw)
        if evidence_path.is_file():
            raw = evidence_path.read_bytes()
            board.evidence_artifact = str(evidence_path.resolve())
            board.evidence_sha256 = hashlib.sha256(raw).hexdigest()
        return board.model_dump_json(indent=2)
