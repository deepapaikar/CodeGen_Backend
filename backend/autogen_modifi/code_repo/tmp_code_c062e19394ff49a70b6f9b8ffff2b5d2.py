import requests
import datetime
import xml.etree.ElementTree as ET

# Define the current year
current_year = datetime.datetime.now().year

# Define the ArXiv API endpoint for searching
arxiv_api_endpoint = "http://export.arxiv.org/api/query"

# Define the search query parameters
search_query = f"all:segmentation AND submittedDate:[{current_year}01010000 TO {current_year}12312359]"
start = 0
max_results = 100  # Adjust as needed, keeping in mind potential API rate limits
results_per_iteration = 100  # Adjust based on how many results you want per API call

# Initialize the list to store paper information
papers = []

# Fetch papers in batches to avoid hitting rate limits
while True:
    params = {
        "search_query": search_query,
        "start": start,
        "max_results": results_per_iteration,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    response = requests.get(arxiv_api_endpoint, params=params)
    if response.status_code != 200:
        print(f"Error fetching data from ArXiv: {response.status_code}")
        break

    # Parse the response using ElementTree
    root = ET.fromstring(response.content)

    # Check if there are no more results
    if not root.findall('{http://www.w3.org/2005/Atom}entry'):
        break

    # Process each entry (paper)
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        # Extract relevant information
        title = entry.find('{http://www.w3.org/2005/Atom}title').text
        authors = ", ".join(author.find('{http://www.w3.org/2005/Atom}name').text for author in entry.findall('{http://www.w3.org/2005/Atom}author'))
        published = entry.find('{http://www.w3.org/2005/Atom}published').text
        link = entry.find('{http://www.w3.org/2005/Atom}id').text

        paper_info = {
            "Title": title,
            "Authors": authors,
            "Date": published,
            "Domain": "TBD",  # Placeholder for domain, which needs to be categorized manually or with additional logic
            "ArXiv_Link": link
        }
        papers.append(paper_info)

    # Prepare for the next batch
    start += results_per_iteration

# Create a markdown table
markdown_table = "| Title | Authors | Date | Domain | ArXiv Link |\n"
markdown_table += "| --- | --- | --- | --- | --- |\n"
for paper in papers:
    markdown_table += f"| {paper['Title']} | {paper['Authors']} | {paper['Date']} | {paper['Domain']} | [Link]({paper['ArXiv_Link']}) |\n"

# Output the markdown table
print(markdown_table)