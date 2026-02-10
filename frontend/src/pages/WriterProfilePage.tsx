import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { usersAPI, articlesAPI } from '../services/api';

const WriterProfilePage: React.FC = () => {
  const { username } = useParams<{ username: string }>();

  // Fetch writer profile
  const { data: writer, isLoading: loadingWriter } = useQuery({
    queryKey: ['writer', username],
    queryFn: async () => {
      // TODO: Create API endpoint for fetching writer by username
      // For now, return mock data
      return {
        id: '1',
        username: username,
        full_name: 'Jane Writer',
        bio: 'Investigative journalist focused on local government, education, and environmental issues. Former newspaper reporter with 10 years of experience.',
        avatar_url: `https://ui-avatars.com/api/?name=${username}&background=0ea5e9&color=fff&size=200`,
        is_writer: true,
        created_at: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString(), // 1 year ago
        article_count: 24,
        total_views: 15420,
        average_rating: 4.6,
        total_ratings: 142,
      };
    },
  });

  // Fetch writer's articles
  const { data: articles = [], isLoading: loadingArticles } = useQuery({
    queryKey: ['writer-articles', username],
    queryFn: async () => {
      const response = await articlesAPI.list();
      // Filter by writer - in real implementation, this would be server-side
      return response.data;
    },
  });

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

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays < 30) {
      return `${diffDays} days ago`;
    } else if (diffDays < 365) {
      const months = Math.floor(diffDays / 30);
      return `${months} month${months > 1 ? 's' : ''} ago`;
    } else {
      const years = Math.floor(diffDays / 365);
      return `${years} year${years > 1 ? 's' : ''} ago`;
    }
  };

  if (loadingWriter) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading writer profile...</p>
        </div>
      </div>
    );
  }

  if (!writer) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Writer Not Found</h1>
          <p className="text-gray-600 mb-8">The writer you're looking for doesn't exist.</p>
          <Link to="/articles" className="btn btn-primary">
            Browse Articles
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-start gap-8">
            {/* Avatar */}
            {writer.avatar_url ? (
              <img
                src={writer.avatar_url}
                alt={writer.full_name}
                className="w-32 h-32 rounded-full border-4 border-primary-100"
              />
            ) : (
              <div className="w-32 h-32 rounded-full bg-primary-600 flex items-center justify-center border-4 border-primary-100">
                <span className="text-white text-5xl font-bold">
                  {writer.full_name?.charAt(0) || '?'}
                </span>
              </div>
            )}

            {/* Info */}
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-4xl font-bold text-gray-900">{writer.full_name}</h1>
                <span className="badge badge-primary">Verified Writer</span>
              </div>
              <p className="text-xl text-gray-600 mb-4">@{writer.username}</p>

              {/* Bio */}
              <p className="text-gray-700 mb-6 max-w-3xl">{writer.bio}</p>

              {/* Stats */}
              <div className="flex items-center gap-8 mb-6">
                <div>
                  <p className="text-2xl font-bold text-gray-900">{writer.article_count}</p>
                  <p className="text-sm text-gray-600">Articles Published</p>
                </div>
                <div className="h-12 w-px bg-gray-300"></div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{writer.total_views.toLocaleString()}</p>
                  <p className="text-sm text-gray-600">Total Views</p>
                </div>
                <div className="h-12 w-px bg-gray-300"></div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Writer Rating</p>
                  <div className="flex items-center gap-2">
                    {renderStars(Math.round(writer.average_rating))}
                    <span className="text-lg font-bold text-gray-900">{writer.average_rating.toFixed(1)}</span>
                    <span className="text-sm text-gray-500">({writer.total_ratings})</span>
                  </div>
                </div>
              </div>

              {/* Member Since */}
              <p className="text-sm text-gray-500">
                Member since {formatDate(writer.created_at)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Articles Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h2 className="text-3xl font-bold text-gray-900 mb-8">Published Articles</h2>

        {loadingArticles ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-white rounded-lg shadow-sm p-6 animate-pulse">
                <div className="h-48 bg-gray-200 rounded-lg mb-4"></div>
                <div className="h-6 bg-gray-200 rounded mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              </div>
            ))}
          </div>
        ) : articles.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow-sm">
            <p className="text-gray-600">No articles published yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {articles.map((article: any) => (
              <Link
                key={article.id}
                to={`/articles/${article.slug}`}
                className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow overflow-hidden group"
              >
                {article.cover_image_url && (
                  <div className="h-48 overflow-hidden">
                    <img
                      src={article.cover_image_url}
                      alt={article.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  </div>
                )}

                <div className="p-6">
                  <span className="badge badge-primary text-xs mb-3">{article.category}</span>
                  <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors line-clamp-2">
                    {article.title}
                  </h3>
                  <p className="text-gray-600 text-sm mb-4 line-clamp-3">{article.summary}</p>

                  <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                    <div className="flex items-center gap-2">
                      {renderStars(Math.round(article.average_rating))}
                      <span className="text-sm font-medium text-gray-700">
                        {article.average_rating.toFixed(1)}
                      </span>
                    </div>
                    <div className="flex items-center gap-1 text-gray-500 text-sm">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                        />
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                        />
                      </svg>
                      <span>{article.view_count.toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default WriterProfilePage;
