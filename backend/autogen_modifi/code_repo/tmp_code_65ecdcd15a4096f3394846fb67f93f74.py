import requests
import datetime
import xml.etree.ElementTree as ET

# Define the current year
current_year = datetime.datetime.now().year

# Define the search query parameters
params = {
    'search_query': f'all:segmentation AND submittedDate:[{current_year}0101 TO {current_year}1231]',
    'start': 0,
    'max_results': 100,
    'sortBy': 'submittedDate',
    'sortOrder': 'descending'
}

# URL for the arXiv API
api_url = 'http://export.arxiv.org/api/query'

# Make the request to the arXiv API
response = requests.get(api_url, params=params)

# Check if the request was successful
if response.status_code == 200:
    # Parse the response XML
    root = ET.fromstring(response.content)
    
    # Namespace for parsing the arXiv XML response
    namespace = {'arxiv': 'http://arxiv.org/schemas/atom'}
    
    # Create a list to hold the paper information
    paper_list = []
    
    # Process the entries in the XML
    for entry in root.findall('arxiv:entry', namespace):
        # Extract relevant information
        title = entry.find('arxiv:title', namespace).text.strip()
        authors = ', '.join(author.find('arxiv:name', namespace).text for author in entry.findall('arxiv:author', namespace))
        arxiv_id = entry.find('arxiv:id', namespace).text.split('/abs/')[-1]
        url = entry.find('arxiv:id', namespace).text
        
        # Add the paper information to the list
        paper_list.append({
            'title': title,
            'authors': authors,
            'arxiv_id': arxiv_id,
            'url': url
        })
    
    # Output the list of papers (this will be processed further in the next step)
    for paper in paper_list:
        print(paper)
else:
    print(f"Failed to fetch data from arXiv API. Status code: {response.status_code}")