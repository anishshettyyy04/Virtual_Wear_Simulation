from app.schemas.ai import (
    ImageDimensions,
    PostprocessingResult,
    RawTryOnOutput,
)
from app.services.ai.interfaces.postprocessor import BasePostprocessor
from app.utils.logger import logger


class MockPostprocessor(BasePostprocessor):
    """Deterministic mock postprocessor implementation."""

    async def process(self, raw_output: RawTryOnOutput) -> PostprocessingResult:
        logger.info(
            f"MockPostprocessor: Finalizing image encoding for raw render "
            f"'{raw_output.raw_render_id}'"
        )
        out_ref = raw_output.output_ref if (raw_output.output_ref and not raw_output.output_ref.startswith("mock://")) else f"data/processed/renders/final_{raw_output.raw_render_id}.jpg"
        return PostprocessingResult(
            final_image_id=f"final_{raw_output.raw_render_id}",
            output_ref=out_ref,
            dimensions=ImageDimensions(width=1024, height=1024),
            format="jpeg",
            metadata={
                "color_enhanced": True,
                "sharpened": True,
                "model_used": raw_output.model_name,
            },
        )
