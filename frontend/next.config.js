/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow large PDF uploads up to 50MB
  experimental: {
    proxyTimeout: 120_000, // 2 minutes — gives Flask time to embed large PDFs
  },

  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:5000';
    return [
      {
        source: '/api/ask',
        destination: `${backendUrl}/ask`,
      },
      {
        source: '/api/health',
        destination: `${backendUrl}/health`,
      },
      {
        source: '/api/upload',
        destination: `${backendUrl}/upload`,
      },
    ];
  },
};

module.exports = nextConfig;