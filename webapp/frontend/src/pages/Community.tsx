import React, { useState, useEffect } from 'react';
import { usePreferences } from '../preferences';
import type { CommunityReview, User } from '../types';
import { api } from '../services/api';
import { Icon } from '../components/Icon';
import { Feedback } from '../components/Feedback';
import { SkeletonGrid } from '../components/SkeletonGrid';

export interface CommunityProps {
  readonly user: User | null;
  readonly defaultProductName?: string;
  readonly setToast: (msg: string) => void;
}

export function Community({ user, defaultProductName, setToast }: Readonly<CommunityProps>) {
  const { t } = usePreferences();
  const [filter, setFilter] = useState('');
  const [page, setPage] = useState(1);
  const [reviews, setReviews] = useState<CommunityReview[]>([]);
  const [lastPage, setLastPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [upvotedIds, setUpvotedIds] = useState<number[]>(() => {
    try {
      const stored = localStorage.getItem('honest_upvoted_reviews');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  const [writing, setWriting] = useState(false);
  const [busyPublishing, setBusyPublishing] = useState(false);
  const [publishError, setPublishError] = useState('');

  const loadReviews = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await api.getReviews({
        product: filter,
        page
      });
      if (data.reviews) {
        setReviews(data.reviews);
        setLastPage(data.pagination?.last_page || 1);
      }
    } catch (e: any) {
      setError(e?.message || 'Failed to load community reviews');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReviews();
  }, [filter, page]);

  const handlePublishReview = async (form: HTMLFormElement) => {
    setBusyPublishing(true);
    setPublishError('');
    const data = Object.fromEntries(new FormData(form));

    try {
      await api.submitReview({
        product_name: String(data.product_name || ''),
        user_name: user?.name || String(data.user_name || 'Community shopper'),
        tier: 'original',
        rating: Number(data.rating || 5),
        material_accuracy_rating: Number(data.material_accuracy_rating || 5),
        comment: String(data.comment || '')
      });
      setWriting(false);
      setToast(t('Your review has been published.'));
      loadReviews();
    } catch (e: any) {
      setPublishError(e?.message || 'Failed to publish review');
    } finally {
      setBusyPublishing(false);
    }
  };

  const handleUpvote = async (id: number) => {
    if (upvotedIds.includes(id)) return;
    try {
      const res = await api.upvoteReview(id);
      const newUpvoted = [...upvotedIds, id];
      setUpvotedIds(newUpvoted);
      localStorage.setItem('honest_upvoted_reviews', JSON.stringify(newUpvoted));

      setReviews((prev) =>
        prev.map((r) => (r.id === id ? { ...r, upvotes: res.upvotes || r.upvotes + 1 } : r))
      );
      setToast(t('Marked helpful.'));
    } catch (e: any) {
      setToast(e?.message || 'Could not register upvote');
    }
  };

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <div className="eyebrow">{t('BETTER TOGETHER')}</div>
          <h1>
            {t('The community view')}
            <span className="heading-dot">.</span>
          </h1>
          <p>{t('Share your experience. Help the next shopper make a better choice.')}</p>
        </div>
        <button className="button primary" onClick={() => setWriting(!writing)}>
          <Icon name={writing ? 'close' : 'plus'} size={17} />
          {writing ? t('Cancel review') : t('Write a review')}
        </button>
      </div>

      <div className="notice">
        <Icon name="users" size={18} />
        <span>{t('Community submissions and seeded examples. Purchase verification is not provided.')}</span>
      </div>

      {writing && (
        <form
          className="panel review-form"
          onSubmit={(e) => {
            e.preventDefault();
            handlePublishReview(e.currentTarget);
          }}
        >
          <h2>{t('Tell us how it really is')}</h2>
          <div className="form-grid">
            <div className="field">
              <label htmlFor="review-product">{t('Product name')}</label>
              <input
                id="review-product"
                name="product_name"
                required
                maxLength={255}
                defaultValue={defaultProductName || ''}
              />
            </div>
            <div className="field">
              <label htmlFor="review-name">{t('Display name')}</label>
              <input
                id="review-name"
                name="user_name"
                maxLength={100}
                defaultValue={user?.name || ''}
                placeholder={t('Community shopper')}
              />
            </div>
            <div className="field">
              <label htmlFor="review-rating">{t('Overall rating')}</label>
              <select id="review-rating" name="rating" defaultValue="5">
                {[5, 4, 3, 2, 1].map((n) => (
                  <option key={n} value={n}>
                    {n} / 5
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label htmlFor="review-material">{t('Material accuracy')}</label>
              <select id="review-material" name="material_accuracy_rating" defaultValue="5">
                {[5, 4, 3, 2, 1].map((n) => (
                  <option key={n} value={n}>
                    {n} / 5
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="field">
            <label htmlFor="review-comment">{t('Your experience')}</label>
            <textarea
              id="review-comment"
              name="comment"
              required
              minLength={5}
              maxLength={2000}
              rows={4}
              placeholder={t('How did the quality, fit, or materials compare with the listing?')}
            />
          </div>

          {publishError && <Feedback message={publishError} />}

          <button className="button primary" type="submit" disabled={busyPublishing}>
            {busyPublishing ? t('Publishing…') : t('Publish review')}
          </button>
        </form>
      )}

      {/* Review Search Filter */}
      <form
        className="catalog-search community-search"
        onSubmit={(e) => {
          e.preventDefault();
          const d = new FormData(e.currentTarget);
          setFilter(String(d.get('q') || ''));
          setPage(1);
        }}
      >
        <Icon name="search" size={18} />
        <input
          aria-label={t('Filter reviews by product')}
          name="q"
          placeholder={t('Find reviews for a product…')}
        />
        <button className="button secondary small" type="submit">
          {t('Search')}
        </button>
      </form>

      {loading ? (
        <SkeletonGrid variant="review" count={4} />
      ) : error ? (
        <Feedback message={error} onRetry={loadReviews} />
      ) : (
        <>
          <div className="review-grid">
            {reviews.map((r) => (
              <article className="panel review-card" key={r.id}>
                <div className="review-author">
                  <span className="avatar">{r.user_name?.slice(0, 1) || 'S'}</span>
                  <span>
                    <strong>{r.user_name || t('Community shopper')}</strong>
                    <small>{new Date(r.created_at).toLocaleDateString()}</small>
                  </span>
                  <span className="stars" aria-label={`${r.rating} out of 5 stars`}>
                    {'★'.repeat(r.rating)}
                    {'☆'.repeat(5 - r.rating)}
                  </span>
                </div>
                <h3>{r.product_name}</h3>
                <p dir="auto">{r.comment}</p>
                <div className="review-footer">
                  <small>
                    {t('Material accuracy')}{' '}
                    <strong>{r.material_accuracy_rating}/5</strong>
                  </small>
                  <button
                    className="text-button"
                    disabled={upvotedIds.includes(r.id)}
                    onClick={() => handleUpvote(r.id)}
                  >
                    <Icon name="heart" size={16} />
                    {upvotedIds.includes(r.id) ? t('Marked helpful') : t('Helpful')} ({r.upvotes})
                  </button>
                </div>
              </article>
            ))}
          </div>

          {!reviews.length && (
            <div className="empty-state">
              <Icon name="chat" size={35} />
              <h2>{t('No reviews yet')}</h2>
              <p>{t('Be the first to share your experience with this product.')}</p>
            </div>
          )}

          <div className="pagination">
            <button
              className="button secondary small"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
            >
              {t('Previous')}
            </button>
            <span>
              {t('Page')} {page} {t('of')} {lastPage}
            </span>
            <button
              className="button secondary small"
              disabled={page >= lastPage}
              onClick={() => setPage((p) => p + 1)}
            >
              {t('Next')}
            </button>
          </div>
        </>
      )}
    </div>
  );
}
