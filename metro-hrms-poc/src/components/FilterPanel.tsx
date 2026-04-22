// Filter panel component for employee list
import React from 'react';
import type { FilterState } from '../utils/types';

interface FilterPanelProps {
  filters: FilterState;
  onFilterChange: (filters: FilterState) => void;
  onApply: () => void;
}

const FilterPanel: React.FC<FilterPanelProps> = ({ filters, onFilterChange, onApply }) => {
  const handleReset = () => {
    onFilterChange({ submissionStatus: '', submissionLevel: '' });
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-base font-semibold text-gray-900">Filters</h3>
        <button
          onClick={handleReset}
          className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
        >
          Reset
        </button>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Submission Status
          </label>
          <select
            value={filters.submissionStatus}
            onChange={(e) =>
              onFilterChange({ ...filters, submissionStatus: e.target.value })
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 text-sm bg-white"
          >
            <option value="">All</option>
            <option value="PENDING">Pending</option>
            <option value="APPROVED">In Progress</option>
            <option value="FINALIZED">Completed</option>
            <option value="REJECTED">Rejected</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Submission Level
          </label>
          <select
            value={filters.submissionLevel}
            onChange={(e) =>
              onFilterChange({ ...filters, submissionLevel: e.target.value })
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 text-sm bg-white"
          >
            <option value="">All</option>
            <option value="Basic Info">Basic Info</option>
            <option value="Payroll">Payroll</option>
            <option value="Completed">Completed</option>
          </select>
        </div>
      </div>

      <button
        onClick={onApply}
        className="w-full mt-6 bg-blue-600 text-white py-2.5 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
      >
        Apply
      </button>
    </div>
  );
};

export default FilterPanel;
