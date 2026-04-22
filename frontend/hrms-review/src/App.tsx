import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { DocumentUpload } from "./pages/DocumentUpload";
import { SubmissionReview } from "./pages/SubmissionReview";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 30_000 } },
});

/** Pulls submissionId from ?id= query param and renders the review page. */
function ReviewPage() {
  const id = new URLSearchParams(window.location.search).get("id") || "";
  return <SubmissionReview submissionId={id} />;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/"       element={<Navigate to="/upload" replace />} />
          <Route path="/upload" element={<DocumentUpload />} />
          <Route path="/review" element={<ReviewPage />} />
          <Route path="*"       element={<Navigate to="/upload" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
