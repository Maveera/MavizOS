"""Human approval gate for destructive boot remediation."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from bootguardai.config import get_settings


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"


class ApprovalRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    action_type: str
    description: str
    target: str
    requested_by: str
    analysis_id: str | None = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    resolved_at: datetime | None = None
    resolved_by: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


DESTRUCTIVE_BOOT_ACTIONS = frozenset({
    "bootloader_rewrite",
    "bcd_destructive_change",
    "kernel_module_blacklist",
    "efi_modification",
    "grub_cfg_overwrite",
    "secure_boot_disable",
})


class ApprovalGate:
    def __init__(self) -> None:
        self._requests: dict[str, ApprovalRequest] = {}
        self._settings = get_settings()

    def requires_approval(self, action_type: str) -> bool:
        if not self._settings.require_approval:
            return action_type in DESTRUCTIVE_BOOT_ACTIONS
        return action_type in DESTRUCTIVE_BOOT_ACTIONS

    def request_approval(
        self,
        action_type: str,
        description: str,
        target: str,
        requested_by: str,
        analysis_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ApprovalRequest:
        req = ApprovalRequest(
            action_type=action_type,
            description=description,
            target=target,
            requested_by=requested_by,
            analysis_id=analysis_id,
            metadata=metadata or {},
        )
        self._requests[req.id] = req
        return req

    def approve(self, request_id: str, resolved_by: str) -> ApprovalRequest | None:
        req = self._requests.get(request_id)
        if req and req.status == ApprovalStatus.PENDING:
            req.status = ApprovalStatus.APPROVED
            req.resolved_at = datetime.now(UTC)
            req.resolved_by = resolved_by
        return req

    def deny(self, request_id: str, resolved_by: str) -> ApprovalRequest | None:
        req = self._requests.get(request_id)
        if req and req.status == ApprovalStatus.PENDING:
            req.status = ApprovalStatus.DENIED
            req.resolved_at = datetime.now(UTC)
            req.resolved_by = resolved_by
        return req

    def list_pending(self) -> list[ApprovalRequest]:
        return [r for r in self._requests.values() if r.status == ApprovalStatus.PENDING]
