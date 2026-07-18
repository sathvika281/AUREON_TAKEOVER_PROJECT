import pytest
from pydantic import ValidationError

from aureon.domain.services.suggestion_service import submit_suggestion, update_status


def _suggestion(**overrides):
    defaults: dict = dict(
        student_id="student_1",
        category="career",
        title="  Wildlife Photographer  ",
        description="  I couldn't find this career in the catalog.  ",
    )
    defaults.update(overrides)
    return submit_suggestion(**defaults)


def test_submit_suggestion_builds_a_pending_suggestion_with_trimmed_text():
    suggestion = _suggestion()
    assert suggestion.status == "pending"
    assert suggestion.title == "Wildlife Photographer"
    assert suggestion.description == "I couldn't find this career in the catalog."
    assert suggestion.review_notes is None
    assert suggestion.reviewed_at is None
    assert suggestion.context_metadata == {}


def test_submit_suggestion_carries_context_fields():
    suggestion = _suggestion(
        category="correction",
        context_type="opportunity",
        context_id="opportunity_1",
        context_metadata={"page_or_feature": "Opportunity Equality"},
        source_url="https://example.com/scholarship",
    )
    assert suggestion.context_type == "opportunity"
    assert suggestion.context_id == "opportunity_1"
    assert suggestion.context_metadata == {"page_or_feature": "Opportunity Equality"}
    assert suggestion.source_url == "https://example.com/scholarship"


def test_submit_suggestion_rejects_an_invalid_category():
    with pytest.raises(ValidationError):
        _suggestion(category="not_a_real_category")


def test_update_status_sets_reviewed_and_updated_timestamps():
    suggestion = _suggestion()
    updated = update_status(suggestion, status="approved", review_notes="Great find, adding it.")
    assert updated.status == "approved"
    assert updated.review_notes == "Great find, adding it."
    assert updated.reviewed_at is not None
    assert updated.updated_at >= suggestion.updated_at


def test_update_status_without_notes_leaves_prior_notes_untouched():
    suggestion = _suggestion()
    first = update_status(suggestion, status="under_review", review_notes="Looking into it.")
    second = update_status(first, status="approved")
    assert second.review_notes == "Looking into it."


def test_update_status_rejects_an_invalid_status():
    suggestion = _suggestion()
    with pytest.raises(ValueError):
        update_status(suggestion, status="not_a_real_status")
