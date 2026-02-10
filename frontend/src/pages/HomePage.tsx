import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { articlesAPI } from '../services/api';

interface Article {
  id: string;
  title: string;
  slug: string;
  summary: string;
  author: {
    full_name: string;
    username: string;
  };
  category: string;
  cover_image_url?: string;
  reading_time_minutes: number;
  view_count: number;
  average_rating: number;
  rating_count: number;
  published_at: string;
}

const HomePage: React.FC = () => {
  const [filter, setFilter] = useState<'recent' | 'top_rated' | 'trending'>('recent');

  // Fetch articles
  const { data: articles = [], isLoading } = useQuery<Article[]>({
    queryKey: ['articles', filter],
    queryFn: async () => {
      const response = await articlesAPI.list();
      let sortedArticles = response.data;

      // Sort based on filter
      if (filter === 'top_rated') {
        sortedArticles = sortedArticles.sort((a: Article, b: Article) => b.average_rating - a.average_rating);
      } else if (filter === 'trending') {
        sortedArticles = sortedArticles.sort((a: Article, b: Article) => b.view_count - a.view_count);
      } else {
        sortedArticles = sortedArticles.sort((a: Article, b: Article) =>
          new Date(b.published_at).getTime() - new Date(a.published_at).getTime()
        );
      }

      return sortedArticles.slice(0, 6); // Show top 6
    },
  });

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center">
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

  return (
    <div className="bg-gradient-to-b from-primary-50 via-white to-gray-50">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Empowering Citizen Journalism
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            A platform where readers vote on important topics and writers create
            compelling content. Join our community of truth-seekers and storytellers.
          </p>
          <div className="flex justify-center space-x-4">
            <Link to="/register" className="btn btn-primary text-lg px-8 py-3">
              Get Started
            </Link>
            <Link to="/articles" className="btn btn-secondary text-lg px-8 py-3">
              Browse Articles
            </Link>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="card text-center">
            <div className="text-4xl mb-4">📝</div>
            <h3 className="text-xl font-bold mb-2">Vote on Topics</h3>
            <p className="text-gray-600">
              Community members propose and vote on important topics that need coverage.
            </p>
          </div>
          <div className="card text-center">
            <div className="text-4xl mb-4">✍️</div>
            <h3 className="text-xl font-bold mb-2">Writers Create</h3>
            <p className="text-gray-600">
              Verified writers research and create in-depth articles on trending topics.
            </p>
          </div>
          <div className="card text-center">
            <div className="text-4xl mb-4">⭐</div>
            <h3 className="text-xl font-bold mb-2">Rate & Support</h3>
            <p className="text-gray-600">
              Readers rate articles and support their favorite writers directly.
            </p>
          </div>
        </div>
      </div>

      {/* Featured Articles Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-3xl font-bold text-gray-900">Featured Articles</h2>
          <Link to="/articles" className="text-primary-600 hover:text-primary-700 font-medium">
            View All →
          </Link>
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-2 mb-8 border-b border-gray-200">
          <button
            onClick={() => setFilter('recent')}
            className={`px-6 py-3 font-medium transition-colors border-b-2 ${
              filter === 'recent'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            🕒 Recent
          </button>
          <button
            onClick={() => setFilter('top_rated')}
            className={`px-6 py-3 font-medium transition-colors border-b-2 ${
              filter === 'top_rated'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            ⭐ Top Rated
          </button>
          <button
            onClick={() => setFilter('trending')}
            className={`px-6 py-3 font-medium transition-colors border-b-2 ${
              filter === 'trending'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            🔥 Trending
          </button>
        </div>

        {/* Articles Grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="bg-white rounded-lg shadow-sm p-6 animate-pulse">
                <div className="h-48 bg-gray-200 rounded-lg mb-4"></div>
                <div className="h-6 bg-gray-200 rounded mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              </div>
            ))}
          </div>
        ) : articles.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600">No articles available yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {articles.map((article) => (
              <Link
                key={article.id}
                to={`/articles/${article.slug}`}
                className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow overflow-hidden group"
              >
                {/* Cover Image */}
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
                  {/* Category Badge */}
                  <span className="badge badge-primary text-xs mb-3">{article.category}</span>

                  {/* Title */}
                  <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors line-clamp-2">
                    {article.title}
                  </h3>

                  {/* Summary */}
                  <p className="text-gray-600 text-sm mb-4 line-clamp-3">{article.summary}</p>

                  {/* Author & Meta */}
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span className="font-medium text-gray-700">{article.author.full_name}</span>
                    <span>{article.reading_time_minutes} min read</span>
                  </div>

                  {/* Rating & Stats */}
                  <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
                    <div className="flex items-center gap-2">
                      {renderStars(Math.round(article.average_rating))}
                      <span className="text-sm font-medium text-gray-700">
                        {article.average_rating.toFixed(1)}
                      </span>
                      <span className="text-xs text-gray-500">({article.rating_count})</span>
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

export default HomePage;
