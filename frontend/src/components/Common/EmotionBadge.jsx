import React from 'react';
import { motion } from 'framer-motion';
import { getEmotionConfig, formatConfidence, getDistressColor } from '../../utils/emotionHelpers';

const EmotionBadge = ({ emotion, compact = false }) => {
  if (!emotion) return null;

  const config = getEmotionConfig(emotion.primary_emotion);
  const distressColor = getDistressColor(emotion.distress_level);

  if (compact) {
    return (
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium"
        style={{
          backgroundColor: config.bgColor,
          color: config.textColor,
          border: `1px solid ${config.color}`,
        }}
      >
        <span>{config.icon}</span>
        <span>{config.label}</span>
        <span className="opacity-70">{formatConfidence(emotion.confidence)}</span>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ y: -10, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="rounded-2xl p-4 border"
      style={{
        backgroundColor: config.bgColor,
        borderColor: config.borderColor,
      }}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{config.icon}</span>
          <div>
            <p className="font-semibold text-sm" style={{ color: config.textColor }}>
              Emotional State
            </p>
            <p className="font-bold text-base" style={{ color: config.textColor }}>
              {config.label}
            </p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-xs font-medium opacity-70" style={{ color: config.textColor }}>
            Confidence
          </p>
          <p className="font-bold text-lg" style={{ color: config.color }}>
            {formatConfidence(emotion.confidence)}
          </p>
        </div>
      </div>

      <p className="text-xs italic mb-3" style={{ color: config.textColor }}>
        {config.description}
      </p>

      {/* Distress Level Indicator */}
      <div className="space-y-1">
        <div className="flex justify-between text-xs" style={{ color: config.textColor }}>
          <span>Distress Level</span>
          <span className="font-semibold capitalize">{emotion.distress_level}</span>
        </div>
        <div className="w-full bg-white bg-opacity-50 rounded-full h-1.5">
          <motion.div
            className="h-1.5 rounded-full"
            style={{ backgroundColor: distressColor }}
            initial={{ width: 0 }}
            animate={{
              width: {
                low: '20%',
                moderate: '50%',
                high: '75%',
                severe: '95%',
              }[emotion.distress_level] || '20%',
            }}
            transition={{ duration: 0.5, delay: 0.2 }}
          />
        </div>
      </div>

      {/* Emotion Score Breakdown */}
      <div className="mt-3 space-y-1">
        {Object.entries(emotion.all_scores)
          .sort(([, a], [, b]) => b - a)
          .slice(0, 3)
          .map(([emotion_key, score]) => (
            <div key={emotion_key} className="flex items-center gap-2">
              <span className="text-xs capitalize w-16" style={{ color: config.textColor }}>
                {emotion_key}
              </span>
              <div className="flex-1 bg-white bg-opacity-40 rounded-full h-1">
                <motion.div
                  className="h-1 rounded-full"
                  style={{ backgroundColor: getEmotionConfig(emotion_key).color }}
                  initial={{ width: 0 }}
                  animate={{ width: `${score * 100}%` }}
                  transition={{ duration: 0.4, delay: 0.1 }}
                />
              </div>
              <span className="text-xs font-medium w-8" style={{ color: config.textColor }}>
                {Math.round(score * 100)}%
              </span>
            </div>
          ))}
      </div>
    </motion.div>
  );
};

export default EmotionBadge;
