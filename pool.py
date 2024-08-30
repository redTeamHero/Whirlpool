import argparse
import asyncio
import re
import sys
import time

import httpx
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

init(autoreset=True)

class Scraper:
    def __init__(self, method, _url):
        self.method = method
        self._url = _url

    def get_url(self, **kwargs):
        return self._url.format(**kwargs, method=self.method)

    async def get_response(self, client):
        return await client.get(self.get_url())

    async def handle(self, response):
        return response.text

    async def scrape(self, client):
        response = await self.get_response(client)
        proxies = await self.handle(response)
        pattern = re.compile(r"\d{1,3}(?:\.\d{1,3}){3}(?::\d{1,5})?")
        return re.findall(pattern, proxies)

class SpysMeScraper(Scraper):
    def __init__(self, method):
        super().__init__(method, "https://spys.me/{mode}.txt")

    def get_url(self, **kwargs):
        mode = "proxy" if self.method == "http" else "socks" if self.method in ["socks4", "socks5"] else "unknown"
        if mode == "unknown":
            raise NotImplementedError
        return super().get_url(mode=mode, **kwargs)

class ProxyScrapeScraper(Scraper):
    def __init__(self, method, timeout=1000, country="All"):
        self.timeout = timeout
        self.country = country
        super().__init__(method,
                         "https://api.proxyscrape.com/?request=getproxies"
                         "&proxytype={method}"
                         "&timeout={timeout}"
                         "&country={country}")

    def get_url(self, **kwargs):
        return super().get_url(timeout=self.timeout, country=self.country, **kwargs)

class GeoNodeScraper(Scraper):
    def __init__(self, method, limit="500", page="1", sort_by="lastChecked", sort_type="desc"):
        self.limit = limit
        self.page = page
        self.sort_by = sort_by
        self.sort_type = sort_type
        super().__init__(method,
                         "https://proxylist.geonode.com/api/proxy-list?"
                         "&limit={limit}"
                         "&page={page}"
                         "&sort_by={sort_by}"
                         "&sort_type={sort_type}")

    def get_url(self, **kwargs):
        return super().get_url(limit=self.limit, page=self.page, sort_by=self.sort_by, sort_type=self.sort_type, **kwargs)

class ProxyListDownloadScraper(Scraper):
    def __init__(self, method, anon):
        self.anon = anon
        super().__init__(method, "https://www.proxy-list.download/api/v1/get?type={method}&anon={anon}")

    def get_url(self, **kwargs):
        return super().get_url(anon=self.anon, **kwargs)

