# URL Shortener Solution

This solution shortens URLs using the is.gd API and is fully containerized with Docker.

## Project Structure

```
url-shortener/
├── Dockerfile
├── requirements.txt
├── url_shortener.py
├── urls.txt
└── README.md
```

## Design Considerations

### 1. **Rate Limiting**
- Implemented 0.2-second delay between requests to avoid being blocked by the API
- Handles 429 (rate limited) responses with exponential backoff

### 2. **Deduplication**
- Code identifies unique URLs while preserving first occurrence order
- Only shortens each unique URL once, improving efficiency

### 3. **Robust Error Handling**
- Automatic retries (3 attempts per URL)
- Request timeouts
- File not found handling
- Fallback to original URL if shortening fails

### 4. **Scalability**
- Works with 6 URLs or 600+ URLs
- Uses Session for HTTP connection reuse
- Visible progress during processing

### 5. **Security**
- Container runs as non-root user
- Input validation
- Safe file handling

## Usage Instructions

First unzip url_shortener.zip and move to url_shortener directory

```bash
unzip url_shortener.zip
cd url_shortener
```
### Option 1: Run with Docker

1. **Build the image:**
```bash
docker build -t url-shortener .
```

2. **Run with sample file:**
```bash
docker run url-shortener
```

3. **Run with your own URL file:**
```bash
# First copy your file to container or mount a volume
docker run -v /path/to/your/urls.txt:/app/urls.txt url-shortener python url_shortener.py urls.txt
```

### Option 2: Run locally

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Execute:**
```bash
python url_shortener.py urls.txt
```

## Input Format

The URL file should contain one URL per line:
```
https://example.com/very/long/url/1
https://example.com/very/long/url/2
```

## Output Format

```
https://is.gd/abc123, https://example.com/very/long/url/1
https://is.gd/def456, https://example.com/very/long/url/2
```

