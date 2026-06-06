import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Volume2, VolumeX, Clock } from 'lucide-react';
import { format } from 'date-fns';
import { ttsService } from '../../services/tts';
import { getEmotionConfig } from '../../utils/emotionHelpers';
import { useChat } from '../../contexts/ChatContext';

const MessageBubble = ({ message }) => {
  const { language } = useChat();
  const [isSpeaking, setIsSpeaking] = useState(false);
  const isUser = message.role === 'user';
  const emotion = message.emotion;

  const handleSpeak = () => {
    if (isSpeaking) {
      ttsService.stop();
      setIsSpeaking(false);
    } else {
      ttsService.speak(message.content, language, {
        onStart: () => setIsSpeaking(true),
        onEnd: () => setIsSpeaking(false),
        onError: () => setIsSpeaking(false),
      });
    }
  };

  const formatContent = (content) => {
    // Simple markdown-like formatting
    return content
      .split('\n')
      .map((line, i) => {
        if (line.startsWith('**') && line.endsWith('**')) {
          return (
            <strong key={i} className="block font-semibold">
              {line.slice(2, -2)}
            </strong>
          );
        }
        if (line.startsWith('• ') || line.startsWith('- ')) {
          return (
            <li key={i} className="ml-4 list-disc">
              {line.slice(2)}
            </li>
          );
        }
        if (line.startsWith('---')) {
          return <hr key={i} className="my-3 border-current opacity-20" />;
        }
        if (line.trim() === '') {
          return <br key={i} />;
        }
        return <p key={i} className="mb-1">{line}</p>;
      });
  };

  return (
    <motion.div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 message-enter`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
    >
      {!isUser && (
        <div className="w-8 h-8 rounded-full gradient-primary flex items-center justify-center mr-2 mt-1 flex-shrink-0">
          <span className="text-white text-xs font-bold">AI</span>
        </div>
      )}

      <div className={`max-w-[75%] ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
        {/* Emotion Badge for user messages */}
        {isUser && emotion && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-1 self-end"
          >
            <span
              className="text-xs px-2 py-0.5 rounded-full"
              style={{
                backgroundColor: getEmotionConfig(emotion.primary_emotion).bgColor,
                color: getEmotionConfig(emotion.primary_emotion).textColor,
              }}
            >
              {getEmotionConfig(emotion.primary_emotion).icon}{' '}
              {getEmotionConfig(emotion.primary_emotion).label}
            </span>
          </motion.div>
        )}

        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? 'gradient-primary text-white rounded-tr-none'
              : 'bg-white shadow-sm border border-gray-100 rounded-tl-none'
          }`}
          style={{ maxWidth: '100%' }}
        >
          {/* Voice indicator */}
          {message.isVoice && (
            <div className="flex items-center gap-1 mb-2 text-xs opacity-70">
              <Volume2 size={12} />
              <span>Voice message</span>
            </div>
          )}

          {/* Message content */}
          <div
            className={`text-sm leading-relaxed ${
              isUser ? 'text-white' : 'text-gray-700'
            }`}
          >
            {formatContent(message.content)}
          </div>
        </div>

        {/* Message actions and timestamp */}
        <div
          className={`flex items-center gap-2 mt-1 ${
            isUser ? 'flex-row-reverse' : 'flex-row'
          }`}
        >
          <span className="text-xs text-gray-400 flex items-center gap-1">
            <Clock size={10} />
            {message.timestamp
              ? format(new Date(message.timestamp), 'HH:mm')
              : format(new Date(), 'HH:mm')}
          </span>

          {/* TTS button for assistant messages */}
          {!isUser && (
            <button
              onClick={handleSpeak}
              className="p-1 rounded-full hover:bg-gray-100 transition-colors"
              title={isSpeaking ? 'Stop speaking' : 'Read aloud'}
            >
              {isSpeaking ? (
                <VolumeX size={14} className="text-blue-500" />
              ) : (
                <Volume2 size={14} className="text-gray-400 hover:text-blue-500" />
              )}
            </button>
          )}
        </div>
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center ml-2 mt-1 flex-shrink-0">
          <span className="text-gray-600 text-xs font-bold">You</span>
        </div>
      )}
    </motion.div>
  );
};

export default MessageBubble;
