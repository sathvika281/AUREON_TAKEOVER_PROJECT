import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AuthScreen } from "./features/auth/AuthScreen";
import { ForgotPasswordScreen } from "./features/auth/ForgotPasswordScreen";
import { OnboardingGate } from "./features/auth/OnboardingGate";
import { ProtectedRoute } from "./features/auth/ProtectedRoute";
import { ResetPasswordScreen } from "./features/auth/ResetPasswordScreen";
import { CareerDnaScreen } from "./features/career-dna/CareerDnaScreen";
import { CareerDetailsScreen } from "./features/career-details/CareerDetailsScreen";
import { CompanyDetailScreen } from "./features/companies/CompanyDetailScreen";
import { CompaniesScreen } from "./features/companies/CompaniesScreen";
import { ProjectDetailScreen } from "./features/projects/ProjectDetailScreen";
import { ProjectsScreen } from "./features/projects/ProjectsScreen";
import { SkillDetailScreen } from "./features/skills/SkillDetailScreen";
import { SkillsScreen } from "./features/skills/SkillsScreen";
import { CareerExperienceProvider } from "./features/career-experience/CareerExperienceContext";
import { CollegeCollaborationScreen } from "./features/career-experience/CollegeCollaborationScreen";
import { ExpertConnectScreen } from "./features/career-experience/ExpertConnectScreen";
import { JointSessionTokenScreen } from "./features/career-experience/JointSessionTokenScreen";
import { JourneyStoriesScreen } from "./features/career-experience/JourneyStoriesScreen";
import { KnowledgeCirclesScreen } from "./features/career-experience/KnowledgeCirclesScreen";
import { MentorshipReviewScreen } from "./features/career-experience/MentorshipReviewScreen";
import { MyMentorsScreen } from "./features/career-experience/MyMentorsScreen";
import { ParentConnectScreen } from "./features/career-experience/ParentConnectScreen";
import { SharedSessionScreen } from "./features/career-experience/SharedSessionScreen";
import { CareerExplorationProvider } from "./features/career-exploration/CareerExplorationContext";
import { CareerIntelligenceProvider } from "./features/career-intelligence/CareerIntelligenceContext";
import { DecisionLabScreen } from "./features/decision/DecisionLabScreen";
import { DecisionProvider } from "./features/decision/DecisionContext";
import { DiscoveryScreen } from "./features/discovery/components/DiscoveryScreen";
import { DocumentIntelligenceProvider } from "./features/document-intelligence/DocumentIntelligenceContext";
import { DiscoveryProvider } from "./features/discovery/DiscoveryContext";
import { ExperienceLabScreen } from "./features/experience-lab/ExperienceLabScreen";
import { ExposureUniverseScreen } from "./features/exposure-universe/ExposureUniverseScreen";
import { GlobalCareerDiscoveryScreen } from "./features/global-discovery/GlobalCareerDiscoveryScreen";
import { GitHubIntelligenceProvider } from "./features/github-intelligence/GitHubIntelligenceContext";
import { GlobalTrendsScreen } from "./features/global-trends/GlobalTrendsScreen";
import { HiddenPotentialScreen } from "./features/hidden-potential/HiddenPotentialScreen";
import { HistoryProvider } from "./features/history/HistoryContext";
import { HistoryScreen } from "./features/history/HistoryScreen";
import { HomeScreen } from "./features/home/HomeScreen";
import { LearningStyleDiscoveryScreen } from "./features/learning-style-discovery/LearningStyleDiscoveryScreen";
import { LockedModule } from "./features/locked/LockedModule";
import { NotFoundScreen } from "./features/locked/NotFoundScreen";
import { ALL_MODULES } from "./features/navigation/journeyConfig";
import { JourneyNav } from "./features/navigation/JourneyNav";
import { OnboardingScreen } from "./features/onboarding/OnboardingScreen";
import { OpportunityEqualityScreen } from "./features/opportunity-equality/OpportunityEqualityScreen";
import { ProfileScreen } from "./features/profile/ProfileScreen";
import { ReflectionJournalScreen } from "./features/reflection-journal/ReflectionJournalScreen";
import { SearchInvestigationProvider } from "./features/search-investigation/SearchInvestigationContext";
import { HelpAureonGrowModal } from "./features/suggestions/HelpAureonGrowModal";
import { MySuggestionsScreen } from "./features/suggestions/MySuggestionsScreen";
import { SuggestionReviewScreen } from "./features/suggestions/SuggestionReviewScreen";
import { SuggestionsProvider } from "./features/suggestions/SuggestionsContext";
import { UrlInvestigationProvider } from "./features/url-investigation/UrlInvestigationContext";
import { AuthProvider } from "./shared/auth/AuthContext";
import { Layout } from "./shared/components/Layout";