class GeneralTableScraper(Scraper):
    async def handle(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        proxies = set()
        table = soup.find("table", attrs={"class": "table table-striped table-bordered"})
        for row in table.findAll("tr"):
            count = 0
            proxy = ""
            for cell in row.findAll("td"):
                if count == 1:
                    proxy += ":" + cell.text.replace("&nbsp;", "")
                    proxies.add(proxy)
                    break
                proxy += cell.text.replace("&nbsp;", "")
                count += 1
        return "\n".join(proxies)

class GeneralDivScraper(Scraper):
    async def handle(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        proxies = set()
        table = soup.find("div", attrs={"class": "list"})
        for row in table.findAll("div"):
            count = 0
            proxy = ""
            for cell in row.findAll("div", attrs={"class": "td"}):
                if count == 2:
                    break
                proxy += cell.text + ":"
                count += 1
            proxy = proxy.rstrip(":")
            proxies.add(proxy)
        return "\n".join(proxies)
    
class GitHubScraper(Scraper):
    async def handle(self, response):
        tempproxies = response.text.split("\n")
        proxies = set()
        for prxy in tempproxies:
            if self.method in prxy:
                proxies.add(prxy.split("//")[-1])
        return "\n".join(proxies)




# Initialize scrapers for all required methods
scrapers = [
    # Existing scrapers
    SpysMeScraper("http"),
    SpysMeScraper("socks4"),
    SpysMeScraper("socks5"),
    ProxyScrapeScraper("http"),
    ProxyScrapeScraper("socks4"),
    ProxyScrapeScraper("socks5"),
    GeoNodeScraper("socks4"),
    ProxyListDownloadScraper("https", "elite"),
    ProxyListDownloadScraper("http", "elite"),
    ProxyListDownloadScraper("http", "transparent"),
    ProxyListDownloadScraper("http", "anonymous"),
    GeneralTableScraper("http", "http://sslproxies.org"),
    GeneralTableScraper("http", "http://free-proxy-list.net"),
    GeneralTableScraper("http", "http://us-proxy.org"),
    GeneralTableScraper("socks4", "http://socks-proxy.net"),
    GeneralDivScraper("http", "https://freeproxy.lunaproxy.com/"),
    GitHubScraper("http", "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt"),
    GitHubScraper("socks4", "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt"),
    GitHubScraper("socks5", "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt"),
    GitHubScraper("http", "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt"),
    GitHubScraper("socks4", "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt"),
    GitHubScraper("socks5", "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt"),
    GitHubScraper("https", "https://raw.githubusercontent.com/zloi-user/hideip.me/main/https.txt"),
    GitHubScraper("http", "https://raw.githubusercontent.com/zloi-user/hideip.me/main/http.txt"),
    GitHubScraper("socks4", "https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks4.txt"),
    GitHubScraper("socks5", "https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks5.txt"),
    GitHubScraper("http", "https://github.com/Zaeem20/FREE_PROXIES_LIST/blob/master/http.txt"),
    GitHubScraper("https", "https://github.com/Zaeem20/FREE_PROXIES_LIST/blob/master/https.txt"),
    GitHubScraper("socks4", "https://github.com/Zaeem20/FREE_PROXIES_LIST/blob/master/socks4.txt"),
    GitHubScraper("http", "https://github.com/TheSpeedX/PROXY-List/blob/master/http.txt"),
    GitHubScraper("socks4", "https://github.com/TheSpeedX/PROXY-List/blob/master/socks4.txt"),
    GitHubScraper("socks5", "https://github.com/TheSpeedX/PROXY-List/blob/master/socks5.txt"),
    GitHubScraper("http", "https://github.com/mmpx12/proxy-list/blob/master/http.txt"),
    GitHubScraper("https", "https://github.com/mmpx12/proxy-list/blob/master/https.txt"),
    GitHubScraper("socks4", "https://github.com/mmpx12/proxy-list/blob/master/socks4.txt"),
    

]


def verbose_print(verbose, message, color=Fore.WHITE):
    if verbose:
        print(color + message)

def sanitize_proxy(proxy):
    # Remove unwanted characters and ensure the format is correct
    proxy = proxy.strip()
    if ':' in proxy:
        try:
            ip, port = proxy.split(":")
            ip = ip.strip()
            port = port.strip()
            return f"{ip}:{port}"
        except ValueError:
            return None
    return None

async def scrape(method, output, ip_ports_output, verbose):
    now = time.time()
    methods = [method]
    if method == "socks":
        methods += ["socks4", "socks5"]
    proxy_scrapers = [s for s in scrapers if s.method in methods]
    if not proxy_scrapers:
        raise ValueError("Method not supported")
    verbose_print(verbose, "Scraping proxies...", Fore.YELLOW)
    proxies = []

    tasks = []
    client = httpx.AsyncClient(follow_redirects=True)

    async def scrape_scraper(scraper):
        try:
            verbose_print(verbose, f"Looking {scraper.get_url()}...", Fore.CYAN)
            raw_proxies = await scraper.scrape(client)
            for proxy in raw_proxies:
                sanitized_proxy = sanitize_proxy(proxy)
                if sanitized_proxy:
                    proxies.append(sanitized_proxy)
                else:
                    verbose_print(verbose, f"Skipping malformed proxy: {proxy}", Fore.RED)
        except Exception as e:
            verbose_print(verbose, f"Error scraping {scraper.get_url()}: {e}", Fore.RED)

    for scraper in proxy_scrapers:
        tasks.append(asyncio.ensure_future(scrape_scraper(scraper)))

    await asyncio.gather(*tasks)
    await client.aclose()

    proxies = set(proxies)
    verbose_print(verbose, f"Writing {len(proxies)} proxies to file...", Fore.YELLOW)

    with open(output, "w") as f, open(ip_ports_output, "w") as ip_ports_f:
        for proxy in proxies:
            proxy = proxy.strip()  # Remove any extra whitespace
            if ':' in proxy:
                try:
                    ip, port = proxy.split(":")
                    # Write full proxy to output file
                    protocol = method.lower() if method != "socks" else "socks4"
                    f.write(f"{protocol} {ip} {port}\n")
                    # Write IP and port to ip_ports file
                    ip_ports_f.write(f"{ip}:{port}\n")
                except ValueError:
                    verbose_print(verbose, f"Skipping malformed proxy: {proxy}", Fore.RED)
            else:
                verbose_print(verbose, f"Skipping malformed proxy: {proxy}", Fore.RED)

    verbose_print(verbose, f"Scraped proxies saved to {output} and IP/port saved to {ip_ports_output} in {round(time.time() - now, 2)} seconds", Fore.GREEN)

async def main(args):
    while True:
        try:
            await scrape(args.proxy, args.output, args.ip_ports_output, args.verbose)
            if args.cycle:
                verbose_print(args.verbose, f"Waiting {args.cycle} seconds before rescraping...", Fore.YELLOW)
                await asyncio.sleep(args.cycle)
            else:
                break
        except Exception as e:
            print(Fore.RED + f"Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape and validate proxies.")
    parser.add_argument("-p", "--proxy", required=True, choices=["http", "https", "socks4", "socks5"], help="Type of proxy to scrape.")
    parser.add_argument("-o", "--output", default="proxies.txt", help="File to save the scraped proxies.")
    parser.add_argument("-i", "--ip_ports_output", default="ip_ports.txt", help="File to save IP and ports.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output.")
    parser.add_argument("--cycle", type=int, help="Time in seconds to wait before rescraping proxies.")
    
    args = parser.parse_args()

    asyncio.run(main(args))
