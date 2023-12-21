# filename: arxiv_segmentation_papers.py

import requests
import datetime
from collections import defaultdict

# Function to query the arXiv API
def query_arxiv(search_query, start=0, max_results=100):
    url = 'http://export.arxiv.org/api/query'
    params = {
        'search_query': search_query,
        'start': start,
        'max_results': max_results,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Error while querying arXiv API: {response.content}")
    return response.text

# Function to parse the arXiv API response and extract relevant information
def parse_arxiv_response(response_text):
    from xml.etree import ElementTree as ET
    ns = {'arxiv': 'http://arxiv.org/schemas/atom'}
    root = ET.fromstring(response_text)
    entries = root.findall('arxiv:entry', ns)
    
    papers = []
    for entry in entries:
        title = entry.find('arxiv:title', ns).text.strip()
        arxiv_id = entry.find('arxiv:id', ns).text.split('/')[-1]
        published = entry.find('arxiv:published', ns).text.split('T')[0]
        authors = [author.find('arxiv:name', ns).text for author in entry.findall('arxiv:author', ns)]
        summary = entry.find('arxiv:summary', ns).text.strip()
        categories = [category.attrib['term'] for category in entry.findall('arxiv:category', ns)]
        
        papers.append({
            'title': title,
            'arxiv_id': arxiv_id,
            'published': published,
            'authors': authors,
            'summary': summary,
            'categories': categories
        })
    return papers

# Function to categorize papers by domain
def categorize_papers(papers):
    domain_keywords = {
        'Computer Vision': ['cs.CV', 'cs.LG', 'cs.AI'],
        'Medical': ['q-bio', 'cs.CY', 'eess.IV'],
        'Natural Language Processing': ['cs.CL', 'cs.LG', 'cs.AI'],
        'Robotics': ['cs.RO', 'cs.AI'],
        'Other': []
    }
    
    categorized_papers = defaultdict(list)
    for paper in papers:
        found = False
        for domain, keywords in domain_keywords.items():
            if any(keyword in paper['categories'] for keyword in keywords):
                categorized_papers[domain].append(paper)
                found = True
                break
        if not found:
            categorized_papers['Other'].append(paper)
    return categorized_papers

# Function to create a markdown table from the categorized papers
def create_markdown_table(categorized_papers):
    markdown_table = ""
    for domain, papers in categorized_papers.items():
        markdown_table += f"## {domain}\n"
        markdown_table += "| Title | Authors | arXiv ID | Date | URL |\n"
        markdown_table += "|-------|---------|----------|------|-----|\n"
        for paper in papers:
            authors = ', '.join(paper['authors'])
            url = f"https://arxiv.org/abs/{paper['arxiv_id']}"
            markdown_table += f"| {paper['title']} | {authors} | {paper['arxiv_id']} | {paper['published']} | [Link]({url}) |\n"
        markdown_table += "\n"
    return markdown_table

# Main function to execute the workflow
def main():
    current_year = datetime.datetime.now().year
    search_query = f'all:segmentation AND submittedDate:[{current_year}01010000 TO {current_year}12312359]'
    response_text = query_arxiv(search_query)
    papers = parse_arxiv_response(response_text)
    categorized_papers = categorize_papers(papers)
    markdown_table = create_markdown_table(categorized_papers)
    print(markdown_table)

if __name__ == "__main__":
    main()