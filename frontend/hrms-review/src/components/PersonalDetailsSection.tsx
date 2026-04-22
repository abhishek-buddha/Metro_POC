import type { DisplayData } from '../types/submission';

interface PersonalDetailsSectionProps {
  data: DisplayData['personalDetails'];
}

export const PersonalDetailsSection = ({ data }: PersonalDetailsSectionProps) => {
  const renderField = (label: string, value: string | number) => {
    const displayValue = value || 'Not extracted from documents';
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

  const fields = [
    { label: 'Employee Name', value: data.employeeName },
    { label: 'Date of Birth', value: data.dateOfBirth },
    { label: 'Gender', value: data.gender },
    { label: 'Phone Number', value: data.phoneNumber },
    { label: 'Email', value: data.email },
    { label: 'Age', value: data.age || '' },
    { label: 'Address Line 1', value: data.addressLine1 },
    { label: 'Address Line 2', value: data.addressLine2 },
    { label: 'Address Line 3', value: data.addressLine3 },
  ];

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
        <span className="mr-2">👤</span>
        Personal Details
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {fields.map((field) => renderField(field.label, field.value))}
      </div>
    </div>
  );
};
