import pytest

import aureon.agents.specialized  # noqa: F401  (registers every agent)
from aureon.agents.registry import AgentRegistry
from aureon.domain.models.student_profile import StudentProfile
from aureon.shared.types import AgentName


def _agent():
    return AgentRegistry.get(AgentName.CAREER_ORCHESTRATOR.value)


def test_career_orchestrator_registers_with_real_capabilities():
    assert AgentName.CAREER_ORCHESTRATOR.value in AgentRegistry.names()
    descriptor = next(d for d in AgentRegistry.describe_all() if d.name == AgentName.CAREER_ORCHESTRATOR.value)
    assert descriptor.is_recommendation_stage is False


def test_plan_execution_resolves_mentor_match_analysis():
    plan = _agent().plan_execution(objective="mentor_match_analysis", profile=StudentProfile(student_id="s1"))
    assert plan.primary_agent == AgentName.DECISION.value
    assert [s.agent_name for s in plan.steps] == [AgentName.MENTOR.value]


def test_plan_execution_resolves_college_match_analysis():
    plan = _agent().plan_execution(objective="college_match_analysis", profile=StudentProfile(student_id="s1"))
    assert plan.primary_agent == AgentName.DECISION.value
    assert [s.agent_name for s in plan.steps] == [AgentName.INSTITUTION.value]


def test_plan_execution_resolves_progress_intelligence_analysis():
    plan = _agent().plan_execution(objective="progress_intelligence_analysis", profile=StudentProfile(student_id="s1"))
    assert plan.primary_agent == AgentName.GROWTH.value
    assert [s.agent_name for s in plan.steps] == [AgentName.GROWTH.value]
    assert plan.steps[0].capability is None  # primary agent doing its own work, no delegation


def test_plan_execution_raises_for_unknown_objective():
    with pytest.raises(ValueError):
        _agent().plan_execution(objective="not_a_real_objective", profile=StudentProfile(student_id="s1"))


async def test_run_is_a_no_op_passthrough():
    from aureon.agents.state import new_state

    state = new_state(conversation_id="c1", student_id="s1")
    result = await _agent().run(state, llm=None)
    assert result["agent_history"] == [AgentName.CAREER_ORCHESTRATOR.value]
    assert AgentName.CAREER_ORCHESTRATOR.value in result["agent_outputs"]
