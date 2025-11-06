import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { mockArticles } from '../utils/mockData';
import MultiCriteriaRating from '../components/MultiCriteriaRating';
import RatingsDisplay from '../components/RatingsDisplay';
import ArticleAnnotations from '../components/ArticleAnnotations';

const ArticleDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  // Find article by slug (using mock data for now)
  const article = mockArticles.find(a => a.slug === id);

  if (!article) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Article Not Found</h1>
        <p className="text-gray-600 mb-8">The article you're looking for doesn't exist.</p>
        <Link to="/articles" className="btn btn-primary">
          Browse All Articles
        </Link>
      </div>
    );
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  };

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
        <span className="ml-2 text-lg font-medium text-gray-700">
          {article.average_rating.toFixed(1)}
        </span>
        <span className="ml-1 text-sm text-gray-500">
          ({article.rating_count} ratings)
        </span>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Article Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Breadcrumb */}
          <nav className="mb-4">
            <Link to="/articles" className="text-primary-600 hover:text-primary-700">
              ← Back to Articles
            </Link>
          </nav>

          {/* Category */}
          <span className="badge badge-primary mb-3 text-sm">{article.category}</span>

          {/* Title */}
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4 leading-tight">
            {article.title}
          </h1>

          {/* Summary */}
          <p className="text-xl text-gray-600 mb-6 leading-relaxed">
            {article.summary}
          </p>

          {/* Author Info */}
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center">
              <img
                src={article.author.avatar_url}
                alt={article.author.full_name}
                className="w-12 h-12 rounded-full mr-3"
              />
              <div>
                <Link
                  to={`/writers/${article.author.username}`}
                  className="font-semibold text-gray-900 hover:text-primary-600"
                >
                  {article.author.full_name}
                </Link>
                <div className="text-sm text-gray-500">
                  {formatDate(article.published_at)} · {article.reading_time_minutes} min read
                </div>
              </div>
            </div>

            {/* Stats */}
            <div className="flex items-center gap-6 text-sm text-gray-600">
              <div className="flex items-center">
                <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                {article.view_count.toLocaleString()} views
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Article Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-lg shadow-sm p-8 md:p-12">
          {/* Cover Image */}
          {article.cover_image_url && (
            <img
              src={article.cover_image_url}
              alt={article.title}
              className="w-full h-96 object-cover rounded-lg mb-8"
            />
          )}

          {/* Article Body with Annotations */}
          <ArticleAnnotations articleId={article.id} content={article.content} />

          {/* Tags */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <div className="flex flex-wrap gap-2">
              {article.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                >
                  #{tag}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Ratings Display */}
        <div className="mt-6">
          <RatingsDisplay articleId={article.id} />
        </div>

        {/* Rating Form */}
        <div className="mt-6">
          <MultiCriteriaRating articleId={article.id} />
        </div>

        {/* Support Writer */}
        <div className="bg-gradient-to-r from-primary-50 to-secondary-50 rounded-lg shadow-sm p-8 mt-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center">
              <img
                src={article.author.avatar_url}
                alt={article.author.full_name}
                className="w-16 h-16 rounded-full mr-4"
              />
              <div>
                <h3 className="text-xl font-bold text-gray-900">
                  Enjoyed this article?
                </h3>
                <p className="text-gray-600">
                  Support {article.author.full_name} and help them create more great content.
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <button className="btn btn-primary">
                ❤️ Donate
              </button>
              <button className="btn btn-secondary">
                Follow Writer
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArticleDetailPage;
