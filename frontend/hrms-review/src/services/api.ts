import axios from 'axios';
import type { Submission, FinalizeRequest, FinalizeResponse } from '../types/submission';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY;

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json',
  },
});

export const api = {
  async getSubmission(submissionId: string): Promise<Submission> {
    const response = await apiClient.get(`/api/submissions/${submissionId}`);
    return response.data;
  },

  async finalizeSubmission(
    submissionId: string,
    data?: FinalizeRequest
  ): Promise<FinalizeResponse> {
    const response = await apiClient.post(
      `/api/submissions/${submissionId}/finalize`,
      data || {}
    );
    return response.data;
  },
};
