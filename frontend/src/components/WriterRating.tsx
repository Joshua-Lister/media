import React, { useState } from 'react';
import { Link } from 'react-router-dom';

interface WriterRatingProps {
  writer: {
    id: string;
    username: string;
    full_name: string;
    avatar_url?: string;
  };
  averageRating?: number;
  totalRatings?: number;
}

const WriterRating: React.FC<WriterRatingProps> = ({ writer, averageRating = 0, totalRatings = 0 }) => {
  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center">
        {[1, 2, 3, 4, 5].map((star) => (
          <svg
            key={star}
            className={`w-5 h-5 ${star <= rating ? 'text-yellow-400' : 'text-gray-300'}`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        ))}
      </div>
    );
  };

  return (
    <div className="bg-gradient-to-r from-primary-50 to-secondary-50 rounded-lg shadow-sm p-6 border border-primary-200">
      <div className="flex items-center gap-6">
        {/* Writer Avatar */}
        <Link to={`/writers/${writer.username}`}>
          {writer.avatar_url ? (
            <img
              src={writer.avatar_url}
              alt={writer.full_name}
              className="w-24 h-24 rounded-full border-4 border-white shadow-lg hover:scale-105 transition-transform"
            />
          ) : (
            <div className="w-24 h-24 rounded-full bg-primary-600 flex items-center justify-center border-4 border-white shadow-lg hover:scale-105 transition-transform">
              <span className="text-white text-3xl font-bold">
                {writer.full_name?.charAt(0) || '?'}
              </span>
            </div>
          )}
        </Link>

        {/* Writer Info */}
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <Link
              to={`/writers/${writer.username}`}
              className="text-2xl font-bold text-gray-900 hover:text-primary-600 transition-colors"
            >
              {writer.full_name}
            </Link>
            <span className="badge badge-primary">Writer</span>
          </div>

          <Link
            to={`/writers/${writer.username}`}
            className="text-gray-600 hover:text-primary-600 mb-3 block"
          >
            @{writer.username}
          </Link>

          {/* Writer Rating */}
          <div className="flex items-center gap-4">
            <div>
              <p className="text-xs text-gray-600 mb-1">Writer Rating</p>
              <div className="flex items-center gap-2">
                {renderStars(Math.round(averageRating))}
                <span className="text-lg font-bold text-gray-900 ml-2">
                  {averageRating > 0 ? averageRating.toFixed(1) : 'Not rated yet'}
                </span>
                {totalRatings > 0 && (
                  <span className="text-sm text-gray-500">({totalRatings} ratings)</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* View Profile Button */}
        <div>
          <Link
            to={`/writers/${writer.username}`}
            className="btn btn-primary"
          >
            View Profile
          </Link>
        </div>
      </div>
    </div>
  );
};

export default WriterRating;
