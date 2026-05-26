# Platform Compliance Notes

This project is a dataset builder, not a scraping bypass tool.

## X

Use the official X API when available. For public sharing, prefer Post IDs,
URLs, and labels instead of hydrated post objects or downloaded media.

Relevant policy pages:

- https://docs.x.com/developer-terms/policy
- https://docs.x.com/developer-guidelines

## YouTube

Use YouTube Data API with your own API key. Store only what your research use
requires. Link back to YouTube pages and avoid redistributing video files.

Relevant policy page:

- https://developers.google.com/youtube/terms/api-services-terms-of-service

## TikTok

Use approved Research API access when available. Without approved access, use
manual public-page records only and do not automate scraping at scale.

Relevant policy page:

- https://www.tiktok.com/legal/page/global/terms-of-service-research-api/en

## Public Repository Rule

The public repository should contain:

- code
- schema
- templates
- public-safe manifests
- source URLs
- label-source URLs

It should not contain:

- API keys
- downloaded videos
- bulk platform content dumps
- personal or sensitive data
- private user information
