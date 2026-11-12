import React, { useEffect, useState, useRef } from 'react';
import './BrandIntro.css';

/**
 * BrandIntro – Cinematic 3-second opening animation for ROY DESIGNS.
 * Sequence:
 *   0.0 - 0.5s: Deep charcoal background (#171717)
 *   0.5 - 1.5s: Brand name "ROY DESIGNS" smoothly reveals
 *   1.5 - 2.5s: Champagne gold (#C6A46A) light sweep + architectural geometry outline
 *   2.5 - 2.9s: Tagline "AI-POWERED ARCHITECTURE & DESIGN" appears
 *   2.9 - 3.3s: Smooth fade transition into the homepage
 */
export default function BrandIntro({ onFinish }) {
  const [isExiting, setIsExiting] = useState(false);
  const [isVisible, setIsVisible] = useState(true);
  const hasFinishedRef = useRef(false);

  useEffect(() => {
    // Check prefers-reduced-motion
    if (typeof window !== 'undefined' && window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
      if (mediaQuery.matches) {
        setIsVisible(false);
        if (onFinish && !hasFinishedRef.current) {
          hasFinishedRef.current = true;
          onFinish();
        }
        return;
      }
    }

    // Begin smooth fade-out at 2850ms
    const exitTimer = setTimeout(() => {
      setIsExiting(true);
    }, 2850);

    // Complete transition and unmount at 3300ms
    const finishTimer = setTimeout(() => {
      setIsVisible(false);
      if (onFinish && !hasFinishedRef.current) {
        hasFinishedRef.current = true;
        onFinish();
      }
    }, 3300);

    return () => {
      clearTimeout(exitTimer);
      clearTimeout(finishTimer);
    };
  }, [onFinish]);

  const handleSkip = () => {
    setIsExiting(true);
    setTimeout(() => {
      setIsVisible(false);
      if (onFinish && !hasFinishedRef.current) {
        hasFinishedRef.current = true;
        onFinish();
      }
    }, 150);
  };

  if (!isVisible) return null;

  return (
    <aside
      className={`brand-intro-overlay ${isExiting ? 'fade-exit' : ''}`}
      role="dialog"
      aria-modal="true"
      aria-label="ROY DESIGNS Brand Introduction"
    >
      <div className="brand-intro-backdrop" />

      <div className="brand-intro-content">
        {/* Architectural Geometric Line Outline */}
        <div className="architectural-symbol-wrap" aria-hidden="true">
          <svg
            className="architectural-symbol"
            viewBox="0 0 120 64"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            {/* Minimalist architectural apex / pediment */}
            <path
              className="arch-line arch-roof"
              d="M14 48 L60 12 L106 48"
              stroke="#C6A46A"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            {/* Baseline horizontal guide */}
            <path
              className="arch-line arch-base"
              d="M26 48 L94 48"
              stroke="#C6A46A"
              strokeWidth="1"
              strokeLinecap="round"
            />
            {/* Center architectural focal point */}
            <circle
              className="arch-line arch-keystone"
              cx="60"
              cy="28"
              r="2"
              fill="#C6A46A"
            />
          </svg>
        </div>

        {/* Brand Name with Champagne-Gold Light Sweep */}
        <div className="brand-title-wrap">
          <h1 className="brand-name-base">ROY DESIGNS</h1>
          <div className="brand-name-shimmer" aria-hidden="true">
            ROY DESIGNS
          </div>
        </div>

        {/* Sophisticated Architectural Symmetrical Accent */}
        <div className="architectural-divider" aria-hidden="true">
          <span className="divider-line" />
          <span className="divider-diamond" />
          <span className="divider-line" />
        </div>

        {/* Primary Tagline */}
        <p className="brand-tagline">
          AI-POWERED ARCHITECTURE &amp; DESIGN
        </p>

        {/* Official Product Sub-label */}
        <p className="brand-product-label">
          AI House Planning &amp; Visualization System
        </p>
      </div>

      <button
        type="button"
        className="brand-intro-skip"
        onClick={handleSkip}
        aria-label="Skip intro animation"
      >
        SKIP
      </button>
    </aside>
  );
}
