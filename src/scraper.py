import html
import json
import requests

from bs4 import BeautifulSoup



def get_soup(url):
    """

    """
    response = requests.get(url)
    html_ = html.unescape(response.text)
    return BeautifulSoup(html_, "html.parser")



def get_star_entries(soup):
    """

    """
    star_tables = soup.find_all('table', {'class': ['wikitable', 'sortable', 'jquery-tablesorter']})
    verified_rows = star_tables[0]
    unverified_rows = star_tables[1]

    verified_trs = verified_rows.find('tbody').find_all('tr')
    verified_trs = verified_trs[1:]  # Remove the header row.
    verified_star_entries = map(_get_verified_star_entry, verified_trs)

    unverified_trs = unverified_rows.find('tbody').find_all('tr')
    unverified_trs = unverified_trs[1:]  # Remove the header row.
    unverified_star_entries = map(_get_unverified_star_entry, unverified_trs)

    return list(verified_star_entries) + list(unverified_star_entries)


def _get_verified_star_entry(star_tr):
    """

    """
    cols = star_tr.find_all('td')

    return {
        'constellation': cols[0].text.strip(),
        'designation'  : cols[1].text.strip(),
        'proper_name'  : cols[2].text.strip(),
        'ipa'          : cols[4].text.strip(),
        'comments'     : cols[3].text.strip(),
    }


def _get_unverified_star_entry(star_tr):
    """

    """
    cols = star_tr.find_all('td')

    return {
        'constellation': cols[0].text.strip(),
        'designation'  : cols[1].text.strip(),
        'proper_name'  : cols[2].text.strip(),
        'ipa'          : '//',
        'comments'     : cols[3].text.strip(),
    }


def write_star_entries_to_jsonl(file, star_entries):
    """

    """
    with open(file, 'w', encoding='utf-8') as jsonfile:
        jsonfile.writelines(
            json.dumps(star_entry, ensure_ascii=False) + '\n'
            for star_entry in star_entries
        )


# TODO: Write a regex cleaner to remove citations from comments.

if __name__ == '__main__':

    stars_url = "https://en.wikipedia.org/wiki/List_of_proper_names_of_stars"
    soup = get_soup(stars_url)
    star_entries = get_star_entries(soup)

    print(star_entries[1])

    out_file = './data/star_entries.jsonl'
    write_star_entries_to_jsonl(out_file, star_entries)

    # Verify the Unicode matches as expected.
    with open(out_file, 'r') as jsonfile:
        lines = jsonfile.readlines()
        print(lines[1])
