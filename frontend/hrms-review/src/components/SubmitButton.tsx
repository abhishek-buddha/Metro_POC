import { useState } from 'react';
import { api } from '../services/api';

interface SubmitButtonProps {
  submissionId: string;
  onSuccess?: (employeeId: string) => void;
}

export const SubmitButton = ({ submissionId, onSuccess }: SubmitButtonProps) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await api.finalizeSubmission(submissionId, {
        finalized_by: 'hr_user@metro.com',
        notes: 'Auto-populated data verified via HRMS interface',
      });

      setSuccess(`Employee ID ${result.hrms_employee_id} created successfully!`);

      if (onSuccess) {
        onSuccess(result.hrms_employee_id);
      }
    } catch (err: any) {
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Failed to finalize submission. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {success && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-md">
          <p className="text-sm text-green-600">{success}</p>
        </div>
      )}

      <div className="flex justify-end space-x-4">
        <button
          type="button"
          className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-6 py-2.5 rounded-md transition-colors"
          onClick={() => window.history.back()}
        >
          Cancel
        </button>

        <button
          type="button"
          onClick={handleSubmit}
          disabled={isSubmitting || !!success}
          className={`bg-primary hover:bg-indigo-700 text-white px-6 py-2.5 rounded-md transition-colors flex items-center ${
            (isSubmitting || !!success) ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          {isSubmitting ? (
            <>
              <div className="w-4 h-4 mr-2 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Submitting...
            </>
          ) : success ? (
            'Submitted ✓'
          ) : (
            'Submit'
          )}
        </button>
      </div>
    </div>
  );
};
