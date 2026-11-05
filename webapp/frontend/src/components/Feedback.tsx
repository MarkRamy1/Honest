import React from 'react';
import { Icon } from './Icon';

export interface FeedbackProps {
  readonly message: string;
  readonly loading?: boolean;
  readonly onRetry?: () => void;
}

export function Feedback({ message, loading = false, onRetry }: Readonly<FeedbackProps>) {
  return (
    <div className={`feedback ${loading ? 'loading' : 'error'}`} role={loading ? 'status' : 'alert'}>
      <Icon name={loading ? 'loading' : 'alert'} className={loading ? 'spin' : ''} size={18} />
      <span>{message}</span>
      {onRetry && (
        <button className="text-button" onClick={onRetry}>
          Retry
        </button>
      )}
    </div>
  );
}
