import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ratingsAPI } from '../services/api';
import { useAuthStore } from '../store/authStore';

interface MultiCriteriaRatingProps {
  articleId: string;
  onSuccess?: () => void;
}

interface RatingCriteria {
  accuracy_rating: number;
  sources_rating: number;
  writing_quality_rating: number;
  originality_rating: number;
  depth_rating: number;
  bias_rating: number;
}

const MultiCriteriaRating: React.FC<MultiCriteriaRatingProps> = ({ articleId, onSuccess }) => {
  const queryClient = useQueryClient();
  const { isAuthenticated } = useAuthStore();
  const [feedback, setFeedback] = useState('');
  const [ratings, setRatings] = useState<RatingCriteria>({
    accuracy_rating: 0,
    sources_rating: 0,
    writing_quality_rating: 0,
    originality_rating: 0,
    depth_rating: 0,
    bias_rating: 0,
  });

  const criteriaInfo = [
    {
      key: 'accuracy_rating' as keyof RatingCriteria,
      label: 'Accuracy',
      description: 'How factually accurate is the article?',
      icon: '✓',
    },
    {
      key: 'sources_rating' as keyof RatingCriteria,
      label: 'Sources',
      description: 'Quality and reliability of cited sources',
      icon: '📚',
    },
    {
      key: 'writing_quality_rating' as keyof RatingCriteria,
      label: 'Writing Quality',
      description: 'Clarity, grammar, and readability',
      icon: '✍️',
    },
    {
      key: 'originality_rating' as keyof RatingCriteria,
      label: 'Originality',
      description: 'Unique insights and fresh perspective',
      icon: '💡',
    },
    {
      key: 'depth_rating' as keyof RatingCriteria,
      label: 'Depth',
      description: 'Thoroughness of analysis and research',
      icon: '🔍',
    },
    {
      key: 'bias_rating' as keyof RatingCriteria,
      label: 'Objectivity',
      description: 'Balance and lack of bias (5 = unbiased)',
      icon: '⚖️',
    },
  ];

  const submitMutation = useMutation({
    mutationFn: () => {
      // Calculate overall rating as average of all criteria
      const criteriaValues = Object.values(ratings).filter(v => v > 0);
      const overallRating = criteriaValues.length > 0
        ? Math.round(criteriaValues.reduce((a, b) => a + b, 0) / criteriaValues.length)
        : 0;

      return ratingsAPI.create(articleId, {
        rating: overallRating,
        feedback: feedback || undefined,
        ...ratings,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['article', articleId] });
      queryClient.invalidateQueries({ queryKey: ['ratings', articleId] });
      // Reset form
      setRatings({
        accuracy_rating: 0,
        sources_rating: 0,
        writing_quality_rating: 0,
        originality_rating: 0,
        depth_rating: 0,
        bias_rating: 0,
      });
      setFeedback('');
      alert('Thank you! Your rating has been submitted.');
      onSuccess?.();
    },
  });

  const renderStars = (value: number, onChange: (rating: number) => void, disabled: boolean = false) => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onClick={() => !disabled && onChange(star)}
            className={`transition-colors ${disabled ? 'cursor-not-allowed' : 'cursor-pointer hover:scale-110'}`}
            disabled={disabled}
          >
            <svg
              className={`w-8 h-8 ${star <= value ? 'text-yellow-400' : 'text-gray-300'} transition-all`}
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          </button>
        ))}
      </div>
    );
  };

  const hasAnyRating = Object.values(ratings).some(v => v > 0);

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 border-2 border-primary-200">
      <div className="mb-6">
        <h3 className="text-2xl font-bold text-gray-900 mb-2">Rate This Article</h3>
        <p className="text-gray-600">
          Rate the article across 6 quality dimensions. Click the stars to rate.
        </p>
      </div>

      <div className="space-y-6">
        {/* Rating Criteria - ALWAYS VISIBLE */}
        {criteriaInfo.map((criteria) => (
          <div key={criteria.key} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-2xl">{criteria.icon}</span>
                  <h4 className="text-lg font-semibold text-gray-900">{criteria.label}</h4>
                </div>
                <p className="text-sm text-gray-600">{criteria.description}</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              {renderStars(
                ratings[criteria.key],
                (rating) => setRatings({ ...ratings, [criteria.key]: rating }),
                submitMutation.isPending
              )}
              {ratings[criteria.key] > 0 && (
                <span className="text-lg font-bold text-primary-600">
                  {ratings[criteria.key]} / 5
                </span>
              )}
            </div>
          </div>
        ))}

        {/* Feedback */}
        <div>
          <label className="block text-lg font-semibold text-gray-900 mb-2">
            Written Feedback (Optional)
          </label>
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Share your thoughts about this article..."
            rows={4}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            disabled={submitMutation.isPending}
          />
        </div>

        {/* Error Message */}
        {submitMutation.isError && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            Failed to submit rating. Please try again.
          </div>
        )}

        {/* Submit Button */}
        <div className="pt-4">
          {!isAuthenticated ? (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
              <p className="text-yellow-800 text-sm">
                Please <a href="/login" className="font-semibold underline">log in</a> to submit your rating.
              </p>
            </div>
          ) : null}
          <button
            onClick={() => {
              if (!isAuthenticated) {
                alert('Please log in to rate articles');
                return;
              }
              submitMutation.mutate();
            }}
            className="btn btn-primary w-full text-lg py-3"
            disabled={submitMutation.isPending || !hasAnyRating || !isAuthenticated}
          >
            {submitMutation.isPending ? 'Submitting Your Rating...' : 'Submit Rating'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default MultiCriteriaRating;
