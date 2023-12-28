# filename: arxiv_segmentation_papers.py
import requests
import feedparser
from datetime import datetime

# Current year
current_year = datetime.now().year

# arXiv API endpoint
ARXIV_API_URL = 'http://export.arxiv.org/api/query?'

# Search query parameters
search_query = 'cat:cs.CV AND ti:segmentation AND submittedDate:[{}01010000 TO {}12312359]'.format(current_year, current_year)
start = 0
max_results = 100
results = []

# Collect papers
while True:
    response = requests.get(ARXIV_API_URL, params={
        'search_query': search_query,
        'start': start,
        'max_results': max_results
    })
    feed = feedparser.parse(response.content)
    results.extend(feed.entries)
    if len(feed.entries) == 0:
        break
    start += max_results

# Categorize papers based on domain
domains = {}
for entry in results:
    domain = entry.arxiv_primary_category['term']
    if domain not in domains:
        domains[domain] = []
    domains[domain].append({
        'Title': entry.title,
        'Authors': ', '.join(author.name for author in entry.authors),
        'arXiv ID': entry.id.split('/abs/')[-1],
        'Date': entry.published,
        'URL': entry.id
    })

# Create markdown table
markdown_table = ""
for domain, papers in domains.items():
    markdown_table += f"## Domain: {domain}\n"
    markdown_table += "| Title | Authors | arXiv ID | Date | URL |\n"
    markdown_table += "| --- | --- | --- | --- | --- |\n"
    for paper in papers:
        markdown_table += f"| {paper['Title']} | {paper['Authors']} | {paper['arXiv ID']} | {paper['Date'][:10]} | [Link]({paper['URL']}) |\n"
    markdown_table += "\n"

# Save markdown table to a file
with open('segmentation_papers.md', 'w') as file:
    file.write(markdown_table)

print("Markdown table of segmentation papers has been saved to 'segmentation_papers.md'")