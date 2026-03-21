/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;

    return [
      {
        source: '/api/ask',
        destination: `${backendUrl}/ask`,
      },
      {
        source: '/api/health',
        destination: `${backendUrl}/health`,
      },
    ];
  },
};

module.exports = nextConfig;