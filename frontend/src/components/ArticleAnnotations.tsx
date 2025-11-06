import React, { useState, useRef, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { annotationsAPI } from '../services/api';
import useAuthStore from '../store/authStore';

interface Annotation {
  id: string;
  user: {
    username: string;
    full_name: string;
    avatar_url?: string;
  };
  selection_text: string;
  selection_start_offset: number;
  selection_end_offset: number;
  annotation_type: string;
  comment: string;
  evidence_url?: string;
  evidence_title?: string;
  evidence_excerpt?: string;
  verification_status: string;
  upvotes: number;
  downvotes: number;
  created_at: string;
}

interface ArticleAnnotationsProps {
  articleId: string;
  content: string;
}

const ArticleAnnotations: React.FC<ArticleAnnotationsProps> = ({ articleId, content }) => {
  const queryClient = useQueryClient();
  const { isAuthenticated } = useAuthStore();
  const contentRef = useRef<HTMLDivElement>(null);
  const [selectedText, setSelectedText] = useState('');
  const [selectionRange, setSelectionRange] = useState<{ start: number; end: number } | null>(null);
  const [showAnnotationForm, setShowAnnotationForm] = useState(false);
  const [selectedAnnotation, setSelectedAnnotation] = useState<Annotation | null>(null);
  const [formData, setFormData] = useState({
    annotation_type: 'comment',
    comment: '',
    evidence_url: '',
    evidence_title: '',
    evidence_excerpt: '',
  });

  // Fetch annotations
  const { data: annotations = [] } = useQuery<Annotation[]>({
    queryKey: ['annotations', articleId],
    queryFn: async () => {
      const response = await annotationsAPI.list(articleId);
      return response.data;
    },
  });

  // Create annotation mutation
  const createMutation = useMutation({
    mutationFn: (data: any) => annotationsAPI.create(articleId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['annotations', articleId] });
      setShowAnnotationForm(false);
      resetForm();
    },
  });

  // Vote on annotation mutation
  const voteMutation = useMutation({
    mutationFn: ({ annotationId, voteType }: { annotationId: string; voteType: 'upvote' | 'downvote' }) =>
      annotationsAPI.vote(annotationId, voteType),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['annotations', articleId] });
    },
  });

  const resetForm = () => {
    setFormData({
      annotation_type: 'comment',
      comment: '',
      evidence_url: '',
      evidence_title: '',
      evidence_excerpt: '',
    });
    setSelectedText('');
    setSelectionRange(null);
  };

  // Handle text selection
  const handleTextSelection = () => {
    const selection = window.getSelection();
    if (!selection || selection.isCollapsed) {
      return;
    }

    const text = selection.toString().trim();
    if (text.length < 3) return;

    // Calculate character offsets in the article content
    const range = selection.getRangeAt(0);
    const preSelectionRange = range.cloneRange();
    preSelectionRange.selectNodeContents(contentRef.current!);
    preSelectionRange.setEnd(range.startContainer, range.startOffset);
    const start = preSelectionRange.toString().length;
    const end = start + text.length;

    setSelectedText(text);
    setSelectionRange({ start, end });
    setShowAnnotationForm(true);
  };

  const handleCreateAnnotation = () => {
    if (!isAuthenticated) {
      alert('Please log in to create annotations');
      return;
    }

    if (!selectionRange || !selectedText || !formData.comment) {
      alert('Please select text and add a comment');
      return;
    }

    createMutation.mutate({
      selection_text: selectedText,
      selection_start_offset: selectionRange.start,
      selection_end_offset: selectionRange.end,
      annotation_type: formData.annotation_type,
      comment: formData.comment,
      evidence_url: formData.evidence_url || undefined,
      evidence_title: formData.evidence_title || undefined,
      evidence_excerpt: formData.evidence_excerpt || undefined,
    });
  };

  const getAnnotationColor = (type: string) => {
    switch (type) {
      case 'fact_check':
        return 'bg-blue-100 border-blue-300';
      case 'correction':
        return 'bg-red-100 border-red-300';
      case 'support':
        return 'bg-green-100 border-green-300';
      case 'question':
        return 'bg-yellow-100 border-yellow-300';
      default:
        return 'bg-gray-100 border-gray-300';
    }
  };

  const getVerificationBadge = (status: string) => {
    switch (status) {
      case 'verified_accurate':
        return <span className="badge badge-success text-xs">Verified Accurate</span>;
      case 'verified_inaccurate':
        return <span className="badge badge-error text-xs">Verified Inaccurate</span>;
      case 'disputed':
        return <span className="badge badge-warning text-xs">Disputed</span>;
      default:
        return <span className="badge badge-secondary text-xs">Pending Review</span>;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  return (
    <div className="space-y-6">
      {/* Article Content with Selection */}
      <div
        ref={contentRef}
        onMouseUp={handleTextSelection}
        className="prose prose-lg max-w-none cursor-text"
      >
        {content.split('\n\n').map((paragraph, index) => (
          <p key={index}>{paragraph}</p>
        ))}
      </div>

      {/* Selection Tooltip/Form */}
      {showAnnotationForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-gray-900">Add Annotation</h3>
              <button
                onClick={() => {
                  setShowAnnotationForm(false);
                  resetForm();
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Selected Text */}
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 mb-4">
              <p className="text-sm text-gray-600 mb-1">Selected Text:</p>
              <p className="text-gray-900 italic">"{selectedText}"</p>
            </div>

            {/* Annotation Type */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Annotation Type
              </label>
              <select
                value={formData.annotation_type}
                onChange={(e) => setFormData({ ...formData, annotation_type: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                <option value="comment">💬 Comment</option>
                <option value="fact_check">✓ Fact Check</option>
                <option value="correction">✏️ Correction</option>
                <option value="question">❓ Question</option>
                <option value="support">👍 Supporting Evidence</option>
              </select>
            </div>

            {/* Comment */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Comment <span className="text-red-500">*</span>
              </label>
              <textarea
                value={formData.comment}
                onChange={(e) => setFormData({ ...formData, comment: e.target.value })}
                placeholder="Share your thoughts, fact-check, or provide additional context..."
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>

            {/* Evidence (for fact-checks and corrections) */}
            {(formData.annotation_type === 'fact_check' ||
              formData.annotation_type === 'correction' ||
              formData.annotation_type === 'support') && (
              <>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Evidence URL (Optional)
                  </label>
                  <input
                    type="url"
                    value={formData.evidence_url}
                    onChange={(e) => setFormData({ ...formData, evidence_url: e.target.value })}
                    placeholder="https://source.com/article"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Evidence Title (Optional)
                  </label>
                  <input
                    type="text"
                    value={formData.evidence_title}
                    onChange={(e) => setFormData({ ...formData, evidence_title: e.target.value })}
                    placeholder="Title of the source"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </>
            )}

            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowAnnotationForm(false);
                  resetForm();
                }}
                className="btn btn-secondary flex-1"
                disabled={createMutation.isPending}
              >
                Cancel
              </button>
              <button
                onClick={handleCreateAnnotation}
                className="btn btn-primary flex-1"
                disabled={createMutation.isPending || !formData.comment}
              >
                {createMutation.isPending ? 'Creating...' : 'Create Annotation'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Annotations List */}
      {annotations.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Annotations & Fact-Checks ({annotations.length})
          </h3>

          <div className="space-y-6">
            {annotations.map((annotation) => (
              <div
                key={annotation.id}
                className={`border rounded-lg p-4 ${getAnnotationColor(annotation.annotation_type)}`}
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    {annotation.user.avatar_url ? (
                      <img
                        src={annotation.user.avatar_url}
                        alt={annotation.user.full_name}
                        className="w-8 h-8 rounded-full"
                      />
                    ) : (
                      <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
                        <span className="text-primary-600 text-sm font-semibold">
                          {annotation.user.full_name?.charAt(0) || '?'}
                        </span>
                      </div>
                    )}
                    <div>
                      <p className="font-semibold text-sm text-gray-900">{annotation.user.full_name}</p>
                      <p className="text-xs text-gray-600">{formatDate(annotation.created_at)}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-medium text-gray-600 capitalize">
                      {annotation.annotation_type.replace('_', ' ')}
                    </span>
                    {annotation.annotation_type === 'fact_check' && getVerificationBadge(annotation.verification_status)}
                  </div>
                </div>

                {/* Selected Text */}
                <div className="bg-white bg-opacity-50 rounded p-2 mb-3">
                  <p className="text-sm text-gray-900 italic">"{annotation.selection_text}"</p>
                </div>

                {/* Comment */}
                <p className="text-gray-800 mb-3">{annotation.comment}</p>

                {/* Evidence */}
                {annotation.evidence_url && (
                  <div className="bg-white bg-opacity-70 rounded-lg p-3 mb-3">
                    <p className="text-xs font-semibold text-gray-600 mb-1">Evidence:</p>
                    {annotation.evidence_title && (
                      <p className="text-sm font-medium text-gray-900 mb-1">{annotation.evidence_title}</p>
                    )}
                    <a
                      href={annotation.evidence_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-primary-600 hover:underline break-all"
                    >
                      {annotation.evidence_url}
                    </a>
                    {annotation.evidence_excerpt && (
                      <p className="text-sm text-gray-700 mt-2 italic">"{annotation.evidence_excerpt}"</p>
                    )}
                  </div>
                )}

                {/* Voting */}
                <div className="flex items-center gap-4">
                  <button
                    onClick={() => voteMutation.mutate({ annotationId: annotation.id, voteType: 'upvote' })}
                    className="flex items-center gap-1 text-sm text-gray-600 hover:text-green-600"
                    disabled={!isAuthenticated || voteMutation.isPending}
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clipRule="evenodd" />
                    </svg>
                    <span className="font-medium">{annotation.upvotes}</span>
                  </button>
                  <button
                    onClick={() => voteMutation.mutate({ annotationId: annotation.id, voteType: 'downvote' })}
                    className="flex items-center gap-1 text-sm text-gray-600 hover:text-red-600"
                    disabled={!isAuthenticated || voteMutation.isPending}
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                    <span className="font-medium">{annotation.downvotes}</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Help Text */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-blue-900 mb-2">How to Annotate</h4>
        <p className="text-sm text-blue-800">
          Select any text in the article above to add comments, fact-checks, corrections, or supporting evidence.
          Help improve article quality through community verification!
        </p>
      </div>
    </div>
  );
};

export default ArticleAnnotations;
