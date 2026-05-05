/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  compress: true,
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
