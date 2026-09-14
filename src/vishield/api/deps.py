"""Dependency wiring for the API."""

from __future__ import annotations

from fastapi import Request

from vishield.services.analyzer import AnalysisService


def get_service(request: Request) -> AnalysisService:
    service: AnalysisService = request.app.state.service
    return service
