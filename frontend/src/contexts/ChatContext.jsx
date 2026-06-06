import React, { createContext, useContext, useState, useCallback } from 'react';
import { chatAPI, reportAPI, voiceAPI } from '../services/api';
import toast from 'react-hot-toast';

const ChatContext = createContext(null);

export const ChatProvider = ({ children }) => {
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [currentEmotion, setCurrentEmotion] = useState(null);
  const [sessionPhase, setSessionPhase] = useState('initial');
  const [isLoading, setIsLoading] = useState(false);
  const [reportData, setReportData] = useState(null);
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);
  const [escalationData, setEscalationData] = useState(null);
  const [language, setLanguage] = useState('en');

  const addMessage = useCallback((role, content, extra = {}) => {
    const message = {
      id: Date.now().toString(),
      role,
      content,
      timestamp: new Date(),
      ...extra,
    };
    setMessages((prev) => [...prev, message]);
    return message;
  }, []);

  const sendMessage = useCallback(
    async (text, isVoice = false) => {
      if (!text.trim()) return;

      // Add user message immediately
      addMessage('user', text, { isVoice });
      setIsLoading(true);

      try {
        const response = await chatAPI.sendMessage({
          conversation_id: conversationId,
          message: text,
          language,
          is_voice: isVoice,
          report_id: reportData?.report_id || null,
        });

        const data = response.data;

        // Update conversation ID
        if (!conversationId) {
          setConversationId(data.conversation_id);
        }

        // Update emotion state
        if (data.emotion_analysis) {
          setCurrentEmotion(data.emotion_analysis);
        }

        // Update session phase
        setSessionPhase(data.session_phase);

        // Update suggested questions
        setSuggestedQuestions(data.suggested_next_questions || []);

        // Handle escalation
        if (data.escalation_recommended) {
          setEscalationData({
            message: data.escalation_message,
            recommended: true,
          });
        }

        // Add assistant message
        addMessage('assistant', data.message.content, {
          emotion: data.emotion_analysis,
          sessionPhase: data.session_phase,
        });
      } catch (error) {
        toast.error('Failed to send message. Please try again.');
        console.error('Send message error:', error);
      } finally {
        setIsLoading(false);
      }
    },
    [conversationId, language, reportData, addMessage]
  );

  const uploadReport = useCallback(
    async (file) => {
      setIsLoading(true);
      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('language', language);

        const response = await reportAPI.upload(formData);
        const data = response.data;

        setReportData(data);

        // Add system message about the report
        addMessage('assistant', data.message);

        toast.success('Report uploaded successfully!');
        return data;
      } catch (error) {
        const message = error.response?.data?.detail || 'Failed to upload report';
        toast.error(message);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [language, addMessage]
  );

  const transcribeAudio = useCallback(
    async (audioBlob) => {
      try {
        const formData = new FormData();
        formData.append('audio_file', audioBlob, 'recording.wav');
        formData.append('language', language);

        const response = await voiceAPI.transcribe(formData);
        return response.data;
      } catch (error) {
        toast.error('Failed to transcribe audio');
        return null;
      }
    },
    [language]
  );

  const resetConversation = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setCurrentEmotion(null);
    setSessionPhase('initial');
    setReportData(null);
    setSuggestedQuestions([]);
    setEscalationData(null);
  }, []);

  return (
    <ChatContext.Provider
      value={{
        messages,
        conversationId,
        currentEmotion,
        sessionPhase,
        isLoading,
        reportData,
        suggestedQuestions,
        escalationData,
        language,
        setLanguage,
        sendMessage,
        uploadReport,
        transcribeAudio,
        resetConversation,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) throw new Error('useChat must be used within ChatProvider');
  return context;
};
