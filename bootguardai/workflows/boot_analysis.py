"""10-step boot analysis workflow pipeline."""

import logging
from typing import TYPE_CHECKING

from bootguardai.models.boot_alert import BootMode, OSType
from bootguardai.models.workflow import BootAnalysisContext, WorkflowStep

if TYPE_CHECKING:
    from bootguardai.orchestrator.orchestrator import Orchestrator

logger = logging.getLogger(__name__)

BOOT_ANALYSIS_PIPELINE: list[tuple[str, str]] = [
    (WorkflowStep.COLLECT_CONTEXT, "collect"),
    (WorkflowStep.STAGE_IDENTIFICATION, "stage"),
    (WorkflowStep.BOOTLOADER_ANALYSIS, "bootloader_integrity"),
    (WorkflowStep.KERNEL_INIT_ANALYSIS, "kernel_analysis"),
    (WorkflowStep.DRIVER_MODULE_ANALYSIS, "driver_module"),
    (WorkflowStep.PERSISTENCE_SCAN, "persistence_hunt"),
    (WorkflowStep.THREAT_CORRELATION, "rootkit_bootkit"),
    (WorkflowStep.INTEGRITY_ASSESSMENT, "firmware_uefi"),
    (WorkflowStep.REMEDIATION_PLANNING, "remediation"),
    (WorkflowStep.REPORT_GENERATION, "reporting"),
]

POST_OS_AGENTS = [
    ("forensics_timeline", lambda c: True),
    ("script_command", lambda c: True),
    ("mitre_persistence", lambda c: True),
    ("memory_knowledge", lambda c: True),
]


class BootAnalysisWorkflow:
    def __init__(self, orchestrator: "Orchestrator") -> None:
        self._orchestrator = orchestrator

    async def execute(self, context: BootAnalysisContext) -> BootAnalysisContext:
        logger.info("Starting boot analysis %s", context.analysis_id)

        for step_name, agent_key in BOOT_ANALYSIS_PIPELINE:
            if agent_key == "collect":
                self._collect_context(context)
                continue
            if agent_key == "stage":
                await self._stage_identification(context)
                continue
            if agent_key == "driver_module":
                await self._driver_module(context)
                continue
            agent_name = agent_key
            logger.info("Step %s: agent %s", step_name, agent_name)
            await self._orchestrator.run_agent(agent_name, context)

        for agent_name, condition in POST_OS_AGENTS:
            if condition(context):
                await self._orchestrator.run_agent(agent_name, context)

        return context

    def _collect_context(self, context: BootAnalysisContext) -> None:
        if context.alerts:
            alert = context.alerts[0]
            if context.os_type == OSType.UNKNOWN:
                context.os_type = alert.os_type
            if context.boot_mode == BootMode.UNKNOWN:
                context.boot_mode = alert.boot_mode
            if context.secure_boot is None:
                context.secure_boot = alert.secure_boot
        context.metadata["pipeline_steps"] = len(BOOT_ANALYSIS_PIPELINE)
        context.soc_notes.append("BootGuardAI Boot Analysis Workflow v1.0")

    async def _stage_identification(self, context: BootAnalysisContext) -> None:
        if context.os_type == OSType.WINDOWS:
            await self._orchestrator.run_agent("windows_boot", context)
        elif context.os_type == OSType.LINUX:
            await self._orchestrator.run_agent("linux_boot", context)
        else:
            context.soc_notes.append("OS type unknown — run windows or linux targeted analysis")

    async def _driver_module(self, context: BootAnalysisContext) -> None:
        await self._orchestrator.run_agent("kernel_analysis", context)
        for comp in context.alerts[0].raw_data.get("loaded_drivers", []) if context.alerts else []:
            context.loaded_components.append(str(comp))
