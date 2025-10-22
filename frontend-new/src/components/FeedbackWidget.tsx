import React, { useState } from 'react';
import { MessageSquare, X, Send, Star } from 'lucide-react';
import { AccessibleButton } from './AccessibleButton';
import { notify } from '../utils/toast';

export const FeedbackWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [rating, setRating] = useState(0);
  const [feedback, setFeedback] = useState('');
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!feedback.trim()) {
      notify.error('Please provide feedback');
      return;
    }

    setIsSubmitting(true);

    try {
      // Send feedback to API
      await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          rating,
          feedback: feedback.trim(),
          email: email.trim() || null,
          url: window.location.href,
          userAgent: navigator.userAgent,
          timestamp: new Date().toISOString(),
        }),
      });

      notify.success('Thank you for your feedback!');
      setIsOpen(false);
      setRating(0);
      setFeedback('');
      setEmail('');
    } catch (error) {
      notify.error('Failed to submit feedback');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 right-4 p-4 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-all hover:scale-110 z-50"
        aria-label="Send feedback"
      >
        <MessageSquare className="w-6 h-6" />
      </button>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 w-96 bg-white dark:bg-gray-800 rounded-2xl shadow-2xl z-50 border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-blue-600" />
          <h3 className="font-semibold text-gray-900 dark:text-white">
            Send Feedback
          </h3>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          aria-label="Close"
        >
          <X className="w-5 h-5 text-gray-500" />
        </button>
      </div>

      {/* Body */}
      <form onSubmit={handleSubmit} className="p-4 space-y-4">
        {/* Rating */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            How would you rate your experience?
          </label>
          <div className="flex gap-2">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                onClick={() => setRating(star)}
                className="p-1 hover:scale-110 transition-transform"
              >
                <Star
                  className={`w-8 h-8 ${
                    star <= rating
                      ? 'fill-yellow-400 text-yellow-400'
                      : 'text-gray-300 dark:text-gray-600'
                  }`}
                />
              </button>
            ))}
          </div>
        </div>

        {/* Feedback */}
        <div>
          <label
            htmlFor="feedback-text"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
          >
            Your feedback *
          </label>
          <textarea
            id="feedback-text"
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Tell us what you think..."
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400"
            rows={4}
            required
          />
        </div>

        {/* Email */}
        <div>
          <label
            htmlFor="feedback-email"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
          >
            Email (optional)
          </label>
          <input
            id="feedback-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400"
          />
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            We'll only use this to follow up on your feedback
          </p>
        </div>

        {/* Submit */}
        <AccessibleButton
          type="submit"
          variant="primary"
          className="w-full"
          isLoading={isSubmitting}
          leftIcon={<Send className="w-4 h-4" />}
        >
          Send Feedback
        </AccessibleButton>
      </form>
    </div>
  );
};

export default FeedbackWidget;
