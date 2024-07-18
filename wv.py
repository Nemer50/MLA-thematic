"""
dc.type: software
dc.format: text/x-python
dc.relation: https://cmc.wp.musiclibraryassoc.org/thematic-indexes-used-in-library-of-congress-naco-authority-files/
dc.creator: Emerson Morgan, Oberlin Conservatory Library
dc.date: 2024-07-18
dc.description: Extracts information about thematic indices from MLA CMC web pages.
"""

import requests
from bs4 import BeautifulSoup

# Function for retrieving headings and URLs listed on the MLA CMC web page
def fetch_list_items():
    url = "https://cmc.wp.musiclibraryassoc.org/thematic-indexes-used-in-library-of-congress-naco-authority-files/"

    try:
        # Request the web page
        response = requests.get(url)
        response.raise_for_status()  # In case of HTTP error
    except requests.exceptions.RequestException as e:
        print(f"Error requesting the web page: {e}")
        return []

    # Parse the HTML content of the web page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the <div> @data-id="5f33992"
    div_element = soup.find('div', {'data-id': '5f33992'})
    
    # In case this <div> is not found
    if not div_element:
        print("Error finding a list on the web page")
        return []

    # Find all <ul> within this <div>
    ul_elements = div_element.find_all('ul')
    
    # Is case no <ul> is found
    if not ul_elements:
        print("Error finding a list on the web page")
        return []

    # Extract each <li> from each <ul>
    output = []
    for ul in ul_elements:
        li = ul.find('li')
        if li:
            a = li.find('a')
            if a and 'href' in a.attrs:
                text = li.get_text(strip=True)
                href = a['href']
                output.append((text, href))

    if not output:
        print("Error finding a list on the web page")
        return []

    return output

# Function for retrieving citation information from MLA CMC web pages
def fetch_and_process_tables(url, count, text):
    try:
        # Request the web page
        response = requests.get(url)
        response.raise_for_status()  # In case of HTTP error

        # Parse the HTML content of the web page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find each <table>
        tables = soup.find_all('table')

        # Prepare text output
        output = ""

        # Extract information from the second <td> of every <tl> and arrange in columns
        for idx, table in enumerate(tables, start=1):
            rows = table.find_all('tr')
            if len(rows) >= 5:
                code = citation = abbreviation = access_point_use = notes = ""
                if len(rows[0].find_all('td')) > 1:
                    code = ''.join(str(e) for e in rows[0].find_all('td')[1].contents)
                if len(rows[1].find_all('td')) > 1:
                    citation = ''.join(str(e) for e in rows[1].find_all('td')[1].contents)
                if len(rows[2].find_all('td')) > 1:
                    abbreviation = ''.join(str(e) for e in rows[2].find_all('td')[1].contents)
                if len(rows[3].find_all('td')) > 1:
                    access_point_use = ''.join(str(e) for e in rows[3].find_all('td')[1].contents)
                if len(rows[4].find_all('td')) > 1:
                    notes = ''.join(str(e) for e in rows[4].find_all('td')[1].contents)

                output += f"{count}\t{text}\t{url}\t{idx}\t{code}\t{citation}\t{abbreviation}\t{access_point_use}\t{notes}\n"

        return output

    except requests.exceptions.RequestException as e:
        return f"Error requesting the web page: {e}\n"

# Program
if __name__ == "__main__":
    # Count the listed items
    print("Counting the number of headings...")  # Display program status
    list_items = fetch_list_items()
    print(f"Counted {len(list_items)} headings")  # Display program status

    # Prepare header of final output
    final_output = "Heading Number\tHeading\tURL\tCitation Number\tCode\tCitation\tAbbreviation\tAccess Point Use\tNotes\n"
    
    # Compile output body from individual web pages
    for count, (text, url) in enumerate(list_items, start=1):
        print(f"Processing URL: {url}")  # Display program status
        final_output += fetch_and_process_tables(url, count, text)

    # Present the final output
    print(final_output)
    print("Processing complete")  # Display program status