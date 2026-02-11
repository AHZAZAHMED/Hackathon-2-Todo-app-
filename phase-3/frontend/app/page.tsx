/**
 * Landing page
 * Home page with hero section and features showcase
 */

import { Hero } from '@/components/landing/Hero';
import { Features } from '@/components/landing/Features';

export default function HomePage() {
  return (
    <>
      <Hero />
      <Features />
    </>
  );
}
