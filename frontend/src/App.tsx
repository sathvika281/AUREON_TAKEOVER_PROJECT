import { BrowserRouter, Route, Routes } from "react-router-dom";

import { AuthScreen } from "./features/auth/AuthScreen";
import { ProtectedRoute } from "./features/auth/ProtectedRoute";
import { CareerDnaScreen } from "./features/career-dna/CareerDnaScreen";
import { CareerDetailsScreen } from "./features/career-details/CareerDetailsScreen";
import { CareerExperienceProvider } from "./features/career-experience/CareerExperienceContext";
import { CollegeCollaborationScreen } from "./features/career-experience/CollegeCollaborationScreen";
import { ExpertConnectScreen } from "./features/career-experience/ExpertConnectScreen";
import { CareerExplorationProvider } from "./features/career-exploration/CareerExplorationContext";
import { CareerIntelligenceProvider } from "./features/career-intelligence/CareerIntelligenceContext";
import { CareerIntelligenceScreen } from "./features/career-intelligence/CareerIntelligenceScreen";
import { CareerSimulatorScreen } from "./features/decision/CareerSimulatorScreen";
import { DecisionLabScreen } from "./features/decision/DecisionLabScreen";
import { DecisionProvider } from "./features/decision/DecisionContext";
import { MentorMatchScreen } from "./features/decision/MentorMatchScreen";
import { ParallelUniverseScreen } from "./features/decision/ParallelUniverseScreen";
import { DiscoveryScreen } from "./features/discovery/components/DiscoveryScreen";
import { DocumentIntelligenceProvider } from "./features/document-intelligence/DocumentIntelligenceContext";
import { DiscoveryProvider } from "./features/discovery/DiscoveryContext";
import { FutureLensScreen } from "./features/future-lens/FutureLensScreen";
import { GlobalCareerDiscoveryScreen } from "./features/global-discovery/GlobalCareerDiscoveryScreen";
import { GitHubIntelligenceProvider } from "./features/github-intelligence/GitHubIntelligenceContext";
import { HiddenPotentialScreen } from "./features/hidden-potential/HiddenPotentialScreen";
import { HistoryProvider } from "./features/history/HistoryContext";
import { HistoryScreen } from "./features/history/HistoryScreen";
import { HomeScreen } from "./features/home/HomeScreen";
import { LockedModule } from "./features/locked/LockedModule";
import { ALL_MODULES } from "./features/navigation/journeyConfig";
import { JourneyNav } from "./features/navigation/JourneyNav";
import { ProfileScreen } from "./features/profile/ProfileScreen";
import { ProgressProvider } from "./features/progress/ProgressContext";
import { ProgressScreen } from "./features/progress/ProgressScreen";
import { ReflectionJournalScreen } from "./features/reflection-journal/ReflectionJournalScreen";
import { SearchInvestigationProvider } from "./features/search-investigation/SearchInvestigationContext";
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
            <ProgressProvider>
              <UrlInvestigationProvider>
                <DocumentIntelligenceProvider>
                  <GitHubIntelligenceProvider>
                    <SearchInvestigationProvider>
                      <HistoryProvider>
                        <Layout>
                          <div className="flex h-full">
                            <JourneyNav />
                            <main className="h-full flex-1 overflow-y-auto">
                              <Routes>
                                <Route path="/" element={<HomeScreen />} />
                                <Route path="/dashboard" element={<HomeScreen />} />
                                <Route path="/history" element={<HistoryScreen />} />
                                <Route path="/profile" element={<ProfileScreen />} />
                                <Route path="/discover/identity" element={<DiscoveryScreen />} />
                                <Route path="/discover/career-dna" element={<CareerDnaScreen />} />
                                <Route path="/discover/reflection-journal" element={<ReflectionJournalScreen />} />
                                <Route path="/discover/hidden-potential" element={<HiddenPotentialScreen />} />
                                <Route path="/explore/career-intelligence" element={<CareerIntelligenceScreen />} />
                                <Route path="/explore/career-reality" element={<GlobalCareerDiscoveryScreen />} />
                                <Route path="/explore/career-reality/:careerId" element={<CareerDetailsScreen />} />
                                <Route path="/explore/future-lens" element={<FutureLensScreen />} />
                                <Route path="/experience/college-collaboration" element={<CollegeCollaborationScreen />} />
                                <Route path="/experience/expert-connect" element={<ExpertConnectScreen />} />
                                <Route path="/decide/decision-lab" element={<DecisionLabScreen />} />
                                <Route path="/decide/parallel-universe" element={<ParallelUniverseScreen />} />
                                <Route path="/decide/mentor-match" element={<MentorMatchScreen />} />
                                <Route path="/decide/career-simulator" element={<CareerSimulatorScreen />} />
                                <Route path="/build/progress-intelligence" element={<ProgressScreen />} />
                                {lockedModules.map((module) => (
                                  <Route
                                    key={module.id}
                                    path={module.path}
                                    element={<LockedModule module={module} />}
                                  />
                                ))}
                              </Routes>
                            </main>
                          </div>
                        </Layout>
                      </HistoryProvider>
                    </SearchInvestigationProvider>
                  </GitHubIntelligenceProvider>
                </DocumentIntelligenceProvider>
              </UrlInvestigationProvider>
            </ProgressProvider>
          </DecisionProvider>
          </CareerExperienceProvider>
        </CareerExplorationProvider>
      </CareerIntelligenceProvider>
    </DiscoveryProvider>
  );
}

export function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<AuthScreen />} />
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <AppShell />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
