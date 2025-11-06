import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { topicsAPI } from '../services/api';
import useAuthStore from '../store/authStore';

interface Topic {
  id: string;
  title: string;
  description: string;
  upvotes: number;
  downvotes: number;
  net_votes: number;
  trending_score: number;
  article_count: number;
  user_vote: string | null;
  created_at: string;
  created_by: string;
}

const TopicsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const { isAuthenticated } = useAuthStore();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTopic, setNewTopic] = useState({ title: '', description: '' });

  // Fetch topics from API
  const { data: topics = [], isLoading, error } = useQuery<Topic[]>({
    queryKey: ['topics'],
    queryFn: async () => {
      const response = await topicsAPI.list();
      return response.data;
    },
  });

  // Vote mutation
  const voteMutation = useMutation({
    mutationFn: ({ topicId, voteType }: { topicId: string; voteType: 'upvote' | 'downvote' }) =>
      topicsAPI.vote(topicId, voteType),
    onSuccess: () => {
      // Refetch topics after voting
      queryClient.invalidateQueries({ queryKey: ['topics'] });
    },
  });

  // Create topic mutation
  const createMutation = useMutation({
    mutationFn: (data: { title: string; description: string }) =>
      topicsAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['topics'] });
      setShowCreateModal(false);
      setNewTopic({ title: '', description: '' });
    },
  });

  const handleVote = (topicId: string, voteType: 'up' | 'down') => {
    if (!isAuthenticated) {
      alert('Please log in to vote on topics');
      return;
    }
    voteMutation.mutate({ topicId, voteType: voteType === 'up' ? 'upvote' : 'downvote' });
  };

  const handleCreateTopic = () => {
    if (!isAuthenticated) {
      alert('Please log in to propose topics');
      return;
    }
    if (newTopic.title.length < 5 || newTopic.description.length < 20) {
      alert('Title must be at least 5 characters and description at least 20 characters');
      return;
    }
    createMutation.mutate(newTopic);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading topics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">Failed to load topics</p>
          <button onClick={() => queryClient.invalidateQueries({ queryKey: ['topics'] })} className="btn btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

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
          <button onClick={() => setShowCreateModal(true)} className="btn btn-primary">
            + Propose Topic
          </button>
        </div>

        {/* Topics List */}
        <div className="space-y-4">
          {topics.length === 0 ? (
            <div className="bg-white rounded-lg shadow-sm p-12 text-center">
              <p className="text-gray-600 mb-4">No topics yet. Be the first to propose one!</p>
              <button onClick={() => setShowCreateModal(true)} className="btn btn-primary">
                + Propose Topic
              </button>
            </div>
          ) : (
            topics.map((topic, index) => (
              <div key={topic.id} className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow">
                <div className="flex gap-4">
                  {/* Voting */}
                  <div className="flex flex-col items-center">
                    <button
                      onClick={() => handleVote(topic.id, 'up')}
                      className={`p-2 rounded hover:bg-gray-100 transition-colors ${
                        topic.user_vote === 'upvote' ? 'text-primary-600' : 'text-gray-400'
                      }`}
                      disabled={voteMutation.isPending}
                    >
                      <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clipRule="evenodd" />
                      </svg>
                    </button>
                    <span className="text-xl font-bold text-gray-900 my-1">
                      {topic.net_votes}
                    </span>
                    <button
                      onClick={() => handleVote(topic.id, 'down')}
                      className={`p-2 rounded hover:bg-gray-100 transition-colors ${
                        topic.user_vote === 'downvote' ? 'text-red-600' : 'text-gray-400'
                      }`}
                      disabled={voteMutation.isPending}
                    >
                      <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    </button>
                  </div>

                  {/* Content */}
                  <div className="flex-1">
                    {/* Rank */}
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm font-bold text-gray-500">#{index + 1}</span>
                      {topic.article_count > 0 && (
                        <span className="badge badge-success text-xs">
                          {topic.article_count} article{topic.article_count !== 1 ? 's' : ''}
                        </span>
                      )}
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
            ))
          )}
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

      {/* Create Topic Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Propose a New Topic</h2>
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  setNewTopic({ title: '', description: '' });
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Topic Title <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={newTopic.title}
                  onChange={(e) => setNewTopic({ ...newTopic, title: e.target.value })}
                  placeholder="e.g., Investigating Local School Funding"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  maxLength={200}
                />
                <p className="text-sm text-gray-500 mt-1">
                  {newTopic.title.length}/200 characters (minimum 5)
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={newTopic.description}
                  onChange={(e) => setNewTopic({ ...newTopic, description: e.target.value })}
                  placeholder="Provide a detailed description of what you'd like to see covered in this topic..."
                  rows={6}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  maxLength={1000}
                />
                <p className="text-sm text-gray-500 mt-1">
                  {newTopic.description.length}/1000 characters (minimum 20)
                </p>
              </div>

              {createMutation.isError && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                  Failed to create topic. Please try again.
                </div>
              )}

              <div className="flex gap-3 pt-4">
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    setNewTopic({ title: '', description: '' });
                  }}
                  className="btn btn-secondary flex-1"
                  disabled={createMutation.isPending}
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateTopic}
                  className="btn btn-primary flex-1"
                  disabled={createMutation.isPending || newTopic.title.length < 5 || newTopic.description.length < 20}
                >
                  {createMutation.isPending ? 'Creating...' : 'Propose Topic'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TopicsPage;
