import type { DisplayData } from '../types/submission';

interface OrganizationElementsSectionProps {
  data: DisplayData['organizationElements'];
}

export const OrganizationElementsSection = ({ data }: OrganizationElementsSectionProps) => {
  const fields = [
    { label: 'Entity', value: data.entity },
    { label: 'Business Unit', value: data.businessUnit },
    { label: 'Function', value: data.function },
    { label: 'Base Location', value: data.baseLocation },
    { label: 'Department', value: data.department },
    { label: 'Designation', value: data.designation },
    { label: 'Position', value: data.position },
    { label: 'Employment Type', value: data.employmentType },
    { label: 'Estimated DOJ', value: data.estimatedDOJ },
  ];

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
        <span className="mr-2">📋</span>
        Organization Elements
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {fields.map((field) => (
          <div key={field.label}>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {field.label}
            </label>
            <div className="text-base text-gray-900">
              {field.value}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
