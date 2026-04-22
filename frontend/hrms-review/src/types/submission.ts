export interface Employee {
  id: string;
  phone_number: string;
}

export interface Submission {
  id: string;
  employee_id: string;
  status: "APPROVED" | "PENDING" | "REJECTED" | "FINALIZED";
  employee: Employee;

  // PAN Card Data (all optional)
  pan_number?: string;
  pan_name?: string;
  pan_father_name?: string;
  pan_dob?: string;
  pan_confidence?: number;

  // Aadhaar Data (all optional)
  aadhaar_last4?: string;
  aadhaar_name?: string;
  aadhaar_dob?: string;
  aadhaar_gender?: "Male" | "Female" | "Other";
  aadhaar_address?: string;
  aadhaar_pincode?: string;
  aadhaar_confidence?: number;

  // Bank Data (all optional)
  bank_account?: string;
  bank_holder_name?: string;
  bank_ifsc?: string;
  bank_name?: string;
  bank_branch?: string;
  bank_account_type?: string;
  bank_micr?: string;
  bank_confidence?: number;

  // Metadata (optional)
  name_match_score?: number;
  overall_confidence?: number;

  // Review fields (optional)
  reviewed_at?: string;
  reviewed_by?: string;
  review_notes?: string;

  // Finalization fields (optional)
  finalized_at?: string;
  finalized_by?: string;
  hrms_employee_id?: string;

  submitted_at: string;
}

export interface FinalizeRequest {
  finalized_by?: string;
  notes?: string;
}

export interface FinalizeResponse {
  id: string;
  status: "FINALIZED";
  finalized_at: string;
  finalized_by?: string;
  hrms_employee_id: string;
  message: string;
}

export interface DisplayData {
  organizationElements: {
    entity: string;
    businessUnit: string;
    function: string;
    baseLocation: string;
    department: string;
    designation: string;
    position: string;
    employmentType: string;
    estimatedDOJ: string;
  };

  personalDetails: {
    employeeName: string;
    dateOfBirth: string;
    gender: string;
    phoneNumber: string;
    email: string;
    addressLine1: string;
    addressLine2: string;
    addressLine3: string;
    age: number;
  };

  financialDetails: {
    aadhaarNumber: string;
    aadhaarUpload: string;
    panCard: string;
    panUpload: string;
    fatherName: string;
  };

  bankDetails: {
    accountHolderName: string;
    accountNumber: string;
    ifscCode: string;
    bankName: string;
    branchName: string;
    accountType: string;
    bankStatementUpload: string;
  };
}
