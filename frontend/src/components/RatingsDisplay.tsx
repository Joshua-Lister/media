import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { ratingsAPI } from '../services/api';

interface Rating {
  id: string;
  user: {
    username: string;
    full_name: string;
    avatar_url?: string;
  };
  rating: number;
  feedback?: string;
  accuracy_rating?: number;
  sources_rating?: number;
  writing_quality_rating?: number;
  originality_rating?: number;
  depth_rating?: number;
  bias_rating?: number;
  created_at: string;
}

interface RatingsDisplayProps {
  articleId: string;
}

const RatingsDisplay: React.FC<RatingsDisplayProps> = ({ articleId }) => {
  const [showCriteriaBreakdown, setShowCriteriaBreakdown] = React.useState(false);

  const { data: ratings = [], isLoading } = useQuery<Rating[]>({
    queryKey: ['ratings', articleId],
    queryFn: async () => {
      const response = await ratingsAPI.list(articleId);
      return response.data;
    },
  });

  const criteriaLabels = {
    accuracy_rating: { label: 'Accuracy', icon: '✓' },
    sources_rating: { label: 'Sources', icon: '📚' },
    writing_quality_rating: { label: 'Writing', icon: '✍️' },
    originality_rating: { label: 'Originality', icon: '💡' },
    depth_rating: { label: 'Depth', icon: '🔍' },
    bias_rating: { label: 'Objectivity', icon: '⚖️' },
  };

  const renderMiniStars = (rating: number) => {
    return (
      <div className="flex gap-0.5">
        {[1, 2, 3, 4, 5].map((star) => (
          <svg
            key={star}
            className={`w-4 h-4 ${star <= rating ? 'text-yellow-400' : 'text-gray-300'}`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        ))}
      </div>
    );
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/4"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (ratings.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-2">Reader Ratings</h3>
        <p className="text-gray-600">No ratings yet. Be the first to rate this article!</p>
      </div>
    );
  }

  // Calculate averages
  const calculateAverage = (key: keyof Rating) => {
    const validRatings = ratings
      .map(r => r[key] as number)
      .filter(r => r != null && r > 0);
    if (validRatings.length === 0) return null;
    return (validRatings.reduce((a, b) => a + b, 0) / validRatings.length).toFixed(1);
  };

  const overallAverage = calculateAverage('rating');

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h3 className="text-2xl font-bold text-gray-900 mb-6">
        Reader Ratings ({ratings.length})
      </h3>

      {/* Overall Average */}
      {overallAverage && (
        <div className="bg-gradient-to-br from-primary-50 to-secondary-50 rounded-lg p-6 mb-6 border border-primary-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-2">Overall Rating</p>
              <div className="flex items-center gap-3">
                <span className="text-5xl font-bold text-gray-900">{overallAverage}</span>
                <div className="flex flex-col">
                  {renderMiniStars(Math.round(parseFloat(overallAverage)))}
                  <span className="text-sm text-gray-500 mt-1">out of 5 stars</span>
                </div>
              </div>
            </div>
            <button
              onClick={() => setShowCriteriaBreakdown(!showCriteriaBreakdown)}
              className="flex items-center gap-2 px-4 py-2 bg-white rounded-lg shadow-sm hover:shadow-md transition-all border border-gray-200"
            >
              <span className="text-sm font-medium text-gray-700">
                {showCriteriaBreakdown ? 'Hide' : 'Show'} Criteria
              </span>
              <svg
                className={`w-5 h-5 text-gray-600 transition-transform ${showCriteriaBreakdown ? 'rotate-180' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>

          {/* Criteria Averages Dropdown */}
          {showCriteriaBreakdown && (
            <div className="mt-6 pt-6 border-t border-primary-200">
              <h4 className="text-sm font-semibold text-gray-700 mb-4">Rating Breakdown by Criteria</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(criteriaLabels).map(([key, { label, icon }]) => {
                  const avg = calculateAverage(key as keyof Rating);
                  if (!avg) return null;
                  const percentage = (parseFloat(avg) / 5) * 100;
                  return (
                    <div key={key} className="bg-white rounded-lg p-4 shadow-sm">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="text-2xl">{icon}</span>
                          <span className="text-sm font-medium text-gray-700">{label}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <span className="text-lg font-bold text-gray-900">{avg}</span>
                          <span className="text-xs text-gray-500">/5</span>
                        </div>
                      </div>
                      {/* Progress Bar */}
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-primary-500 to-secondary-500 h-2 rounded-full transition-all"
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Individual Ratings */}
      <div className="space-y-6">
        {ratings.map((rating) => (
          <div key={rating.id} className="border-b border-gray-200 pb-6 last:border-0">
            {/* User Info */}
            <div className="flex items-center gap-3 mb-4">
              {rating.user.avatar_url ? (
                <img
                  src={rating.user.avatar_url}
                  alt={rating.user.full_name}
                  className="w-10 h-10 rounded-full"
                />
              ) : (
                <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
                  <span className="text-primary-600 font-semibold">
                    {rating.user.full_name?.charAt(0) || '?'}
                  </span>
                </div>
              )}
              <div className="flex-1">
                <p className="font-semibold text-gray-900">{rating.user.full_name}</p>
                <p className="text-sm text-gray-500">@{rating.user.username} · {formatDate(rating.created_at)}</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold text-gray-900">{rating.rating}</span>
                {renderMiniStars(rating.rating)}
              </div>
            </div>

            {/* Criteria Breakdown */}
            {Object.entries(criteriaLabels).some(([key]) => rating[key as keyof Rating]) && (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4 bg-gray-50 rounded-lg p-4">
                {Object.entries(criteriaLabels).map(([key, { label, icon }]) => {
                  const value = rating[key as keyof Rating] as number;
                  if (!value) return null;
                  return (
                    <div key={key} className="flex items-center gap-2">
                      <span className="text-sm">{icon}</span>
                      <div className="flex-1">
                        <p className="text-xs text-gray-600">{label}</p>
                        <div className="flex items-center gap-1">
                          <span className="font-semibold text-sm text-gray-900">{value}</span>
                          <span className="text-xs text-gray-500">/5</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Feedback */}
            {rating.feedback && (
              <p className="text-gray-700 leading-relaxed">{rating.feedback}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default RatingsDisplay;
