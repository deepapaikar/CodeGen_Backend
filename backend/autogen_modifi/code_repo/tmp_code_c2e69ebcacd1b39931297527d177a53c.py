import requests
import datetime
import xml.etree.ElementTree as ET

# Define the current year
current_year = datetime.datetime.now().year

# Define the base URL for the arXiv API
base_url = 'http://export.arxiv.org/api/query?'

# Define the search query parameters
search_query = 'cat:cs.CV AND ti:segmentation AND submittedDate:[{}0101 TO {}1231]'.format(current_year, current_year)
start = 0
max_results = 10

# Construct the full API request URL
url = base_url + 'search_query={}&start={}&max_results={}'.format(search_query, start, max_results)

# Send the GET request to the arXiv API
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the response XML
    root = ET.fromstring(response.content)
    
    # Namespace dictionary to use with the XML parser
    ns = {'arxiv': 'http://www.w3.org/2005/Atom'}
    
    # Find and print out the entries
    for entry in root.findall('arxiv:entry', ns):
        title = entry.find('arxiv:title', ns).text.strip()
        authors = [author.find('arxiv:name', ns).text for author in entry.findall('arxiv:author', ns)]
        published = entry.find('arxiv:published', ns).text
        summary = entry.find('arxiv:summary', ns).text.strip()
        link = entry.find('arxiv:link[@title="pdf"]', ns).attrib['href']
        
        print('Title:', title)
        print('Authors:', ', '.join(authors))
        print('Published:', published)
        print('Abstract:', summary)
        print('Link:', link)
        print('-' * 80)
else:
    print('Failed to retrieve results from arXiv API. Status code:', response.status_code)