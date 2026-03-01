/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'export',
    basePath: '/hijaiyyahtech',
    assetPrefix: '/hijaiyyahtech/',
    trailingSlash: true,
    images: {
        unoptimized: true,
    },
    reactStrictMode: true,
};
module.exports = nextConfig;
