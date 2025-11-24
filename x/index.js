const express = require('express');
const RSS = require('rss');
const NodeCache = require('node-cache');
require('dotenv').config();

const newsService = require('./services/newsService');

const app = express();
const PORT = process.env.PORT || 3000;

const cache = new NodeCache({ stdTTL: 600 });

app.get('/rss', async (req, res) => {
  try {
    const cacheKey = 'news-feed';
    let articles = cache.get(cacheKey);
    
    if (!articles) {
      articles = await newsService.fetchNews();
      cache.set(cacheKey, articles);
    }

    const feed = new RSS({
      title: 'Epstein & Diddy News Feed',
      description: 'Latest news about Epstein and Diddy',
      feed_url: `http://list-coin.com/rss`,
      site_url: 'http://list-coin.com',
      image_url: 'http://list-coin.com/logo.png',
      docs: 'http://list-coin.com/rss/docs.html',
      managingEditor: 'editor@list-coin.com',
      webMaster: 'webmaster@list-coin.com',
      copyright: '2025 List-Coin',
      language: 'en',
      pubDate: new Date().toUTCString(),
      ttl: '10'
    });

    articles.forEach(article => {
      feed.item({
        title: article.title,
        description: article.description,
        url: article.url,
        guid: article.url,
        author: article.source,
        date: article.publishedAt
      });
    });

    res.set('Content-Type', 'application/rss+xml');
    res.send(feed.xml());
  } catch (error) {
    console.error('Error generating RSS feed:', error);
    res.status(500).send('Error generating RSS feed');
  }
});

app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>RSS News Feed</title>
      <style>
        body { font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; }
        h1 { color: #333; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .info { background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }
      </style>
    </head>
    <body>
      <h1>Epstein & Diddy News RSS Feed</h1>
      <div class="info">
        <p>This service provides an RSS feed aggregating news about Epstein and Diddy from multiple sources.</p>
        <p><strong>RSS Feed URL:</strong> <a href="/rss">/rss</a></p>
        <p>Add this URL to your RSS reader to stay updated with the latest news.</p>
      </div>
    </body>
    </html>
  `);
});

app.listen(PORT, () => {
  console.log(`RSS Feed server running on port ${PORT}`);
  console.log(`Access the feed at: http://localhost:${PORT}/rss`);
});