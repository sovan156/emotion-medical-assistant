import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Heart, TrendingUp, AlertCircle } from 'lucide-react';
import { getEmotionConfig, getDistressColor, getSessionPhaseLabel } from '../../utils/emotionHelpers';

const EmotionDisplay = ({ emotion, sessionPhase, escalationData }) => {
  if (!emotion) return null;

  const config = getEmotionConfig(emotion.primary_emotion);
  const distressColor = getDistressColor(emotion.distress_level);

  return (
    <div className="space-y-3">
      {/* Main Emotion Card */}
      <motion.div
        key={emotion.primary_emotion}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="rounded-xl p-3 border"
        style={{
          backgroundColor: config.bgColor,
          borderColor: config.borderColor + '60',
        }}
      >
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Heart size={14} style={{ color: config.color }} />
            <span className="text-xs font-semibold text-gray-600">Emotional State</span>
          </div>
          <span
            className="text-xs px-2 py-0.5 rounded-full font-medium"
            style={{
              backgroundColor: config.color + '20',
              color: config.textColor,
            }}
          >
            {Math.round(emotion.confidence * 100)}% confidence
          </span>
        </div>

        <div className="flex items-center gap-2 mb-2">
          <span className="text-xl">{config.icon}</span>
          <span className="font-bold text-sm" style={{ color: config.textColor }}>
            {config.label}
          </span>
        </div>

        <p className="text-xs italic" style={{ color: config.textColor + 'CC' }}>
          {config.description}
        </p>

        {/* Distress Bar */}
        <div className="mt-2">
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>Distress Level</span>
            <span className="capitalize font-medium" style={{ color: distressColor }}>
              {emotion.distress_level}
            </span>
          </div>
          <div className="w-full bg-white bg-opacity-60 rounded-full h-1.5">
            <motion.div
              className="h-1.5 rounded-full"
              style={{ backgroundColor: distressColor }}
              initial={{ width: 0 }}
              animate={{
                width: { low: '20%', moderate: '50%', high: '75%', severe: '95%' }[
                  emotion.distress_level
                ],
              }}
              transition={{ duration: 0.6 }}
            />
          </div>
        </div>
      </motion.div>

      {/* Session Phase */}
      <div className="flex items-center gap-2 px-3 py-2 bg-blue-50 rounded-lg">
        <TrendingUp size={14} className="text-blue-500" />
        <span className="text-xs text-blue-700 font-medium">
          {getSessionPhaseLabel(sessionPhase)}
        </span>
      </div>

      {/* Escalation Alert */}
      <AnimatePresence>
        {escalationData?.recommended && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="rounded-xl p-3 bg-red-50 border border-red-200"
          >
            <div className="flex items-start gap-2">
              <AlertCircle size={16} className="text-red-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-xs font-semibold text-red-700 mb-1">
                  Support Recommended
                </p>
                <p className="text-xs text-red-600">
                  Please consider reaching out to a healthcare professional or trusted person.
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Emotion Score Details */}
      <div className="space-y-1.5 px-1">
        {Object.entries(emotion.all_scores)
          .filter(([, score]) => score > 0.05)
          .sort(([, a], [, b]) => b - a)
          .slice(0, 4)
          .map(([key, score]) => {
            const ec = getEmotionConfig(key);
            return (
              <div key={key} className="flex items-center gap-2">
                <span className="text-xs w-16 text-gray-500 capitalize truncate">{key}</span>
                <div className="flex-1 bg-gray-100 rounded-full h-1.5">
                  <motion.div
                    className="h-1.5 rounded-full"
                    style={{ backgroundColor: ec.color }}
                    initial={{ width: 0 }}
                    animate={{ width: `${score * 100}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
                <span className="text-xs text-gray-400 w-8 text-right">
                  {Math.round(score * 100)}%
                </span>
              </div>
            );
          })}
      </div>
    </div>
  );
};

export default EmotionDisplay;
