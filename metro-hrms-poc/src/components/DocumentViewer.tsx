// Document viewer modal with password protection
import React, { useState } from 'react';
import { X } from 'lucide-react';
import type { DocumentViewerProps } from '../utils/types';

const DocumentViewer: React.FC<DocumentViewerProps> = ({
  isOpen,
  onClose,
  documentUrl,
  documentName,
  requiresPassword = false,
}) => {
  const [password, setPassword] = useState('');
  const [showPasswordDialog, setShowPasswordDialog] = useState(requiresPassword);
  const [isUnlocked, setIsUnlocked] = useState(!requiresPassword);

  if (!isOpen) return null;

  const handlePasswordSubmit = () => {
    // In a real app, verify the password
    setIsUnlocked(true);
    setShowPasswordDialog(false);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">View Document</h2>
            <p className="text-sm text-gray-500">{documentName}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X size={20} className="text-gray-600" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto bg-gray-900 relative">
          {showPasswordDialog && !isUnlocked ? (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="bg-gray-800 p-6 rounded-lg shadow-xl max-w-md w-full mx-4">
                <p className="text-white mb-4">Enter the password to open this PDF file.</p>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Password"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-400 focus:outline-none focus:border-indigo-500 mb-4"
                  onKeyPress={(e) => e.key === 'Enter' && handlePasswordSubmit()}
                />
                <div className="flex space-x-3 justify-end">
                  <button
                    onClick={() => {
                      setShowPasswordDialog(false);
                      onClose();
                    }}
                    className="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handlePasswordSubmit}
                    className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition-colors"
                  >
                    OK
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="w-full h-full min-h-[600px]">
              {documentUrl.toLowerCase().endsWith('.pdf') ? (
                <iframe
                  src={documentUrl}
                  className="w-full h-full min-h-[600px]"
                  title={documentName}
                />
              ) : (
                <img
                  src={documentUrl}
                  alt={documentName}
                  className="max-w-full max-h-full object-contain mx-auto"
                />
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentViewer;
