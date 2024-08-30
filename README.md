![whirlpool](https://github.com/user-attachments/assets/6e9ecac3-6b9d-496a-b793-b8c8e6885849)


This code is a proxy scraper that asynchronously gathers proxy IP addresses from multiple online sources. It organizes the proxies by type (HTTP, HTTPS, SOCKS4, SOCKS5), sanitizes the data to ensure it's in a usable format, and saves the proxy IP addresses and ports into specified output files. 

Key features include:

1. **Scraping Proxies**: Different subclasses (`SpysMeScraper`, `ProxyScrapeScraper`, `GeoNodeScraper`, etc.) are used to scrape proxies from different websites and APIs.

2. **Asynchronous Operations**: The code uses `asyncio` to perform multiple network requests concurrently, which speeds up the scraping process.

3. **Data Extraction and Validation**: Regular expressions (`re`) and `BeautifulSoup` are used to parse and extract proxy data from raw HTML or text responses. The proxies are then sanitized to ensure they are in the correct format.

4. **Command-Line Interface**: `argparse` is used to allow users to specify proxy types, output file names, and other options through command-line arguments.

5. **Output**: The script saves the valid proxies to a file (`proxies.txt`) and a separate file for IP and port combinations (`ip_ports.txt`).

6. **Verbose Logging**: The script can provide detailed logging in the terminal, showing progress and errors with color-coded messages using `colorama`.

7. **Cycle Option**: The script can continuously scrape proxies at specified intervals if the `--cycle` argument is provided, allowing for ongoing proxy list updates. 

Overall, this script is designed to efficiently scrape, validate, and manage proxies from various sources for use in applications that require anonymity or bypassing network restrictions.


Here are some example commands to run the proxy scraper script, based on the command-line arguments defined in the code:

1. **Basic HTTP Proxy Scraping**: Scrape HTTP proxies and save them to the default files (`proxies.txt` and `ip_ports.txt`).
   ```bash
   python script_name.py -p http
   ```

2. **HTTPS Proxy Scraping with Verbose Output**: Scrape HTTPS proxies, save to default files, and enable detailed logging in the terminal.
   ```bash
   python script_name.py -p https -v
   ```

3. **SOCKS4 Proxy Scraping with Custom Output Files**: Scrape SOCKS4 proxies and save the results to custom output files (`socks4_proxies.txt` and `socks4_ip_ports.txt`).
   ```bash
   python script_name.py -p socks4 -o socks4_proxies.txt -i socks4_ip_ports.txt
   ```

4. **Scrape SOCKS5 Proxies and Repeat Every 60 Seconds**: Continuously scrape SOCKS5 proxies every 60 seconds.
   ```bash
   python script_name.py -p socks5 --cycle 60
   ```

5. **Scrape All Proxy Types (HTTP, HTTPS, SOCKS4, SOCKS5) in Verbose Mode**: If the script is modified to support a combined `socks` mode, scrape all types of SOCKS proxies and enable verbose output.
   ```bash
   python script_name.py -p socks -v
   ```

6. **Scrape HTTPS Proxies and Save to a Custom Output File**: Save scraped HTTPS proxies to a specific file named `custom_https_proxies.txt`.
   ```bash
   python script_name.py -p https -o custom_https_proxies.txt
   ```

Replace `script_name.py` with the actual name of the script file. These examples cover various use cases for scraping different proxy types, customizing output files, enabling verbose logging, and setting up continuous scraping intervals.
