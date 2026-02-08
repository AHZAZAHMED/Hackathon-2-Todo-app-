/**
 * Hero component
 * Landing page hero section with tagline and CTA
 */

import Link from 'next/link';

export function Hero() {
  return (
    <section className="bg-gradient-to-b from-primary-50 to-white py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto text-center">
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
          Organize Your Tasks,
          <span className="text-primary-600"> Boost Your Productivity</span>
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          A simple and powerful task management application to help you stay organized and get things done.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/signup"
            className="bg-primary-600 text-white px-8 py-3 rounded-md text-lg font-medium hover:bg-primary-700 transition-colors"
          >
            Get Started Free
          </Link>
          <Link
            href="/login"
            className="bg-white text-primary-600 px-8 py-3 rounded-md text-lg font-medium border-2 border-primary-600 hover:bg-primary-50 transition-colors"
          >
            Sign In
          </Link>
        </div>
      </div>
    </section>
  );
}
