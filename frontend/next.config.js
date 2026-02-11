/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  // Optimize production bundle
  swcMinify: true,
  // Enable experimental features for faster navigation
  experimental: {
    optimizePackageImports: ['lucide-react'],
  },
  // Optimize images
  images: {
    remotePatterns: [],
  },
}

module.exports = nextConfig
