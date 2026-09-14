"""REST endpoints."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile

from vishield import __version__
from vishield.api.deps import get_service
from vishield.audio.validation import AudioValidationError
from vishield.domain.models import (
    AnalysisResult,
    BatchEvaluateRequest,
    BatchEvaluateResponse,
    HealthResponse,
    ModelInfo,
    SafetyPolicy,
    TranscriptAnalysisRequest,
)
from vishield.domain.safety import get_policy
from vishield.services.analyzer import AnalysisService

router = APIRouter()
Service = Annotated[AnalysisService, Depends(get_service)]


@router.get("/health", response_model=HealthResponse, tags=["system"])
def health(service: Service) -> HealthResponse:
    return HealthResponse(
        status="ok",
        version=__version__,
        model_loaded=service.classifier is not None,
        stt_backend=service.stt.name,
        timestamp=datetime.now(tz=UTC),
    )


@router.post("/analyze/transcript", response_model=AnalysisResult, tags=["analysis"])
def analyze_transcript(payload: TranscriptAnalysisRequest, service: Service) -> AnalysisResult:
    """Analyse a typed transcript (synthetic, public or consented text only)."""
    return service.analyze_transcript(payload.transcript)


@router.post("/analyze/audio", response_model=AnalysisResult, tags=["analysis"])
async def analyze_audio(
    service: Service,
    file: Annotated[UploadFile, File(description="WAV, MP3 or M4A")],
    consent_confirmed: Annotated[bool, Form()] = False,
) -> AnalysisResult:
    """Analyse an uploaded recording. Audio is processed in memory and not stored."""
    if not consent_confirmed:
        raise AudioValidationError(
            "consent_required",
            "You must confirm the recording is synthetic, public-domain or explicitly consented.",
        )
    max_bytes = service.settings.max_file_bytes
    data = await file.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise AudioValidationError(
            "too_large", f"File exceeds the {service.settings.max_file_mb:g} MB limit."
        )
    return service.analyze_audio(data, file.filename, file.content_type)


@router.post("/evaluate/batch", response_model=BatchEvaluateResponse, tags=["evaluation"])
def evaluate_batch(payload: BatchEvaluateRequest, service: Service) -> BatchEvaluateResponse:
    """Score many transcripts; returns metrics when labels are supplied."""
    return service.evaluate_batch(payload.items)


@router.get("/models/info", response_model=ModelInfo, tags=["system"])
def models_info(service: Service) -> ModelInfo:
    return service.model_info()


@router.get("/safety/policy", response_model=SafetyPolicy, tags=["system"])
def safety_policy() -> SafetyPolicy:
    return get_policy()
