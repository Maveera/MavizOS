"""Human approval gate for destructive remediation actions."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from mavizos.config import get_settings


class ApprovalStatus(str, Enum):
    """Approval request lifecycle."""

    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"


class ApprovalRequest(BaseModel):
    """Request for human approval of a destructive action."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    action_type: str
    description: str
    target: str
    requested_by: str
    incident_id: str | None = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    resolved_at: datetime | None = None
    resolved_by: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


# Actions that always require human approval
DESTRUCTIVE_ACTIONS = frozenset({
    "account_disable",
    "host_isolation",
    "firewall_block",
    "credential_reset",
    "quarantine",
    "file_deletion",
    "system_shutdown",
    "email_purge",
})


class ApprovalGate:
    """Gate destructive actions behind explicit human approval."""

    def __init__(self) -> None:
        self._requests: dict[str, ApprovalRequest] = {}
        self._settings = get_settings()

    def requires_approval(self, action_type: str) -> bool:
        """Return True if action type needs approval."""
        if not self._settings.require_approval:
            return action_type in DESTRUCTIVE_ACTIONS
        return action_type in DESTRUCTIVE_ACTIONS

    def request_approval(
        self,
        action_type: str,
        description: str,
        target: str,
        requested_by: str,
        incident_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ApprovalRequest:
        """Create a pending approval request."""
        req = ApprovalRequest(
            action_type=action_type,
            description=description,
            target=target,
            requested_by=requested_by,
            incident_id=incident_id,
            metadata=metadata or {},
        )
        self._requests[req.id] = req
        return req

    def approve(self, request_id: str, resolved_by: str) -> ApprovalRequest | None:
        """Approve a pending request."""
        req = self._requests.get(request_id)
        if req and req.status == ApprovalStatus.PENDING:
            req.status = ApprovalStatus.APPROVED
            req.resolved_at = datetime.now(UTC)
            req.resolved_by = resolved_by
        return req

    def deny(self, request_id: str, resolved_by: str) -> ApprovalRequest | None:
        """Deny a pending request."""
        req = self._requests.get(request_id)
        if req and req.status == ApprovalStatus.PENDING:
            req.status = ApprovalStatus.DENIED
            req.resolved_at = datetime.now(UTC)
            req.resolved_by = resolved_by
        return req

    def get(self, request_id: str) -> ApprovalRequest | None:
        """Retrieve approval request by ID."""
        return self._requests.get(request_id)

    def list_pending(self) -> list[ApprovalRequest]:
        """List all pending approval requests."""
        return [r for r in self._requests.values() if r.status == ApprovalStatus.PENDING]
