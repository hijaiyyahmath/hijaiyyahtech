/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'export',
    basePath: '/hijaiyyahmath.org',
    assetPrefix: '/hijaiyyahmath.org/',
    trailingSlash: true,
    images: {
        unoptimized: true,
    },
    reactStrictMode: true,
};
module.exports = nextConfig;
