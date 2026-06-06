import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, RefreshCw, Globe } from 'lucide-react';
import MessageBubble from './MessageBubble';
import VoiceInput from './VoiceInput';
import EmotionDisplay from './EmotionDisplay';
import ReportUpload from '../Report/ReportUpload';
import { useChat } from '../../contexts/ChatContext';

const LANGUAGE_OPTIONS = [
  { code: 'en', label: '🇺🇸 English' },
  { code: 'hi', label: '🇮🇳 Hindi' },
  { code: 'bn', label: '🇧🇩 Bengali' },
];

const WELCOME_MESSAGE = `**Welcome to your Medical Communication Assistant** 💙

I'm here to help you understand your health information in a supportive, clear way.

Here's how I can help:
• Explain medical reports in simple terms
• Answer questions about your health information
• Provide emotionally aware, supportive guidance

⚕️ **Important**: I provide health information for educational purposes only. I am not a doctor and do not provide medical diagnoses. Always consult a qualified healthcare professional for medical advice.

**How are you feeling today? Feel free to share what's on your mind, or upload a medical report to get started.**`;

const ChatWindow = () => {
  const {
    messages,
    isLoading,
    currentEmotion,
    sessionPhase,
    suggestedQuestions,
    escalationData,
    language,
    setLanguage,
    sendMessage,
    resetConversation,
    reportData,
  } = useChat();

  const [inputText, setInputText] = useState('');
  const [showReportUpload, setShowReportUpload] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!inputText.trim() || isLoading) return;
    const text = inputText;
    setInputText('');
    await sendMessage(text, false);
    inputRef.current?.focus();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleVoiceTranscription = async (text) => {
    if (text) {
      await sendMessage(text, true);
    }
  };

  const handleSuggestedQuestion = async (question) => {
    await sendMessage(question, false);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full gradient-primary flex items-center justify-center">
                <span className="text-white text-sm">⚕️</span>
              </div>
              <div>
                <h1 className="font-bold text-gray-800 text-sm">
                  Medical Communication Assistant
                </h1>
                <p className="text-xs text-gray-500">
                  Emotionally aware • Supportive • Educational
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* Language Selector */}
              <div className="flex items-center gap-1.5 bg-gray-50 rounded-lg px-3 py-2">
                <Globe size={14} className="text-gray-500" />
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="text-xs bg-transparent border-none outline-none text-gray-600 cursor-pointer"
                >
                  {LANGUAGE_OPTIONS.map((lang) => (
                    <option key={lang.code} value={lang.code}>
                      {lang.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Report Upload Toggle */}
              <button
                onClick={() => setShowReportUpload(!showReportUpload)}
                className={`text-xs px-3 py-2 rounded-lg transition-colors ${
                  reportData
                    ? 'bg-green-100 text-green-700'
                    : showReportUpload
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {reportData ? '✅ Report Loaded' : '📄 Upload Report'}
              </button>

              {/* Reset Button */}
              <button
                onClick={resetConversation}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                title="Start new conversation"
              >
                <RefreshCw size={16} />
              </button>
            </div>
          </div>
        </div>

        {/* Report Upload Panel */}
        <AnimatePresence>
          {showReportUpload && !reportData && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden border-b border-gray-200"
            >
              <ReportUpload onSuccess={() => setShowReportUpload(false)} />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Disclaimer Banner */}
        <div className="bg-blue-50 border-b border-blue-100 px-6 py-2">
          <p className="text-xs text-blue-700 text-center">
            ⚕️ This assistant provides health information for educational purposes only.
            It does not replace professional medical advice.
          </p>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {/* Welcome Message */}
          {messages.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4"
            >
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full gradient-primary flex items-center justify-center flex-shrink-0">
                  <span className="text-white text-xs">AI</span>
                </div>
                <div className="bg-white rounded-2xl rounded-tl-none px-4 py-3 shadow-sm border border-gray-100 max-w-2xl">
                  <div className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
                    {WELCOME_MESSAGE.split('\n').map((line, i) => {
                      if (line.startsWith('**') && line.endsWith('**')) {
                        return <strong key={i} className="block font-bold mb-1">{line.slice(2, -2)}</strong>;
                      }
                      if (line.startsWith('• ')) {
                        return <li key={i} className="ml-4 list-disc">{line.slice(2)}</li>;
                      }
                      return <p key={i} className="mb-1">{line}</p>;
                    })}
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Chat Messages */}
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}

          {/* Loading Indicator */}
          <AnimatePresence>
            {isLoading && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="flex items-start gap-3 mb-4"
              >
                <div className="w-8 h-8 rounded-full gradient-primary flex items-center justify-center flex-shrink-0">
                  <span className="text-white text-xs">AI</span>
                </div>
                <div className="bg-white rounded-2xl rounded-tl-none px-4 py-3 shadow-sm border border-gray-100">
                  <div className="flex items-center gap-1.5">
                    {[...Array(3)].map((_, i) => (
                      <motion.div
                        key={i}
                        className="w-2 h-2 rounded-full bg-blue-400"
                        animate={{ y: [0, -6, 0] }}
                        transition={{
                          duration: 0.6,
                          repeat: Infinity,
                          delay: i * 0.15,
                        }}
                      />
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Questions */}
        <AnimatePresence>
          {suggestedQuestions.length > 0 && !isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="px-6 py-2 border-t border-gray-100 bg-white"
            >
              <p className="text-xs text-gray-500 mb-2">Suggested questions:</p>
              <div className="flex flex-wrap gap-2">
                {suggestedQuestions.map((question, i) => (
                  <button
                    key={i}
                    onClick={() => handleSuggestedQuestion(question)}
                    className="text-xs px-3 py-1.5 bg-blue-50 text-blue-700 rounded-full hover:bg-blue-100 transition-colors border border-blue-200"
                  >
                    {question}
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Input Area */}
        <div className="bg-white border-t border-gray-200 px-6 py-4">
          <div className="flex items-end gap-3">
            <div className="flex-1 bg-gray-50 rounded-2xl border border-gray-200 focus-within:border-blue-400 focus-within:bg-white transition-all">
              <textarea
                ref={inputRef}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type your message or use voice input..."
                className="w-full bg-transparent px-4 py-3 text-sm text-gray-700 resize-none outline-none max-h-32"
                rows={1}
                style={{ minHeight: '44px' }}
              />
            </div>

            <VoiceInput onTranscription={handleVoiceTranscription} />

            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={handleSend}
              disabled={!inputText.trim() || isLoading}
              className={`p-3 rounded-full transition-all ${
                inputText.trim() && !isLoading
                  ? 'gradient-primary text-white shadow-md hover:shadow-lg'
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              }`}
            >
              <Send size={18} />
            </motion.button>
          </div>
        </div>
      </div>

      {/* Right Sidebar - Emotion Panel */}
      <div className="w-72 bg-white border-l border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h2 className="font-semibold text-gray-700 text-sm">Emotional Intelligence</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            Adapting communication to your needs
          </p>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {currentEmotion ? (
            <EmotionDisplay
              emotion={currentEmotion}
              sessionPhase={sessionPhase}
              escalationData={escalationData}
            />
          ) : (
            <div className="text-center py-8">
              <div className="text-4xl mb-3">🤝</div>
              <p className="text-sm text-gray-500">
                Start chatting and I'll adapt my communication style to your emotional state.
              </p>
            </div>
          )}
        </div>

        {/* Bottom Disclaimer */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <p className="text-xs text-gray-400 text-center leading-relaxed">
            ⚕️ Educational purposes only. Not a substitute for professional medical advice.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;
