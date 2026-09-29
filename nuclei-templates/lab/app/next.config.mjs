/** @type {import('next').NextConfig} */
const nextConfig = {
  // sharp stays external so /api/lab-info can report the native library versions
  // the vulnerable ImageResponse path actually runs on.
  serverExternalPackages: ['sharp']
}

export default nextConfig
