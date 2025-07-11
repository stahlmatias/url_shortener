# url_shortener.py
import requests
import sys
import time
from typing import Set, Dict
import click

class URLShortener:

    def __init__(self, rate_limit_delay: float = 0.1):
        """
        Initialize URL shortener with rate limiting
        
        Args:
            rate_limit_delay: Delay between API calls in seconds
        """
        self.base_url = "https://is.gd/create.php"
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        
    def read_urls_from_file(self, filename: str) -> list:
        """
        Read URLs from file, one per line
        
        Args:
            filename: Path to file containing URLs
            
        Returns:
            List of URLs (strings)
        """
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                urls = [line.strip() for line in file if line.strip()]
            print(f"Read {len(urls)} URLs from {filename}")
            return urls
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)
    
    def get_unique_urls(self, urls: list) -> list:
        """
        Get unique URLs while preserving order of first occurrence
        
        Args:
            urls: List of URLs
            
        Returns:
            List of unique URLs
        """
        seen: Set[str] = set()
        unique_urls = []
        
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        print(f"Found {len(unique_urls)} unique URLs out of {len(urls)} total")
        return unique_urls
    
    def shorten_url(self, url: str, retries: int = 3) -> str:
        """
        Shorten a single URL using is.gd API
        
        Args:
            url: URL to shorten
            retries: Number of retry attempts
            
        Returns:
            Shortened URL or original URL if failed
        """
        params = {
            'format': 'simple',
            'url': url
        }
        
        for attempt in range(retries):
            try:
                # Rate limiting
                time.sleep(self.rate_limit_delay)
                
                response = self.session.get(self.base_url, params=params, timeout=10)
                
                if response.status_code == 200:
                    shortened = response.text.strip()
                    
                    # Check if response is actually a shortened URL
                    if shortened.startswith('https://is.gd/'):
                        return shortened
                    else:
                        print(f"Warning: Unexpected response for {url}: {shortened}")
                        return url

                # Check for rate limit
                # The status code according to https://is.gd/apishorteningreference.php
                # is 501 when rate limit has been exceeded
                elif response.status_code == 502:
                    # Rate limited, wait longer
                    wait_time = (attempt + 1) * 2
                    print(f"Rate limited. Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                    
                else:
                    print(f"HTTP {response.status_code} for {url}")
                    
            except requests.exceptions.RequestException as e:
                print(f"Request error for {url} (attempt {attempt + 1}): {e}")
                if attempt < retries - 1:
                    time.sleep((attempt + 1) * 2)
        
        print(f"Failed to shorten {url} after {retries} attempts")
        return url
    
    def process_urls(self, urls: list) -> Dict[str, str]:
        """
        Process list of URLs and return mapping of shortened to original
        
        Args:
            urls: List of URLs to process
            
        Returns:
            Dictionary mapping shortened URLs to original URLs
        """
        unique_urls = self.get_unique_urls(urls)
        results = {}
        
        print(f"\nProcessing {len(unique_urls)} unique URLs...")
        
        for i, url in enumerate(unique_urls, 1):
            print(f"Processing {i}/{len(unique_urls)}: {url[:60]}...")
            shortened = self.shorten_url(url)
            results[shortened] = url
            
        return results
    
    def format_output(self, results: Dict[str, str]) -> None:
        """
        Format and print results to console
        
        Args:
            results: Dictionary of shortened -> original URL mappings
        """
        print("\n" + "="*50)
        print("RESULTS:")
        print("="*50)
        
        for shortened, original in results.items():
            print(f"{shortened}, {original}")

@click.command()
@click.option('--filename', default="urls.txt", help='Path to file with URLs')

def main(filename: str):
    """Main function"""

    # Initialize shortener with rate limiting
    shortener = URLShortener(rate_limit_delay=0.2)
    
    # Read URLs from file
    urls = shortener.read_urls_from_file(filename)

    if not urls:
        print("No URLs found in file")
        sys.exit(1)
    
    # Process URLs
    results = shortener.process_urls(urls)
    
    # Output results
    shortener.format_output(results)

if __name__ == "__main__":
    main()
