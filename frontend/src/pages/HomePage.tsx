import React from 'react';
import { Link } from 'react-router-dom';

const HomePage: React.FC = () => {
  return (
    <div className="bg-gradient-to-b from-primary-50 to-white">
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
    </div>
  );
};

export default HomePage;
