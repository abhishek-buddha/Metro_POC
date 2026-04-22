import type { Submission, DisplayData } from '../types/submission';
import { formatDateForDisplay, calculateAge, getDefaultDOJ, formatAadhaar } from './dateFormat';

export const transformSubmissionData = (submission: Submission): DisplayData => {
  // Split address into multiple lines
  const addressParts = (submission.aadhaar_address || '').split(',').map(s => s.trim());

  return {
    organizationElements: {
      entity: "Metro Brands Limited",
      businessUnit: "Showroom(SR)",
      function: "Maharashtra(MAHARASHTRA)",
      baseLocation: "PLV(PLV)",
      department: "PLV(PLV)",
      designation: "Salesman",
      position: "Field Sales",
      employmentType: "Full-time",
      estimatedDOJ: formatDateForDisplay(getDefaultDOJ()),
    },

    personalDetails: {
      employeeName: submission.aadhaar_name || submission.pan_name || 'N/A',
      dateOfBirth: formatDateForDisplay(submission.aadhaar_dob || submission.pan_dob || ''),
      gender: submission.aadhaar_gender || 'Not specified',
      phoneNumber: submission.employee.phone_number || 'Not available',
      email: '',
      addressLine1: addressParts[0] || '',
      addressLine2: addressParts[1] || '',
      addressLine3: addressParts.slice(2).join(', '),
      age: calculateAge(submission.aadhaar_dob || submission.pan_dob || ''),
    },

    financialDetails: {
      aadhaarNumber: formatAadhaar(submission.aadhaar_last4 || ''),
      aadhaarUpload: 'eAadhaar.pdf',
      panCard: submission.pan_number || 'Not available',
      panUpload: 'PAN.pdf',
      fatherName: submission.pan_father_name || 'Not available',
    },

    bankDetails: {
      accountHolderName: submission.bank_holder_name || 'Not available',
      accountNumber: submission.bank_account || 'Not available',
      ifscCode: submission.bank_ifsc || 'Not available',
      bankName: submission.bank_name || 'Not available',
      branchName: submission.bank_branch || 'Not available',
      accountType: submission.bank_account_type || 'Savings',
      bankStatementUpload: 'bank_statement.pdf',
    },
  };
};
