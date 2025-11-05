/**
 * Mock data for demo/development mode
 * Enable by setting REACT_APP_DEMO_MODE=true in .env
 */

export const mockArticles = [
  {
    id: '1',
    title: 'The Rise of Citizen Journalism in the Digital Age',
    slug: 'rise-of-citizen-journalism-digital-age',
    summary: 'Exploring how everyday people are becoming powerful voices in media through digital platforms and social networks.',
    content: `# The Rise of Citizen Journalism in the Digital Age

In an era where information travels at the speed of light, citizen journalism has emerged as a powerful force in shaping public discourse...`,
    author: {
      id: '1',
      username: 'sarah_journalist',
      full_name: 'Sarah Johnson',
      avatar_url: 'https://ui-avatars.com/api/?name=Sarah+Johnson&background=0ea5e9&color=fff',
    },
    category: 'Media',
    tags: ['journalism', 'media', 'technology', 'social-media'],
    cover_image_url: 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800',
    reading_time_minutes: 8,
    view_count: 1247,
    average_rating: 4.5,
    rating_count: 23,
    published_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '2',
    title: 'Climate Change: Local Actions for Global Impact',
    slug: 'climate-change-local-actions-global-impact',
    summary: 'How individual communities are making a difference in the fight against climate change through innovative local initiatives.',
    content: `# Climate Change: Local Actions for Global Impact

While world leaders debate climate policy, communities around the globe are taking matters into their own hands...`,
    author: {
      id: '1',
      username: 'sarah_journalist',
      full_name: 'Sarah Johnson',
      avatar_url: 'https://ui-avatars.com/api/?name=Sarah+Johnson&background=0ea5e9&color=fff',
    },
    category: 'Environment',
    tags: ['climate-change', 'sustainability', 'community', 'environment'],
    cover_image_url: 'https://images.unsplash.com/photo-1569163139394-de4798aa62b6?w=800',
    reading_time_minutes: 12,
    view_count: 892,
    average_rating: 4.7,
    rating_count: 18,
    published_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    created_at: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '3',
    title: 'Tech Giants and Data Privacy: What You Need to Know',
    slug: 'tech-giants-data-privacy-what-you-need-know',
    summary: 'An in-depth look at how major technology companies collect, use, and monetize your personal data, and what you can do about it.',
    content: `# Tech Giants and Data Privacy: What You Need to Know

Every click, like, and share contributes to a vast digital profile that tech companies use to target ads...`,
    author: {
      id: '2',
      username: 'mike_tech',
      full_name: 'Mike Chen',
      avatar_url: 'https://ui-avatars.com/api/?name=Mike+Chen&background=9333ea&color=fff',
    },
    category: 'Technology',
    tags: ['privacy', 'technology', 'data-security', 'big-tech'],
    cover_image_url: 'https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800',
    reading_time_minutes: 15,
    view_count: 2134,
    average_rating: 4.8,
    rating_count: 41,
    published_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    created_at: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '4',
    title: 'The Mental Health Crisis: Breaking the Stigma',
    slug: 'mental-health-crisis-breaking-stigma',
    summary: 'Examining the growing mental health challenges in modern society and the movement to normalize conversations about mental wellness.',
    content: `# The Mental Health Crisis: Breaking the Stigma

Mental health has emerged from the shadows as one of the most pressing public health issues of our time...`,
    author: {
      id: '1',
      username: 'sarah_journalist',
      full_name: 'Sarah Johnson',
      avatar_url: 'https://ui-avatars.com/api/?name=Sarah+Johnson&background=0ea5e9&color=fff',
    },
    category: 'Health',
    tags: ['mental-health', 'wellness', 'society', 'healthcare'],
    cover_image_url: 'https://images.unsplash.com/photo-1551190822-a9333d879b1f?w=800',
    reading_time_minutes: 10,
    view_count: 1567,
    average_rating: 4.6,
    rating_count: 28,
    published_at: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
    created_at: new Date(Date.now() - 12 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '5',
    title: 'The Future of Work: Remote, Hybrid, or Back to Office?',
    slug: 'future-of-work-remote-hybrid-back-office',
    summary: 'Analyzing how the pandemic transformed workplace culture and what the future holds for how and where we work.',
    content: `# The Future of Work: Remote, Hybrid, or Back to Office?

The COVID-19 pandemic forced the world's largest work-from-home experiment...`,
    author: {
      id: '2',
      username: 'mike_tech',
      full_name: 'Mike Chen',
      avatar_url: 'https://ui-avatars.com/api/?name=Mike+Chen&background=9333ea&color=fff',
    },
    category: 'Business',
    tags: ['future-of-work', 'remote-work', 'business', 'workplace-culture'],
    cover_image_url: 'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=800',
    reading_time_minutes: 14,
    view_count: 1823,
    average_rating: 4.4,
    rating_count: 35,
    published_at: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
    created_at: new Date(Date.now() - 16 * 24 * 60 * 60 * 1000).toISOString(),
  },
];

export const mockTopics = [
  {
    id: '1',
    title: 'Investigating Local Government Transparency',
    description: 'A deep dive into how accessible local government records and meetings are to citizens, and what can be improved.',
    category: 'Politics',
    upvotes: 42,
    downvotes: 5,
    vote_score: 37,
    proposed_by: {
      username: 'john_reader',
      full_name: 'John Doe',
    },
    created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '2',
    title: 'The Impact of AI on Creative Industries',
    description: 'Exploring how artificial intelligence is changing music, art, writing, and other creative fields.',
    category: 'Technology',
    upvotes: 38,
    downvotes: 3,
    vote_score: 35,
    proposed_by: {
      username: 'john_reader',
      full_name: 'John Doe',
    },
    created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '3',
    title: 'Community Solutions to Food Deserts',
    description: 'Documenting innovative approaches communities are taking to address lack of access to fresh, healthy food.',
    category: 'Community',
    upvotes: 31,
    downvotes: 2,
    vote_score: 29,
    proposed_by: {
      username: 'john_reader',
      full_name: 'John Doe',
    },
    created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
  },
];

export const mockUser = {
  id: '1',
  email: 'demo@example.com',
  username: 'demo_user',
  full_name: 'Demo User',
  is_writer: true,
  is_verified: true,
  avatar_url: 'https://ui-avatars.com/api/?name=Demo+User&background=0ea5e9&color=fff',
  bio: 'Passionate about citizen journalism and community storytelling.',
  karma_points: 150,
  subscription_tier: 'premium_writer',
};

export const isDemoMode = process.env.REACT_APP_DEMO_MODE === 'true';
