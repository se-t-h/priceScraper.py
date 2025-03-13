# Auto Parts Price Scraper

A multithreaded tool to find the best prices for automotive parts across multiple dealership websites. Currently supports Lexus and Subaru dealerships.

![Auto Parts Price Scraper Banner](https://shields.io/badge/Auto%20Parts-Price%20Scraper-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Price Comparison**: Automatically scrapes part prices from hundreds of dealerships
- **Brand Support**: Currently works with Lexus and Subaru dealers
- **Multithreaded**: Fast operation with configurable thread count
- **Proxy Support**: Works with SOCKS5 proxies for better reliability
- **Sorted Results**: Shows results sorted from lowest to highest price
- **ZIP Codes**: Displays dealer ZIP code for shipping estimation

## Installation

### Prerequisites

- Python 3.6+
- Required Python packages:
  - requests
  - urllib3

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/auto-parts-price-scraper.git
   cd auto-parts-price-scraper
   ```

2. Install the required dependencies:
   ```bash
   pip install requests urllib3
   ```

3. Make the script executable (Linux/Mac):
   ```bash
   chmod +x auto_parts_scraper.py
   ```

## Usage

Basic usage pattern:
```bash
python auto_parts_scraper.py PART_NUMBER --proxy USER:PASS@HOST:PORT --brand BRAND
```

### Example

```bash
# Search for a Lexus oil filter
python auto_parts_scraper.py 04152YZZA5 --proxy user:pass@proxy.example.com:7000 --brand lexus

# Search for a Subaru air filter
python auto_parts_scraper.py 15208AA170 --proxy user:pass@proxy.example.com:7000 --brand subaru
```

### Command-line Arguments

| Argument | Description |
|----------|-------------|
| `PART_NUMBER` | The part number to search for (required) |
| `-p, --proxy` | SOCKS5 proxy in format user:pass@host:port (required) |
| `-b, --brand` | Brand to search: 'lexus' or 'subaru' (default: 'lexus') |
| `-t, --threads` | Number of concurrent threads (default: 20) |
| `-r, --retries` | Maximum retries per dealer (default: 3) |

## Output

The script outputs results in real-time showing:
- Success/failure status for each dealer check
- A sorted list of dealers with the lowest prices first
- The dealer's ZIP code for shipping calculation (when available)

Example output:
```
[ LEXUS BOT | made by seth ]

part number: 04152YZZA5

fetching prices using 20 threads...
parkerlexus.com - 92882 [$21.99] [✓]
lexusofsantabarbara.com - 93103 [$22.50] [✓]
lexusoftulsa.com - 74145 [$23.12] [✓]
...

=== LEXUS Results (Sorted by Price) ===
[1] parts.parkerlexus.com/productSearch.aspx?searchTerm=04152YZZA5 ... 92882 ... $21.99
[2] parts.lexusofsantabarbara.com/productSearch.aspx?searchTerm=04152YZZA5 ... 93103 ... $22.50
[3] parts.lexusoftulsa.com/productSearch.aspx?searchTerm=04152YZZA5 ... 74145 ... $23.12
```

## Extending

### Adding More Dealers

You can add more dealers by extending the `LEXUS_DEALERS` or `SUBARU_DEALERS` arrays in the script.

### Adding New Brands

To add support for a new brand:

1. Add a new dealer array (e.g., `TOYOTA_DEALERS = [...]`)
2. Add the brand to the choices in `setup_argparse()`
3. Add a condition in the `main()` function to select the appropriate dealer list

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational purposes only. Always respect the terms of service for websites you interact with. Some websites may prohibit automated access or scraping.

## Credits

- Created by Seth
- Improved version with multithreading and brand support
