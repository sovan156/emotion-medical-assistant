import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, AlertCircle, CheckCircle, X } from 'lucide-react';
import { useChat } from '../../contexts/ChatContext';

const CONCERN_CONFIG = {
  low: { color: 'text-green-600', bg: 'bg-green-50', icon: CheckCircle, label: 'Low Concern' },
  moderate: { color: 'text-yellow-600', bg: 'bg-yellow-50', icon: AlertCircle, label: 'Moderate Concern' },
  high: { color: 'text-red-600', bg: 'bg-red-50', icon: AlertCircle, label: 'Requires Attention' },
};

const ReportUpload = ({ onSuccess }) => {
  const { uploadReport, reportData, isLoading } = useChat();
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);

  const onDrop = useCallback(
    async (acceptedFiles) => {
      const file = acceptedFiles[0];
      if (!file) return;

      setUploadedFile(file);
      const result = await uploadReport(file);
      if (result && onSuccess) {
        setTimeout(onSuccess, 2000);
      }
    },
    [uploadReport, onSuccess]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
    onDragEnter: () => setDragActive(true),
    onDragLeave: () => setDragActive(false),
  });

  if (reportData) {
    const concernConfig = CONCERN_CONFIG[reportData.concern_level] || CONCERN_CONFIG.low;
    const ConcernIcon = concernConfig.icon;

    return (
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="p-4 bg-white"
      >
        <div className="flex items-start gap-3 mb-3">
          <div className="w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center flex-shrink-0">
            <CheckCircle size={20} className="text-green-600" />
          </div>
          <div className="flex-1">
            <p className="font-semibold text-gray-800 text-sm">{reportData.file_name}</p>
            <p className="text-xs text-gray-500">Report processed successfully</p>
          </div>
          <div
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${concernConfig.bg} ${concernConfig.color}`}
          >
            <ConcernIcon size={12} />
            {concernConfig.label}
          </div>
        </div>

        <div className="bg-gray-50 rounded-xl p-3 mb-3">
          <p className="text-xs font-semibold text-gray-600 mb-1.5">Summary</p>
          <p className="text-xs text-gray-600 leading-relaxed line-clamp-4">
            {reportData.summary}
          </p>
        </div>

        {reportData.key_findings?.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-gray-600 mb-1.5">Key Areas</p>
            <div className="space-y-1">
              {reportData.key_findings.slice(0, 2).map((finding, i) => (
                <div key={i} className="flex items-start gap-2">
                  <span className="text-blue-500 mt-0.5 flex-shrink-0">•</span>
                  <p className="text-xs text-gray-600 line-clamp-2">{finding}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="mt-3 p-2.5 bg-blue-50 rounded-lg">
          <p className="text-xs text-blue-700">
            💬 Your report is ready. Ask me anything about it in the chat below.
          </p>
        </div>
      </motion.div>
    );
  }

  return (
    <div className="p-4 bg-white">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all ${
          isDragActive || dragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
        }`}
      >
        <input {...getInputProps()} />

        <AnimatePresence mode="wait">
          {isLoading ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-3"
            >
              <div className="w-12 h-12 mx-auto rounded-xl bg-blue-100 flex items-center justify-center">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                >
                  <Upload size={24} className="text-blue-500" />
                </motion.div>
              </div>
              <p className="text-sm font-medium text-gray-600">
                Processing your report...
              </p>
              <p className="text-xs text-gray-400">This may take a moment</p>
            </motion.div>
          ) : (
            <motion.div
              key="upload"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-3"
            >
              <div
                className={`w-12 h-12 mx-auto rounded-xl flex items-center justify-center transition-colors ${
                  isDragActive ? 'bg-blue-500' : 'bg-blue-100'
                }`}
              >
                <FileText
                  size={24}
                  className={isDragActive ? 'text-white' : 'text-blue-500'}
                />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">
                  {isDragActive ? 'Drop your report here' : 'Upload Medical Report'}
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  Drag & drop or click to select • PDF or TXT • Max 10MB
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <p className="text-xs text-gray-400 text-center mt-2">
        ⚕️ Your data is processed securely and not shared with third parties.
      </p>
    </div>
  );
};

export default ReportUpload;
