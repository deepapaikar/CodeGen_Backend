import requests

# Search query for GPT-4
query = "GPT-4"
# Fetching the arXiv API
base_url = "http://export.arxiv.org/api/query?"
search_query = f"search_query={query}&sortBy=submittedDate&sortOrder=descending&max_results=1"

# Sending the API request
response = requests.get(base_url + search_query)

# Checking if the request was successful
if response.status_code == 200:
    # Extracting the paper data
    data = response.text
    start_index = data.find("<title>") + len("<title>")
    end_index = data.find("</title>")
    paper_title = data[start_index:end_index]
    paper_url = data[data.find("<id>") + len("<id>") : data.find("</id>")]
    print(f"Latest paper on GPT-4: '{paper_title}'")
    print(f"Paper URL: {paper_url}")
else:
    print("Error fetching the data from arXiv!")