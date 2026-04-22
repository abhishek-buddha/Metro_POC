import type { DisplayData } from '../types/submission';

interface BankDetailsSectionProps {
  data: DisplayData['bankDetails'];
}

export const BankDetailsSection = ({ data }: BankDetailsSectionProps) => {
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
        <span className="mr-2">🏦</span>
        Bank Details
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {renderField('Account Holder Name', data.accountHolderName)}
        {renderField('Account Number', data.accountNumber)}
        {renderField('IFSC Code', data.ifscCode)}
        {renderField('Bank Name', data.bankName)}
        {renderField('Branch Name', data.branchName)}
        {renderField('Account Type', data.accountType)}
        {renderDocument('Bank Statement Upload', data.bankStatementUpload)}
      </div>
    </div>
  );
};
