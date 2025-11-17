import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { topicsAPI } from '../services/api';
import { useAuthStore } from '../store/authStore';

interface Topic {
  id: string;
  title: string;
  description: string;
  category: string;
  tags: string[];
  upvotes: number;
  downvotes: number;
  net_votes: number;
  trending_score: number;
  article_count: number;
  user_vote: string | null;
  created_at: string;
  created_by: string;
}

const CATEGORIES = [
  'All',
  'Environment',
  'Politics',
  'Health',
  'Education',
  'Housing',
  'Public Safety',
  'General',
];

const TopicsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const { isAuthenticated } = useAuthStore();

  // Tab state
  const [activeTab, setActiveTab] = useState<'all' | 'foryou'>('all');

  // Filter state
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  // UI state
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newTopic, setNewTopic] = useState({ title: '', description: '' });
  const [expandedTopic, setExpandedTopic] = useState<string | null>(null);
  const [topicComments, setTopicComments] = useState<{ [key: string]: string }>({});

  // Fetch topics from API with filters
  const { data: topics = [], isLoading, error } = useQuery<Topic[]>({
    queryKey: ['topics', selectedCategory, selectedTags, searchQuery],
    queryFn: async () => {
      const params: any = {};

      if (selectedCategory !== 'All') {
        params.category = selectedCategory;
      }

      if (selectedTags.length > 0) {
        params.tags = selectedTags.join(',');
      }

      if (searchQuery.trim()) {
        params.search = searchQuery.trim();
      }

      const response = await topicsAPI.list(params);
      return response.data;
    },
    enabled: activeTab === 'all',
  });

  // Fetch recommended topics (For You tab)
  const { data: recommendedTopics = [], isLoading: isLoadingRecommended } = useQuery<Topic[]>({
    queryKey: ['topics', 'recommended'],
    queryFn: async () => {
      const response = await topicsAPI.recommended();
      return response.data;
    },
    enabled: activeTab === 'foryou' && isAuthenticated,
  });

  // Get all unique tags from topics for filter
  const allTags = React.useMemo(() => {
    const tagSet = new Set<string>();
    topics.forEach((topic) => {
      topic.tags?.forEach((tag) => tagSet.add(tag));
    });
    return Array.from(tagSet).sort();
  }, [topics]);

  // Vote mutation
  const voteMutation = useMutation({
    mutationFn: ({ topicId, voteType }: { topicId: string; voteType: 'upvote' | 'downvote' }) =>
      topicsAPI.vote(topicId, voteType),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['topics'] });
    },
  });

  // Create topic mutation
  const createMutation = useMutation({
    mutationFn: (data: { title: string; description: string }) =>
      topicsAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['topics'] });
      setShowCreateForm(false);
      setNewTopic({ title: '', description: '' });
    },
  });

  const handleCommentSubmit = (topicId: string) => {
    if (!isAuthenticated) {
      alert('Please log in to comment');
      return;
    }
    const comment = topicComments[topicId];
    if (!comment || comment.trim().length === 0) return;

    // TODO: Implement comment API call
    console.log('Submitting comment for topic:', topicId, comment);
    setTopicComments({ ...topicComments, [topicId]: '' });
  };

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

  const toggleTag = (tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  };

  const clearFilters = () => {
    setSelectedCategory('All');
    setSelectedTags([]);
    setSearchQuery('');
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const displayTopics = activeTab === 'all' ? topics : recommendedTopics;
  const displayLoading = activeTab === 'all' ? isLoading : isLoadingRecommended;

  if (displayLoading) {
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
        {/* Tabs */}
        <div className="mb-6 border-b border-gray-200">
          <div className="flex gap-8">
            <button
              onClick={() => setActiveTab('all')}
              className={`pb-4 px-1 border-b-2 font-semibold transition-colors ${
                activeTab === 'all'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              All Topics
            </button>
            <button
              onClick={() => {
                if (!isAuthenticated) {
                  alert('Please log in to see personalized recommendations');
                  return;
                }
                setActiveTab('foryou');
              }}
              className={`pb-4 px-1 border-b-2 font-semibold transition-colors flex items-center gap-2 ${
                activeTab === 'foryou'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              For You
              <span className="px-2 py-0.5 text-xs bg-primary-100 text-primary-700 rounded-full">
                Personalized
              </span>
            </button>
          </div>
        </div>

        {/* Filters (only show on "All Topics" tab) */}
        {activeTab === 'all' && (
          <div className="mb-6 bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
              {(selectedCategory !== 'All' || selectedTags.length > 0 || searchQuery) && (
                <button
                  onClick={clearFilters}
                  className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                >
                  Clear all
                </button>
              )}
            </div>

            {/* Search */}
            <div className="mb-4">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search topics..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            {/* Category Filter */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
              <div className="flex flex-wrap gap-2">
                {CATEGORIES.map((category) => (
                  <button
                    key={category}
                    onClick={() => setSelectedCategory(category)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                      selectedCategory === category
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {category}
                  </button>
                ))}
              </div>
            </div>

            {/* Tags Filter */}
            {allTags.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Tags</label>
                <div className="flex flex-wrap gap-2">
                  {allTags.map((tag) => (
                    <button
                      key={tag}
                      onClick={() => toggleTag(tag)}
                      className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                        selectedTags.includes(tag)
                          ? 'bg-secondary-600 text-white'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                    >
                      #{tag}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Active filters summary */}
            {(selectedCategory !== 'All' || selectedTags.length > 0 || searchQuery) && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-sm text-gray-600">
                  Showing {displayTopics.length} topic{displayTopics.length !== 1 ? 's' : ''}
                  {selectedCategory !== 'All' && <span className="font-medium"> in {selectedCategory}</span>}
                  {selectedTags.length > 0 && (
                    <span className="font-medium"> with tags: {selectedTags.join(', ')}</span>
                  )}
                  {searchQuery && <span className="font-medium"> matching "{searchQuery}"</span>}
                </p>
              </div>
            )}
          </div>
        )}

        {/* For You explanation */}
        {activeTab === 'foryou' && (
          <div className="mb-6 bg-gradient-to-r from-primary-50 to-secondary-50 rounded-lg p-6 border border-primary-200">
            <div className="flex items-start gap-3">
              <svg className="w-6 h-6 text-primary-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">Personalized for You</h3>
                <p className="text-sm text-gray-700">
                  These topics are selected based on your interests, including categories and tags you engage with most.
                  The more you vote and read, the better your recommendations become!
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Propose Topic Section */}
        <div className="mb-8">
          {!showCreateForm ? (
            <button
              onClick={() => {
                if (!isAuthenticated) {
                  alert('Please log in to propose topics');
                  return;
                }
                setShowCreateForm(true);
              }}
              className="w-full bg-white border-2 border-dashed border-gray-300 rounded-lg p-6 hover:border-primary-500 hover:bg-primary-50 transition-all group"
            >
              <div className="flex items-center justify-center gap-3">
                <svg className="w-8 h-8 text-gray-400 group-hover:text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                <span className="text-lg font-semibold text-gray-600 group-hover:text-primary-700">
                  Propose a Topic for Writers to Cover
                </span>
              </div>
            </button>
          ) : (
            <div className="bg-white rounded-lg shadow-md p-6 border-2 border-primary-500">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold text-gray-900">Propose a New Topic</h3>
                <button
                  onClick={() => {
                    setShowCreateForm(false);
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
                  <input
                    type="text"
                    value={newTopic.title}
                    onChange={(e) => setNewTopic({ ...newTopic, title: e.target.value })}
                    placeholder="What topic should be covered? (e.g., Local School Funding Crisis)"
                    className="w-full px-4 py-3 text-lg border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    maxLength={200}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    {newTopic.title.length}/200 characters
                  </p>
                </div>

                <div>
                  <textarea
                    value={newTopic.description}
                    onChange={(e) => setNewTopic({ ...newTopic, description: e.target.value })}
                    placeholder="Describe what you'd like to see covered and why it matters..."
                    rows={4}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    maxLength={1000}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    {newTopic.description.length}/1000 characters
                  </p>
                </div>

                {createMutation.isError && (
                  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                    Failed to create topic. Please try again.
                  </div>
                )}

                <div className="flex gap-3">
                  <button
                    onClick={() => {
                      setShowCreateForm(false);
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
                    {createMutation.isPending ? 'Proposing...' : 'Propose Topic'}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Topics List */}
        <div className="space-y-4">
          {displayTopics.length === 0 ? (
            <div className="bg-white rounded-lg shadow-sm p-12 text-center">
              <p className="text-gray-600 mb-4">
                {activeTab === 'foryou'
                  ? 'Start voting on topics to get personalized recommendations!'
                  : 'No topics found. Try adjusting your filters or be the first to propose one!'}
              </p>
              {activeTab === 'all' && (selectedCategory !== 'All' || selectedTags.length > 0 || searchQuery) && (
                <button onClick={clearFilters} className="btn btn-secondary mr-3">
                  Clear Filters
                </button>
              )}
              <button onClick={() => setShowCreateForm(true)} className="btn btn-primary">
                + Propose Topic
              </button>
            </div>
          ) : (
            displayTopics.map((topic) => {
              const isExpanded = expandedTopic === topic.id;
              return (
                <div key={topic.id} className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow border border-gray-200">
                  <div className="p-6">
                    {/* Topic Header */}
                    <div className="flex gap-4">
                      {/* Voting */}
                      <div className="flex flex-col items-center gap-1">
                        <button
                          onClick={() => handleVote(topic.id, 'up')}
                          className={`p-2 rounded hover:bg-primary-50 transition-colors ${
                            topic.user_vote === 'upvote' ? 'text-primary-600' : 'text-gray-400'
                          }`}
                          disabled={!isAuthenticated}
                        >
                          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clipRule="evenodd" />
                          </svg>
                        </button>
                        <span className="text-lg font-bold text-gray-900">{topic.net_votes}</span>
                        <button
                          onClick={() => handleVote(topic.id, 'down')}
                          className={`p-2 rounded hover:bg-gray-50 transition-colors ${
                            topic.user_vote === 'downvote' ? 'text-red-600' : 'text-gray-400'
                          }`}
                          disabled={!isAuthenticated}
                        >
                          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                          </svg>
                        </button>
                      </div>

                      {/* Content */}
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <h3 className="text-xl font-bold text-gray-900 mb-1">{topic.title}</h3>
                            <div className="flex items-center gap-3 mb-2">
                              <span className="px-3 py-1 bg-primary-100 text-primary-700 text-sm font-medium rounded-full">
                                {topic.category}
                              </span>
                              <span className="text-sm text-gray-500">
                                {formatDate(topic.created_at)}
                              </span>
                            </div>
                          </div>
                        </div>

                        <p className="text-gray-700 mb-3">{topic.description}</p>

                        {/* Tags */}
                        {topic.tags && topic.tags.length > 0 && (
                          <div className="flex flex-wrap gap-2 mb-3">
                            {topic.tags.map((tag) => (
                              <span
                                key={tag}
                                className="px-2.5 py-0.5 bg-gray-100 text-gray-600 text-xs font-medium rounded-full"
                              >
                                #{tag}
                              </span>
                            ))}
                          </div>
                        )}

                        {/* Stats */}
                        <div className="flex items-center gap-4 text-sm text-gray-500">
                          <span className="flex items-center gap-1">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                            </svg>
                            {topic.article_count} articles
                          </span>
                          <button
                            onClick={() => setExpandedTopic(isExpanded ? null : topic.id)}
                            className="flex items-center gap-1 hover:text-primary-600 transition-colors"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                            </svg>
                            Discuss
                          </button>
                        </div>

                        {/* Comments Section */}
                        {isExpanded && (
                          <div className="mt-4 pt-4 border-t border-gray-200">
                            <h4 className="font-semibold text-gray-900 mb-3">Discussion</h4>
                            <div className="space-y-3">
                              <div className="flex gap-3">
                                <textarea
                                  value={topicComments[topic.id] || ''}
                                  onChange={(e) =>
                                    setTopicComments({ ...topicComments, [topic.id]: e.target.value })
                                  }
                                  placeholder="Share your thoughts on this topic..."
                                  rows={3}
                                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
                                  disabled={!isAuthenticated}
                                />
                              </div>
                              <button
                                onClick={() => handleCommentSubmit(topic.id)}
                                className="btn btn-primary btn-sm"
                                disabled={!isAuthenticated || !topicComments[topic.id]?.trim()}
                              >
                                Post Comment
                              </button>
                              <p className="text-xs text-gray-500 mt-2">
                                Comments feature coming soon!
                              </p>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};

export default TopicsPage;
