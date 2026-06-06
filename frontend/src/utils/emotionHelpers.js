export const EMOTION_CONFIG = {
  anxiety: {
    label: 'Anxious',
    color: '#F59E0B',
    bgColor: '#FEF3C7',
    textColor: '#92400E',
    icon: '😟',
    description: 'Providing calm, reassuring guidance',
    borderColor: '#F59E0B',
  },
  stress: {
    label: 'Stressed',
    color: '#EF4444',
    bgColor: '#FEE2E2',
    textColor: '#991B1B',
    icon: '😤',
    description: 'Offering structured, organized support',
    borderColor: '#EF4444',
  },
  confusion: {
    label: 'Confused',
    color: '#8B5CF6',
    bgColor: '#EDE9FE',
    textColor: '#5B21B6',
    icon: '😕',
    description: 'Explaining with clarity and simplicity',
    borderColor: '#8B5CF6',
  },
  calm: {
    label: 'Calm',
    color: '#10B981',
    bgColor: '#D1FAE5',
    textColor: '#065F46',
    icon: '😌',
    description: 'Providing detailed, comprehensive information',
    borderColor: '#10B981',
  },
  fear: {
    label: 'Fearful',
    color: '#DC2626',
    bgColor: '#FEE2E2',
    textColor: '#7F1D1D',
    icon: '😨',
    description: 'Offering grounding and emotional safety',
    borderColor: '#DC2626',
  },
  sadness: {
    label: 'Sad',
    color: '#6366F1',
    bgColor: '#E0E7FF',
    textColor: '#3730A3',
    icon: '😢',
    description: 'Providing compassionate support',
    borderColor: '#6366F1',
  },
  neutral: {
    label: 'Neutral',
    color: '#94A3B8',
    bgColor: '#F1F5F9',
    textColor: '#475569',
    icon: '😐',
    description: 'Ready to help with your questions',
    borderColor: '#94A3B8',
  },
};

export const getEmotionConfig = (emotion) => {
  return EMOTION_CONFIG[emotion?.toLowerCase()] || EMOTION_CONFIG.neutral;
};

export const getDistressColor = (level) => {
  const colors = {
    low: '#10B981',
    moderate: '#F59E0B',
    high: '#EF4444',
    severe: '#DC2626',
  };
  return colors[level] || colors.low;
};

export const formatConfidence = (confidence) => {
  return `${Math.round(confidence * 100)}%`;
};

export const getSessionPhaseLabel = (phase) => {
  const labels = {
    initial: 'Getting Started',
    assessment: 'Understanding Your Needs',
    explanation: 'Reviewing Your Report',
    support: 'Ongoing Support',
  };
  return labels[phase] || phase;
};
