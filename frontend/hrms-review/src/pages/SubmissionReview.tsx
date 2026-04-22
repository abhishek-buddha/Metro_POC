import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { transformSubmissionData } from '../utils/dataTransform';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorState } from '../components/ErrorState';
import { OrganizationElementsSection } from '../components/OrganizationElementsSection';
import { PersonalDetailsSection } from '../components/PersonalDetailsSection';
import { FinancialDetailsSection } from '../components/FinancialDetailsSection';
import { BankDetailsSection } from '../components/BankDetailsSection';
import { SubmitButton } from '../components/SubmitButton';

interface SubmissionReviewProps {
  submissionId: string;
}

export const SubmissionReview = ({ submissionId }: SubmissionReviewProps) => {
  const { data: submission, isLoading, error, refetch } = useQuery({
    queryKey: ['submission', submissionId],
    queryFn: () => api.getSubmission(submissionId),
    retry: 3,
    staleTime: 30000,
  });

  if (isLoading) {
    return <LoadingSpinner message="Loading submission data..." />;
  }

  if (error) {
    return (
      <ErrorState
        title="Unable to load submission"
        message="Please check your connection and try again"
        onRetry={() => refetch()}
      />
    );
  }

  if (!submission) {
    return (
      <ErrorState
        title="Submission Not Found"
        message="The requested submission does not exist"
      />
    );
  }

  const displayData = transformSubmissionData(submission);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-2xl font-semibold text-gray-900 mb-6">
          Employee Onboarding Review
        </h1>

        <div className="space-y-6">
          <OrganizationElementsSection data={displayData.organizationElements} />
          <PersonalDetailsSection data={displayData.personalDetails} />
          <FinancialDetailsSection data={displayData.financialDetails} />
          <BankDetailsSection data={displayData.bankDetails} />
          <SubmitButton submissionId={submissionId} />
        </div>
      </div>
    </div>
  );
};
