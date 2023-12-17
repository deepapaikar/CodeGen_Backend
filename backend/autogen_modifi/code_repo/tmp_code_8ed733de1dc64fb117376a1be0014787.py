# Assume 'paper_list' is the list of papers obtained from the previous step
# For demonstration purposes, here is a mock list with sample data
paper_list = [
    {'title': 'Medical Image Segmentation with Deep Learning', 'authors': 'Author A, Author B', 'arxiv_id': '1234.56789', 'url': 'https://arxiv.org/abs/1234.56789'},
    {'title': 'Satellite Imagery Segmentation for Urban Planning', 'authors': 'Author C, Author D', 'arxiv_id': '9876.54321', 'url': 'https://arxiv.org/abs/9876.54321'},
    # ... more papers
]

# Define domain keywords to categorize papers
domain_keywords = {
    'Medical': ['medical', 'health', 'clinical', 'patient'],
    'Satellite Imagery': ['satellite', 'remote sensing', 'earth observation'],
    'Autonomous Driving': ['autonomous', 'driving', 'vehicle', 'car'],
    # ... more domains
}

# Function to determine the domain of a paper based on its title
def determine_domain(title):
    for domain, keywords in domain_keywords.items():
        if any(keyword.lower() in title.lower() for keyword in keywords):
            return domain
    return 'Other'

# Categorize papers by domain
categorized_papers = {}
for paper in paper_list:
    domain = determine_domain(paper['title'])
    if domain not in categorized_papers:
        categorized_papers[domain] = []
    categorized_papers[domain].append(paper)

# Create a markdown table
markdown_table = "| Domain | Title | Authors | arXiv ID | URL |\n"
markdown_table += "|--------|-------|---------|----------|-----|\n"

for domain, papers in categorized_papers.items():
    for paper in papers:
        markdown_table += f"| {domain} | {paper['title']} | {paper['authors']} | arXiv:{paper['arxiv_id']} | [Link]({paper['url']}) |\n"

# Output the markdown table
print(markdown_table)