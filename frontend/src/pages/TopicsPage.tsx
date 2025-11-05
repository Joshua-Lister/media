import React, { useState } from 'react';
import { mockTopics } from '../utils/mockData';

const TopicsPage: React.FC = () => {
  const [topics] = useState(mockTopics);
  const [votedTopics, setVotedTopics] = useState<Set<string>>(new Set());

  const handleVote = (topicId: string, voteType: 'up' | 'down') => {
    // Mock voting logic
    setVotedTopics(prev => new Set(prev).add(topicId));
    console.log(`Voted ${voteType} on topic ${topicId}`);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Community Topics</h1>
          <p className="text-lg text-gray-600">
            Vote on topics you want to see covered by our community of writers
          </p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Propose Topic Button */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-1">Trending Topics</h2>
            <p className="text-gray-600">Help prioritize what gets written next</p>
          </div>
          <button className="btn btn-primary">
            + Propose Topic
          </button>
        </div>

        {/* Topics List */}
        <div className="space-y-4">
          {topics.map((topic, index) => (
            <div key={topic.id} className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow">
              <div className="flex gap-4">
                {/* Voting */}
                <div className="flex flex-col items-center">
                  <button
                    onClick={() => handleVote(topic.id, 'up')}
                    className={`p-2 rounded hover:bg-gray-100 transition-colors ${
                      votedTopics.has(topic.id) ? 'text-primary-600' : 'text-gray-400'
                    }`}
                    disabled={votedTopics.has(topic.id)}
                  >
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clipRule="evenodd" />
                    </svg>
                  </button>
                  <span className="text-xl font-bold text-gray-900 my-1">
                    {topic.vote_score}
                  </span>
                  <button
                    onClick={() => handleVote(topic.id, 'down')}
                    className="p-2 rounded hover:bg-gray-100 transition-colors text-gray-400"
                    disabled={votedTopics.has(topic.id)}
                  >
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>

                {/* Content */}
                <div className="flex-1">
                  {/* Rank and Category */}
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-sm font-bold text-gray-500">#{index + 1}</span>
                    <span className="badge badge-secondary text-xs">{topic.category}</span>
                  </div>

                  {/* Title */}
                  <h3 className="text-xl font-bold text-gray-900 mb-2">
                    {topic.title}
                  </h3>

                  {/* Description */}
                  <p className="text-gray-600 mb-4">
                    {topic.description}
                  </p>

                  {/* Meta Info */}
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center gap-4">
                      <span>
                        Proposed by <span className="font-medium text-gray-700">{topic.proposed_by.username}</span>
                      </span>
                      <span>•</span>
                      <span>{formatDate(topic.created_at)}</span>
                    </div>

                    {/* Vote Stats */}
                    <div className="flex items-center gap-3">
                      <span className="flex items-center text-green-600">
                        <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clipRule="evenodd" />
                        </svg>
                        {topic.upvotes}
                      </span>
                      <span className="flex items-center text-red-600">
                        <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                        {topic.downvotes}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Info Card */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-bold text-blue-900 mb-2">How Topic Voting Works</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>✓ Propose topics you want to see covered</li>
            <li>✓ Vote on existing topics to show your interest</li>
            <li>✓ Writers can browse trending topics for inspiration</li>
            <li>✓ High-voted topics get priority attention</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default TopicsPage;
