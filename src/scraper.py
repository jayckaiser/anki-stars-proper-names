import csv
import html
import json
import re
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
        'Designation'  : cols[1].text.strip(),
        'Constellation': cols[0].text.strip(),
        'Proper Name'  : cols[2].text.strip(),
        'IPA'          : cols[4].text.strip(),
        'Comments'     : _clean_comment(cols[3].text.strip()),
    }


def _get_unverified_star_entry(star_tr):
    """

    """
    cols = star_tr.find_all('td')

    return {
        'Designation'  : cols[1].text.strip(),
        'Constellation': cols[0].text.strip(),
        'Proper Name'  : cols[2].text.strip(),
        'IPA'          : '//',
        'Comments'     : _clean_comment(cols[3].text.strip()),
    }


def write_star_entries_to_jsonl(file, star_entries):
    """

    """
    with open(file, 'w', encoding='utf-8') as jsonfile:
        jsonfile.writelines(
            json.dumps(star_entry, ensure_ascii=False) + '\n'
            for star_entry in star_entries
        )


def write_star_entries_to_tsv(file, star_entries):
    """

    """
    with open(file, 'w', encoding='utf-8') as tsvfile:
        field_names = [
            'Designation',
            'Constellation',
            'Proper Name',
            'IPA',
            'Comments'
        ]
        csv_writer = csv.DictWriter(tsvfile, fieldnames=field_names, delimiter='\t')
        # csv_writer.writeheader()  # Anki does not use an explicit header, so we can ignore it.
        for star_entry in star_entries:
            csv_writer.writerow(star_entry)


# TODO: Write a regex cleaner to remove citations from comments.
def _clean_comment(comment):
    """

    """
    comment = comment.replace("[c]", "")
    comment = comment.replace("[clarification needed]", "")
    comment = comment.replace("[citation needed]", "")
    comment = comment.replace("[definition needed]", "")
    comment = re.sub(r"\[\d+\](: \d+(-\d+)?)?", "", comment)
    return comment



if __name__ == '__main__':

    stars_url = "https://en.wikipedia.org/wiki/List_of_proper_names_of_stars"
    soup = get_soup(stars_url)
    star_entries = get_star_entries(soup)

    out_file = './data/star_entries.jsonl'
    write_star_entries_to_jsonl(out_file, star_entries)

    out_file = './data/star_entries.tsv'
    write_star_entries_to_tsv(out_file, star_entries)
