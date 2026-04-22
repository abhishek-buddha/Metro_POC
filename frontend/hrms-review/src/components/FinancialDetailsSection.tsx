import type { DisplayData } from '../types/submission';

interface FinancialDetailsSectionProps {
  data: DisplayData['financialDetails'];
}

export const FinancialDetailsSection = ({ data }: FinancialDetailsSectionProps) => {
  const renderField = (label: string, value: string) => {
    const displayValue = value || 'Not available';
    const textClass = value ? 'text-gray-900' : 'text-gray-400 italic';

    return (
      <div key={label}>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
        <div className={`text-base ${textClass}`}>
          {displayValue}
        </div>
      </div>
    );
  };

  const renderDocument = (label: string, filename: string) => (
    <div key={label}>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
      <div className="text-base text-gray-900 flex items-center">
        <span className="mr-2">{filename}</span>
        <span className="text-green-600">✓</span>
      </div>
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
        <span className="mr-2">💳</span>
        Financial Details
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {renderField('Aadhaar Number', data.aadhaarNumber)}
        {renderDocument('E-Aadhaar Upload', data.aadhaarUpload)}
        {renderField('PAN Card Number', data.panCard)}
        {renderDocument('PAN Card Upload', data.panUpload)}
        {renderField("Father's Name", data.fatherName)}
      </div>
    </div>
  );
};
