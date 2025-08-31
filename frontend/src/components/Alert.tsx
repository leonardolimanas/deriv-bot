import React from 'react';
import { AlertCircle, CheckCircle, Info, X, AlertTriangle } from 'lucide-react';

interface AlertProps {
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  onClose?: () => void;
}

export const Alert: React.FC<AlertProps> = ({ message, type, onClose }) => {
  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5" />;
      case 'error':
        return <AlertCircle className="w-5 h-5" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5" />;
      case 'info':
        return <Info className="w-5 h-5" />;
    }
  };

  const getStyles = () => {
    switch (type) {
      case 'success':
        return 'bg-gradient-to-r from-green-500/20 to-emerald-500/20 border-green-500/30 text-green-300';
      case 'error':
        return 'bg-gradient-to-r from-red-500/20 to-pink-500/20 border-red-500/30 text-red-300';
      case 'warning':
        return 'bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border-yellow-500/30 text-yellow-300';
      case 'info':
        return 'bg-gradient-to-r from-blue-500/20 to-indigo-500/20 border-blue-500/30 text-blue-300';
    }
  };

  const getIconStyles = () => {
    switch (type) {
      case 'success':
        return 'bg-green-500/20 text-green-400';
      case 'error':
        return 'bg-red-500/20 text-red-400';
      case 'warning':
        return 'bg-yellow-500/20 text-yellow-400';
      case 'info':
        return 'bg-blue-500/20 text-blue-400';
    }
  };

  return (
    <div className={`rounded-xl border ${getStyles()} backdrop-blur-sm`}>
      <div className="flex items-start p-4">
        <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${getIconStyles()}`}>
          {getIcon()}
        </div>
        <div className="flex-1 ml-3">
          <p className="text-sm font-medium">{message}</p>
        </div>
        {onClose && (
          <div className="flex-shrink-0 ml-3">
            <button
              onClick={onClose}
              className="inline-flex text-gray-400 hover:text-white hover:bg-white/10 rounded-lg p-1 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
