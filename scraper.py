import requests
from bs4 import BeautifulSoup

def scrape_site(url, keywords):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    articles = []
    for article in soup.find_all('article'):
        title = article.find('h2').get_text() if article.find('h2') else ""
        link = article.find('a')['href'] if article.find('a') else ""
        summary = article.find('p').get_text() if article.find('p') else ""

        if any(keyword.lower() in title.lower() or keyword.lower() in summary.lower() for keyword in keywords):
            articles.append({
                'title': title,
                'url': link,
                'summary': summary
            })

    print(f"Scraped from {url}: {articles}")
    return articles

def scrape_articles(keywords):
    sites = [
        "https://techcrunch.com",
        "https://thenextweb.com",
        "https://www.theverge.com",
        "https://www.wired.com",
        "https://www.engadget.com",
        "https://www.digitaltrends.com",
        "https://www.techradar.com",
        "https://www.cnet.com",
        "https://www.zdnet.com",
        "https://www.pcworld.com",
        "https://www.tomshardware.com",
        "https://www.techrepublic.com",
        "https://www.techspot.com",
        "https://www.technewsworld.com",
        "https://www.techworld.com",
        "https://www.techopedia.com",
        "https://www.technotification.com",
        "https://www.techgenyz.com",
        "https://www.techadvisor.com",
        "https://www.techfunnel.com",
        "https://martech.org",
        "https://www.socialmediatoday.com",
        "https://www.socialmediaexaminer.com",
        "https://www.socialbakers.com",
        "https://www.socialmediaweek.org",
        "https://www.socialmediatoday.com",
        "https://www.neurosciencemarketing.com/blog"
        "https://blog.hubspot.com"
        # Ajoutez d'autres sites ici
    ]

    all_articles = []
    for site in sites:
        articles = scrape_site(site, keywords)
        all_articles.extend(articles)

    return all_articles
