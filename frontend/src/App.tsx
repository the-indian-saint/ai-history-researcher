import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import MainLayout from "@/layout/MainLayout";
import Dashboard from "@/pages/Dashboard";
import ResearchList from "@/pages/research/ResearchList";
import NewResearch from "@/pages/research/NewResearch";
import ResearchStatus from "@/pages/research/ResearchStatus";
import DocumentList from "@/pages/documents/DocumentList";
import DocumentDetails from "@/pages/documents/DocumentDetails";
import SearchPage from "@/pages/search/SearchPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Dashboard />} />

            {/* Research Module */}
            <Route path="research">
              <Route index element={<ResearchList />} />
              <Route path="new" element={<NewResearch />} />
              <Route path=":id/results" element={<ResearchStatus />} />
              <Route path=":id/status" element={<ResearchStatus />} />
            </Route>

            {/* Document Module */}
            <Route path="documents">
              <Route index element={<DocumentList />} />
              <Route path=":id" element={<DocumentDetails />} />
            </Route>

            <Route path="search" element={<SearchPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
