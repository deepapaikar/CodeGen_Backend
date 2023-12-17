import requests
import datetime
from urllib.parse import quote

# Current year
current_year = datetime.datetime.now().year

# arXiv API endpoint
ARXIV_API_URL = "http://export.arxiv.org/api/query?"

# Search parameters
search_query = f"cat:cs.CV AND abs:segmentation AND submittedDate:[{current_year}01010000 TO {current_year}12312359]"
start = 0
max_results = 100
results = []

# Collect papers
while True:
    query = f"search_query={quote(search_query)}&start={start}&max_results={max_results}"
    response = requests.get(ARXIV_API_URL + query)
    if response.status_code != 200:
        print("Failed to fetch data from arXiv")
        break
    
    feed = response.text
    entries = feed.count('<entry>')
    
    if entries == 0:
        break
    
    results.append(feed)
    start += entries

# Process results and create markdown table
markdown_table = "| Title | Authors | arXiv Link | Domain |\n"
markdown_table += "|-------|---------|------------|--------|\n"

for result in results:
    # Extract paper information from the result
    # This is a simplified extraction process and assumes the XML is well-formed and simple
    while '<entry>' in result:
        entry_start = result.find('<entry>')
        entry_end = result.find('</entry>') + len('</entry>')
        entry = result[entry_start:entry_end]
        
        # Extract title
        title_start = entry.find('<title>') + len('<title>')
        title_end = entry.find('</title>')
        title = entry[title_start:title_end].strip().replace('\n', ' ')
        
        # Extract authors
        authors = []
        author_start = entry.find('<author>')
        while author_start != -1:
            author_end = entry.find('</author>') + len('</author>')
            author_entry = entry[author_start:author_end]
            name_start = author_entry.find('<name>') + len('<name>')
            name_end = author_entry.find('</name>')
            authors.append(author_entry[name_start:name_end].strip())
            author_start = entry.find('<author>', author_end)
        
        # Extract arXiv ID
        id_start = entry.find('<id>') + len('<id>')
        id_end = entry.find('</id>')
        arxiv_id = entry[id_start:id_end].strip().split('/')[-1]
        
        # Extract domain (simplified to 'Computer Vision' for all cs.CV papers)
        domain = 'Computer Vision'
        
        # Append to markdown table
        markdown_table += f"| {title} | {', '.join(authors)} | [arXiv:{arxiv_id}](https://arxiv.org/abs/{arxiv_id}) | {domain} |\n"
        
        # Move to the next entry
        result = result[entry_end:]

# Output the markdown table
print(markdown_table)