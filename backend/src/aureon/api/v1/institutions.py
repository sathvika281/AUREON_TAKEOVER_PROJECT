from fastapi import APIRouter, Depends, HTTPException

from aureon.api.deps import get_career_event_repository, get_entrance_exam_repository, get_institution_repository
from aureon.domain.services.institution_profile import compute_institution_profile
from aureon.services.supabase.repositories.career_event_repository import CareerEventRepository
from aureon.services.supabase.repositories.entrance_exam_repository import EntranceExamRepository
from aureon.services.supabase.repositories.institution_repository import InstitutionRepository
from aureon.shared.schemas import (
    AcademicProgramDTO,
    CareerEventDTO,
    EntranceExamDTO,
    FacultyHighlightDTO,
    InnovationCenterDTO,
    InstitutionDetailDTO,
    InstitutionProfileDTO,
    InstitutionReviewDTO,
    InstitutionSummaryDTO,
    InternshipOpportunityDTO,
    ResearchLabDTO,
    StudentAmbassadorDTO,
    StudentOrganizationDTO,
    StudentProjectDTO,
)

router = APIRouter(prefix="/institutions", tags=["institutions"])


@router.get("", response_model=list[InstitutionSummaryDTO])
async def list_institutions(
    country: str | None = None,
    is_partner: bool | None = None,
    institutions: InstitutionRepository = Depends(get_institution_repository),
) -> list[InstitutionSummaryDTO]:
    """Institution Knowledge Base browse endpoint — always open, no
    gating. ``is_partner=true`` is how College Collaboration lists
    "Partner Colleges" specifically, without touching the existing
    College Match flow (which lists every institution, partner or not)."""
    results = await institutions.list_institutions(country=country, is_partner=is_partner)
    return [
        InstitutionSummaryDTO(
            id=i.id, name=i.name, country=i.country, city=i.city,
            trait_tags=i.trait_tags, is_partner=i.is_partner,
        )
        for i in results
    ]


@router.get("/{institution_id}", response_model=InstitutionDetailDTO)
async def get_institution_detail(
    institution_id: str,
    institutions: InstitutionRepository = Depends(get_institution_repository),
    events: CareerEventRepository = Depends(get_career_event_repository),
    entrance_exams: EntranceExamRepository = Depends(get_entrance_exam_repository),
) -> InstitutionDetailDTO:
    institution = await institutions.get_institution(institution_id)
    if institution is None:
        raise HTTPException(status_code=404, detail="Institution not found")

    labs = await institutions.list_research_labs(institution_id)
    orgs = await institutions.list_student_organizations(institution_id)
    programs = await institutions.list_academic_programs(institution_id)
    innovation_centers = await institutions.list_innovation_centers(institution_id)
    faculty_highlights = await institutions.list_faculty_highlights(institution_id)
    ambassadors = await institutions.list_student_ambassadors(institution_id)
    projects = await institutions.list_student_projects(institution_id)
    internships = await institutions.list_internship_opportunities(institution_id)
    upcoming_events = await events.list_career_events(institution_id=institution_id)
    exams = await entrance_exams.list_for_institution(institution_id)
    profile = compute_institution_profile(
        institution, research_labs=labs, innovation_centers=innovation_centers, student_organizations=orgs,
    )

    return InstitutionDetailDTO(
        id=institution.id,
        name=institution.name,
        country=institution.country,
        city=institution.city,
        research_culture=institution.research_culture,
        innovation_ecosystem=institution.innovation_ecosystem,
        industry_collaboration=institution.industry_collaboration,
        placements=institution.placements,
        learning_environment=institution.learning_environment,
        trait_tags=institution.trait_tags,
        is_partner=institution.is_partner,
        research_labs=[
            ResearchLabDTO(id=lb.id, name=lb.name, focus_area=lb.focus_area, description=lb.description)
            for lb in labs
        ],
        student_organizations=[
            StudentOrganizationDTO(id=o.id, name=o.name, focus_area=o.focus_area, description=o.description)
            for o in orgs
        ],
        academic_programs=[
            AcademicProgramDTO(
                id=p.id, name=p.name, degree_type=p.degree_type, field=p.field, description=p.description
            )
            for p in programs
        ],
        innovation_centers=[
            InnovationCenterDTO(id=c.id, name=c.name, focus_area=c.focus_area, description=c.description)
            for c in innovation_centers
        ],
        faculty_highlights=[
            FacultyHighlightDTO(
                id=f.id, name=f.name, title=f.title, expertise_area=f.expertise_area, bio=f.bio
            )
            for f in faculty_highlights
        ],
        student_ambassadors=[
            StudentAmbassadorDTO(id=a.id, student_label=a.student_label, program=a.program, message=a.message)
            for a in ambassadors
        ],
        student_projects=[
            StudentProjectDTO(
                id=p.id, student_label=p.student_label, project_title=p.project_title,
                description=p.description, skills_used=p.skills_used,
            )
            for p in projects
        ],
        internship_opportunities=[
            InternshipOpportunityDTO(id=i.id, title=i.title, field=i.field, description=i.description)
            for i in internships
        ],
        upcoming_events=[
            CareerEventDTO(
                id=e.id, title=e.title, event_type=e.event_type, institution_id=e.institution_id,
                mentor_id=e.mentor_id, description=e.description, scheduled_at=e.scheduled_at,
            )
            for e in upcoming_events
        ],
        campus_life_and_culture=institution.campus_life_and_culture,
        fees_summary=institution.fees_summary,
        scholarships_summary=institution.scholarships_summary,
        entrance_exams=[
            EntranceExamDTO(
                id=x.id, name=x.name, description=x.description, eligibility=x.eligibility,
                preparation_guidance=x.preparation_guidance, typical_timeline=x.typical_timeline,
            )
            for x in exams
        ],
        hostels=institution.hostels,
        exchange_programs=institution.exchange_programs,
        campus_facilities=institution.campus_facilities,
        student_reviews=[
            InstitutionReviewDTO(role_label=r.role_label, quote=r.quote, sentiment=r.sentiment)
            for r in institution.student_reviews
        ],
        profile=InstitutionProfileDTO(
            research=profile.research, entrepreneurship=profile.entrepreneurship,
            campus_life=profile.campus_life, international_exposure=profile.international_exposure,
        ),
    )