const lockedModules = ALL_MODULES.filter((module) => module.locked);

function AppShell() {
  return (
    <DiscoveryProvider>
      <CareerIntelligenceProvider>
        <CareerExplorationProvider>
          <CareerExperienceProvider>
          <DecisionProvider>
              <UrlInvestigationProvider>
                <DocumentIntelligenceProvider>
                  <GitHubIntelligenceProvider>
                    <SearchInvestigationProvider>
                      <HistoryProvider>
                        <SuggestionsProvider>
                        <Layout>
                          <div className="flex h-full">
                            <JourneyNav />
                            <main className="h-full flex-1 overflow-y-auto">
                              <Routes>
                                <Route path="/" element={<HomeScreen />} />
                                <Route path="/dashboard" element={<HomeScreen />} />
                                <Route path="/history" element={<HistoryScreen />} />
                                <Route path="/profile" element={<ProfileScreen />} />
                                <Route path="/suggestions" element={<MySuggestionsScreen />} />
                                <Route path="/discover/identity" element={<DiscoveryScreen />} />
                                <Route path="/discover/career-dna" element={<CareerDnaScreen />} />
                                <Route path="/discover/reflection-journal" element={<ReflectionJournalScreen />} />
                                <Route path="/discover/hidden-potential" element={<HiddenPotentialScreen />} />
                                <Route path="/discover/experience-lab" element={<ExperienceLabScreen />} />
                                {/* Exposure Universe merge — Missing Worlds is no longer a
                                    separate destination; its detection engine now composes
                                    into Exposure Universe. Redirect, never a broken URL. */}
                                <Route path="/discover/missing-worlds" element={<Navigate to="/explore/exposure-universe" replace />} />
                                <Route path="/discover/life-missions" element={<Navigate to="/discover/experience-lab" replace />} />
                                <Route path="/discover/learning-style-discovery" element={<LearningStyleDiscoveryScreen />} />
                                <Route path="/explore/career-reality" element={<GlobalCareerDiscoveryScreen />} />
                                <Route path="/explore/career-reality/:careerId" element={<CareerDetailsScreen />} />
                                {/* Sprint 1 — Skill Knowledge Base. No new top-level nav entry
                                 * per docs/SPRINT_1.md's scope; reached via real links from a
                                 * Career page's new Skills section. */}
                                <Route path="/skills" element={<SkillsScreen />} />
                                <Route path="/skills/:skillId" element={<SkillDetailScreen />} />
                                {/* Sprint 2 — Company Knowledge Base. Same no-new-nav-entry
                                 * scope as Skill; reached via real links from Career pages. */}
                                <Route path="/companies" element={<CompaniesScreen />} />
                                <Route path="/companies/:companyId" element={<CompanyDetailScreen />} />
                                {/* Sprint 3 — Project Knowledge Base. Same no-new-nav-entry
                                 * scope as Skill/Company; reached via real links from Career
                                 * pages and the Projects browse page. */}
                                <Route path="/projects" element={<ProjectsScreen />} />
                                <Route path="/projects/:projectId" element={<ProjectDetailScreen />} />
                                <Route path="/explore/global-trends" element={<GlobalTrendsScreen />} />
                                <Route path="/explore/exposure-universe" element={<ExposureUniverseScreen />} />
                                <Route path="/explore/opportunity-equality" element={<OpportunityEqualityScreen />} />
                                <Route path="/experience/college-collaboration" element={<CollegeCollaborationScreen />} />
                                <Route path="/experience/expert-connect" element={<ExpertConnectScreen />} />
                                <Route path="/experience/expert-connect/my-mentors" element={<MyMentorsScreen />} />
                                <Route path="/experience/expert-connect/parent-connect" element={<ParentConnectScreen />} />
                                <Route path="/experience/parent-connect" element={<Navigate to="/experience/expert-connect/parent-connect" replace />} />
                                <Route path="/experience/mentorships" element={<Navigate to="/experience/expert-connect/my-mentors" replace />} />
                                <Route path="/experience/shared-sessions" element={<SharedSessionScreen />} />
                                <Route path="/experience/knowledge-circles" element={<KnowledgeCirclesScreen />} />
                                <Route path="/experience/journey-stories" element={<JourneyStoriesScreen />} />
                                <Route path="/decide/decision-lab" element={<DecisionLabScreen />} />
                                {lockedModules.map((module) => (
                                  <Route
                                    key={module.id}
                                    path={module.path}
                                    element={<LockedModule module={module} />}
                                  />
                                ))}
                                {/* Sprint 7 — global catch-all. Must stay last: React
                                    Router matches routes in order, and every entity
                                    route above (e.g. /projects/:projectId) already
                                    matches its own pattern regardless of whether the
                                    id resolves, so this only ever catches paths with
                                    no matching pattern at all. */}
                                <Route path="*" element={<NotFoundScreen />} />
                              </Routes>
                            </main>
                          </div>
                          <HelpAureonGrowModal />
                        </Layout>
                        </SuggestionsProvider>
                      </HistoryProvider>
                    </SearchInvestigationProvider>
                  </GitHubIntelligenceProvider>
                </DocumentIntelligenceProvider>
              </UrlInvestigationProvider>
          </DecisionProvider>
          </CareerExperienceProvider>
        </CareerExplorationProvider>
      </CareerIntelligenceProvider>
    </DiscoveryProvider>
  );
}

