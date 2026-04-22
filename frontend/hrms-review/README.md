# HRMS Auto-Population Interface

React-based HRMS interface for reviewing and finalizing employee onboarding data extracted from WhatsApp documents.

## Prerequisites

- Node.js 18+
- Backend API running on port 8000
- Valid API key

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create `.env` file:
   ```bash
   cp .env.example .env
   ```

3. Update `.env` with your API key:
   ```
   VITE_API_BASE_URL=http://localhost:8000
   VITE_API_KEY=your_api_key_here
   ```

## Development

Start dev server:
```bash
npm run dev
```

Open in browser:
```
http://localhost:5173?id={submission_id}
```

Replace `{submission_id}` with an actual APPROVED submission ID.

## Build

Create production build:
```bash
npm run build
```

Output in `dist/` directory.

## Architecture

- **React 18** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **React Query** for data fetching
- **Axios** for API calls

## Project Structure

```
src/
  components/     # Reusable UI components
  pages/          # Page components
  services/       # API client
  utils/          # Helper functions
  types/          # TypeScript interfaces
```

## Features

- Auto-populated employee data from document extraction
- View-only display (no editing)
- Organization elements with defaults
- Personal, Financial, and Bank details sections
- Submit to finalize with HRMS employee ID generation
- Error handling and loading states

## Environment Variables

- `VITE_API_BASE_URL` - Backend API URL
- `VITE_API_KEY` - API authentication key
