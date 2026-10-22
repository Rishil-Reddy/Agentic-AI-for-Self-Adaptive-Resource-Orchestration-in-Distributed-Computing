"""Admin views for governance and execution oversight."""

from __future__ import annotations

import logging

from django.contrib import messages
from django.db import connection, transaction
from django.shortcuts import redirect, render

from agentic.models import AgentProfile, AgentStatus, WorkflowExecution, WorkflowStatus
from agentic.services import bootstrap_demo_catalogue, dashboard_snapshot
from users.models import UserRegistrationModel

logger = logging.getLogger(__name__)


def AdminLoginCheck(request):
    if request.method == "POST":
        usrid = request.POST.get("loginid")
        pswd = request.POST.get("pswd")
        logger.info("Admin login attempt loginid=%s", usrid)
        if usrid == "admin" and pswd == "admin":
            logger.info("Admin login successful loginid=%s", usrid)
            return redirect("AdminHome")
        logger.warning("Admin login failed loginid=%s", usrid)
        messages.error(request, "Please check your login details.")
    return render(request, "AdminLogin.html", {})


def AdminHome(request):
    bootstrap_demo_catalogue()
    agents = AgentProfile.objects.all()
    executions = WorkflowExecution.objects.select_related("workflow")
    snapshot = dashboard_snapshot()
    context = {
        "user_count": UserRegistrationModel.objects.count(),
        "activated_count": UserRegistrationModel.objects.filter(status="activated").count(),
        "agent_identity_count": agents.count(),
        "trust_eval_count": executions.count(),
        "policy_count": executions.filter(status=WorkflowStatus.COMPLETED).count(),
        "log_count": executions.filter(status__in=[WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]).count(),
        "active_agent_count": agents.filter(status__in=[AgentStatus.IDLE, AgentStatus.RUNNING]).count(),
        "running_workflows": executions.filter(status=WorkflowStatus.RUNNING).count(),
        "completed_workflows": executions.filter(status=WorkflowStatus.COMPLETED).count(),
        "failed_workflows": executions.filter(status=WorkflowStatus.FAILED).count(),
        "snapshot": snapshot,
        "recent_executions": executions.order_by("-started_at")[:5],
    }
    return render(request, "admins/AdminHome.html", context)


def RegisterUsersView(request):
    registry = []
    for user in UserRegistrationModel.objects.all():
        trust_score = 82.0 if user.status == "activated" else 42.0
        registry.append(
            {
                "user": user,
                "identity": {
                    "did": f"did:agent:{user.loginid}",
                    "agent_id": f"AGENT-{user.id:04d}",
                    "trust_score": trust_score,
                    "verification_status": "verified" if user.status == "activated" else "pending",
                    "credential_status": "valid" if user.status == "activated" else "pending",
                    "lifecycle_status": user.status,
                },
            }
        )
    logger.info("Admin viewed registered users count=%s", len(registry))
    return render(request, "admins/viewregisterusers.html", {"data": registry})


def ActivaUsers(request):
    if request.method == "GET":
        user_id = request.GET.get("uid")
        updated = UserRegistrationModel.objects.filter(id=user_id).update(status="activated")
        logger.info("Admin activated user user_id=%s updated=%s", user_id, updated)
        if updated:
            messages.success(request, "Identity activated.")
        else:
            messages.warning(request, "Identity not found.")
    return redirect("RegisterUsersView")


def DeleteUser(request):
    if request.method == "GET":
        user_id = request.GET.get("uid")
        deleted = _revoke_user_graph(user_id)
        logger.info("Admin deleted user user_id=%s deleted=%s", user_id, deleted)
        if deleted:
            messages.success(request, "Identity revoked and related records removed.")
        else:
            messages.warning(request, "Identity not found.")
    return redirect("RegisterUsersView")


def _revoke_user_graph(user_id: str) -> bool:
    """Delete the user and any legacy rows that still reference it."""
    if not user_id:
        return False

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM UserRegistrations WHERE id = %s", [user_id])
            if cursor.fetchone() is None:
                return False

            cursor.execute(
                "SELECT id FROM AgentIdentities WHERE owner_id = %s",
                [user_id],
            )
            identity_ids = [row[0] for row in cursor.fetchall()]

            cursor.execute(
                "SELECT id FROM TrustEvaluations WHERE identity_id IN ({})".format(
                    ",".join(["%s"] * len(identity_ids)) if identity_ids else "NULL"
                ),
                identity_ids if identity_ids else [],
            )
            evaluation_ids = [row[0] for row in cursor.fetchall()]

            if evaluation_ids:
                placeholders = ",".join(["%s"] * len(evaluation_ids))
                cursor.execute(f"DELETE FROM ZeroTrustExecutionLogs WHERE evaluation_id IN ({placeholders})", evaluation_ids)
                cursor.execute(f"DELETE FROM ComplianceResults WHERE evaluation_id IN ({placeholders})", evaluation_ids)
                cursor.execute(f"DELETE FROM AgentDecisions WHERE evaluation_id IN ({placeholders})", evaluation_ids)
                cursor.execute(f"DELETE FROM RiskAssessments WHERE evaluation_id IN ({placeholders})", evaluation_ids)
                cursor.execute(f"DELETE FROM TrustEvaluations WHERE id IN ({placeholders})", evaluation_ids)

            if identity_ids:
                placeholders = ",".join(["%s"] * len(identity_ids))
                cursor.execute(f"DELETE FROM AgentCredentials WHERE identity_id IN ({placeholders})", identity_ids)
                cursor.execute(f"DELETE FROM AuthenticationLogs WHERE identity_id IN ({placeholders})", identity_ids)
                cursor.execute(f"DELETE FROM ZeroTrustExecutionLogs WHERE identity_id IN ({placeholders})", identity_ids)
                cursor.execute(f"DELETE FROM AgentIdentities WHERE id IN ({placeholders})", identity_ids)

            cursor.execute(
                "UPDATE GeneratedContents SET workflow_id = NULL WHERE owner_id = %s",
                [user_id],
            )
            cursor.execute(
                "UPDATE ContentWorkflows SET content_id = NULL WHERE owner_id = %s",
                [user_id],
            )
            cursor.execute(
                "DELETE FROM AgentExecutionLogs WHERE workflow_id IN (SELECT id FROM ContentWorkflows WHERE owner_id = %s)",
                [user_id],
            )
            cursor.execute(
                "DELETE FROM AgentExecutionLogs WHERE content_id IN (SELECT id FROM GeneratedContents WHERE owner_id = %s)",
                [user_id],
            )
            cursor.execute("DELETE FROM GeneratedContents WHERE owner_id = %s", [user_id])
            cursor.execute("DELETE FROM ContentWorkflows WHERE owner_id = %s", [user_id])
            cursor.execute("DELETE FROM UserRegistrations WHERE id = %s", [user_id])

    return True
