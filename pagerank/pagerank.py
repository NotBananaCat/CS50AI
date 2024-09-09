import os
import random
import re
import sys
import time

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")




def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    next_page_probabilities = {}
  
    if len(corpus[page]) == 0:
        corpus_pages = corpus.keys()
    else:
        corpus_pages = corpus[page]

    #0.15 pick random page
    random_page_probability = (1 - damping_factor) / len(corpus)

    for p in corpus:
        next_page_probabilities[p] = random_page_probability

    #0.85 pick linked page
    link_probability = damping_factor / len(corpus_pages)

    for p in corpus_pages:
        next_page_probabilities[p] += link_probability

    return next_page_probabilities



def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank = {}
    current_page = random.choice(list(corpus.keys()))

    for page in corpus:
        pagerank[page] = 0

    for x in range(n):
        pagerank[current_page] += 1 #visited page
        transition_probabilities = transition_model(corpus, current_page, damping_factor)
        next_page = random.choices(list(transition_probabilities.keys()), weights=list(transition_probabilities.values()))[0]
        current_page = next_page

    for page in pagerank:
        pagerank[page] /= n #times visited in n sampling

    return pagerank




def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_rank = {}
    update_page_rank = {}

    for page in corpus:
        page_rank[page] = 1/len(corpus)

    change = 1
    while change > 0.001:
        for page in corpus:
            update_page_rank[page] = 0

            #0.15 pick random
            update_page_rank[page] += (1 - damping_factor) / len(corpus)

            #0.85 weighted pick 
            #chance on website i with link to p
            for linking_page in corpus:
                if page in corpus[linking_page]:
                    num_links = len(corpus[linking_page])
                    update_page_rank[page] += damping_factor * page_rank[linking_page] / num_links


        change = -1  #reset
        for x in page_rank:
            n = abs(page_rank[x] - update_page_rank[x])
            if n > change: #find largest change
                change = n
       
        page_rank = update_page_rank
        print(page_rank)
        print(change)

    return page_rank

    

    


if __name__ == "__main__":
    main()
