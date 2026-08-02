from typing import Dict


class PipelineProgressProfile:
    """Weighted progress profile mapping pipeline stages to completion weights."""

    STAGE_WEIGHTS: Dict[str, int] = {
        "Queued": 0,
        "Upload": 5,
        "Validation": 5,
        "Preprocessing": 10,
        "Human Parsing": 15,
        "Pose Estimation": 15,
        "Agnostic Mask": 10,
        "Conditioning": 5,
        "Try-On": 30,
        "Postprocessing": 5,
        "Completed": 0,
    }

    STAGE_ORDER = [
        "Queued",
        "Upload",
        "Validation",
        "Preprocessing",
        "Human Parsing",
        "Pose Estimation",
        "Agnostic Mask",
        "Conditioning",
        "Try-On",
        "Postprocessing",
        "Completed",
    ]


class ProgressTracker:
    """Computes normalized progress percentage from weighted stage profile."""

    def __init__(
        self, profile: type[PipelineProgressProfile] = PipelineProgressProfile
    ) -> None:
        self.profile = profile
        self._cumulative_percentages: Dict[str, int] = {}
        self._compute_cumulative_weights()

    def _compute_cumulative_weights(self) -> None:
        """Calculates cumulative percentage per stage (0% to 100%)."""
        total_weight = sum(self.profile.STAGE_WEIGHTS.values())
        if total_weight == 0:
            total_weight = 100

        acc = 0
        for stage in self.profile.STAGE_ORDER:
            if stage == "Queued":
                self._cumulative_percentages[stage] = 0
            elif stage == "Completed":
                self._cumulative_percentages[stage] = 100
            else:
                acc += self.profile.STAGE_WEIGHTS.get(stage, 0)
                pct = int((acc / total_weight) * 100)
                self._cumulative_percentages[stage] = min(pct, 99)

    def get_progress_percent(self, stage: str) -> int:
        """Returns normalized integer progress percentage for a given stage name."""
        return self._cumulative_percentages.get(stage, 0)
