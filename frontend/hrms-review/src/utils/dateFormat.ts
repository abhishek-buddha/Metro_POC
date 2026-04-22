/**
 * Format ISO date to DD/MM/YYYY
 */
export const formatDateForDisplay = (isoDate: string): string => {
  if (!isoDate) return '';

  const date = new Date(isoDate);
  if (isNaN(date.getTime())) {
    return isoDate; // Return original on invalid date
  }

  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  return `${day}/${month}/${year}`;
};

/**
 * Calculate age from date of birth
 */
export const calculateAge = (dob: string): number => {
  if (!dob) return 0;

  const birthDate = new Date(dob);
  if (isNaN(birthDate.getTime())) {
    return 0; // Return 0 on invalid date
  }

  const today = new Date();
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();

  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }

  return age < 0 ? 0 : age; // Also handle future dates
};

/**
 * Get default DOJ (7 days from today)
 */
export const getDefaultDOJ = (): string => {
  const date = new Date();
  date.setDate(date.getDate() + 7);
  return date.toISOString().split('T')[0];
};

/**
 * Format Aadhaar number with masking
 */
export const formatAadhaar = (last4: string): string => {
  if (!last4 || last4.length !== 4) {
    return 'XXXX XXXX XXXX';
  }
  return `XXXX XXXX ${last4}`;
};
