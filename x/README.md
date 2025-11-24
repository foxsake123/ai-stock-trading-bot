# RSS News Feed for List-Coin.com

This application creates an RSS feed that aggregates news about Epstein and Diddy from multiple sources.

## Features

- Aggregates news from multiple sources (NewsAPI, Google News)
- Caches results to reduce API calls (10-minute cache by default)
- Removes duplicate articles
- Sorts articles by publication date
- Provides standard RSS 2.0 format feed
- Simple web interface to access the feed

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Add your NewsAPI key (get one free at https://newsapi.org/register)

3. Start the server:
```bash
npm start
```

4. Access the RSS feed at:
   - Web interface: `http://localhost:3000`
   - RSS feed: `http://localhost:3000/rss`

## Deployment to list-coin.com

To deploy this to list-coin.com, you'll need to:

1. **Set up a subdomain or path**: Configure your web server (Apache/Nginx) to route traffic from list-coin.com/rss to this Node.js application

2. **Use a process manager**: Install PM2 to keep the app running:
```bash
npm install -g pm2
pm2 start index.js --name "rss-feed"
pm2 save
pm2 startup
```

3. **Configure reverse proxy** (Nginx example):
```nginx
location /rss {
    proxy_pass http://localhost:3000/rss;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
}
```

4. **Set environment variables on the server**:
   - Create `.env` file with your production NewsAPI key
   - Optionally set a different PORT if needed

## API Rate Limits

- NewsAPI: Free tier allows 100 requests per day
- Google News RSS: No official rate limit but be respectful
- The app caches results for 10 minutes to minimize API calls

## Customization

You can modify the search terms in `services/newsService.js`:
```javascript
const SEARCH_TERMS = ['Epstein', 'Diddy', 'Sean Combs', 'P Diddy'];
```

## Security Notes

- Never commit your `.env` file with API keys
- Consider adding rate limiting for production use
- Use HTTPS in production

## License

ISC