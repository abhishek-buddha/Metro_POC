import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SubmissionReview } from './pages/SubmissionReview';

const queryClient = new QueryClient();

function App() {
  // For POC, hardcode a submission ID or get from URL
  // In production, use react-router-dom
  const urlParams = new URLSearchParams(window.location.search);
  const submissionId = urlParams.get('id') || 'test-submission-id';

  return (
    <QueryClientProvider client={queryClient}>
      <SubmissionReview submissionId={submissionId} />
    </QueryClientProvider>
  );
}

export default App;