export function App() {
  return (
    <BrowserRouter basename={import.meta.env.BASE_URL}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<AuthScreen />} />
          <Route path="/forgot-password" element={<ForgotPasswordScreen />} />
          {/* Sprint 6 — where a password-reset email link lands. Outside
              ProtectedRoute deliberately: a student clicking this link
              may have no normal session at all, and the screen itself
              verifies the recovery token via a dedicated Supabase auth
              event rather than the general login gate. */}
          <Route path="/reset-password" element={<ResetPasswordScreen />} />
          {/* Connect Batch 1 — a parent/guardian's only way into a Joint
              Session is this opaque token, so it must stay entirely
              outside ProtectedRoute/OnboardingGate — no login required. */}
          <Route path="/joint-session/:token" element={<JointSessionTokenScreen />} />
          {/* Connect Batch 2 — same reasoning as Joint Sessions above: an
              expert has no login anywhere in this system, so their only
              way into a mentorship review is this opaque token. */}
          <Route path="/mentorship-review/:token" element={<MentorshipReviewScreen />} />
          {/* Suggest to Aureon — there is no admin/staff role anywhere in
              this system, so the reviewer screen is gated by a secret
              entered on the screen itself rather than login, same
              reasoning as the token-gated routes above. Deliberately
              never linked from any nav. */}
          <Route path="/suggestions/review" element={<SuggestionReviewScreen />} />
          <Route
            path="/onboarding"
            element={
              <ProtectedRoute>
                <OnboardingScreen />
              </ProtectedRoute>
            }
          />
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <OnboardingGate>
                  <AppShell />
                </OnboardingGate>
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
