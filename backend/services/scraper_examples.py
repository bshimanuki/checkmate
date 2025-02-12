from collections import defaultdict
import json

from celery.utils.log import get_task_logger

from bs4 import BeautifulSoup, NavigableString

logger = get_task_logger(__name__)

def parse_json_mh19(data):
    # MH 2019 when live
    results = defaultdict(list)
    for land in data.get('lands', []):
        round_name = land['title']
        round_link = land['url']
        results['rounds'].append({
            'name': round_name,
            'link': round_link,
        })
        for puzzle in land.get('puzzles', []):
            puzzle_name = puzzle['title']
            puzzle_link = puzzle['url']
            results['puzzles'].append({
                'name': puzzle_name,
                'link': puzzle_link,
                'round_names': [round_name],
            })
    return results

def parse_html_mh12(soup):
    # MH 2012
    results = defaultdict(list)
    for h2 in soup.find_all('h2'):
        table = h2.find_next_sibling('table')
        if table is not None:
            round_name = h2.string
            _round = {}
            _round['name'] = round_name
            for a in table.find_all('a'):
                if a.string == 'Round page':
                    _round['link'] = a.get('href')
                else:
                    puzzle = {}
                    puzzle['name'] = a.string
                    puzzle['link'] = a.get('href')
                    puzzle['round_names'] = [round_name]
                    results['puzzles'].append(puzzle)
            results['rounds'].append(_round)
    return results

def parse_html_gph17(soup):
    # Galact Puzzle Hunt 2017
    results = defaultdict(list)
    for row in soup.find_all('div', class_='row'):
        day, puzzles = (child for child in row.children if child.name == 'div')
        if 'three' in day['class'] and 'nine' in puzzles['class']:
            round_name = day.h3.string
            results['rounds'].append({'name': round_name})
            for td in puzzles.select('td:first-child'):
                a = td.a
                puzzle = {}
                puzzle['name'] = a.string.strip()
                puzzle['link'] = a.get('href')
                puzzle['round_names'] = [round_name]
                results['puzzles'].append(puzzle)
    return results

def parse_html_gph18(soup):
    # Galact Puzzle Hunt 2018
    results = defaultdict(list)
    for h3 in soup.find_all('h3', class_='puzzle-round__name'):
        round_name = h3.string
        results['rounds'].append({'name': round_name})
        container = h3.find_next_sibling('div', class_='puzzle-round__container')
        for div in container.children:
            if not isinstance(div, NavigableString) and 'puzzle-round__item-link' in div.get('class'):
                puzzle = {}
                puzzle['name'] = div.a.text.strip()
                puzzle['link'] = div.a.get('href')
                puzzle['round_names'] = [round_name]
                results['puzzles'].append(puzzle)
    return results

def parse_html_mh16(soup):
    # MH 2016
    results = defaultdict(list)
    for h2 in soup.find_all('h2'):
        round_name = h2.a.string
        results['rounds'].append({
            'name': round_name,
            'link': h2.a.get('href'),
        })
        ul = h2.find_next_sibling('ul')
        for a in ul.find_all('a'):
            puzzle = {
                'name': a.string,
                'link': a.get('href'),
                'round_names': [round_name],
            }
            results['puzzles'].append(puzzle)
    return results

def parse_html_mh20(soup):
    # MH 2020
    results = defaultdict(list)
    for li_round in soup.find('ul', id='loplist').children:
        if not isinstance(li_round, NavigableString):
            round_name = li_round.a.string
            results['rounds'].append({
                'name': round_name,
                'link': li_round.a.get('href'),
            })
            for li_puzzle in li_round.find_all('li'):
                puzzle = {
                    'name': li_puzzle.a.string,
                    'link': li_puzzle.a.get('href'),
                    'round_names': [round_name],
                }
                results['puzzles'].append(puzzle)
    return results

def parse_html_mh21(soup, intro_only=True):
    '''
    If `intro_only` is True, only parses the intro round.

    NB: Public access login needs to have {'public': 'public access'} in the payload.
    '''
    results = defaultdict(list)
    main = soup.find('main')
    for section in main.find_all('section'):
        a_round = section.a
        if a_round.h3 is None:
            continue
        round_name = a_round.h3.string
        if intro_only and round_name != 'Yew Labs':
            # only parse intro round
            continue
        results['rounds'].append({
            'name': round_name,
            'link': a_round.get('href'),
        })
        for tr_puzzle in section.find_all('tr'):
            tds = tr_puzzle.find_all('td')
            if tds:
                if tds[0].a is None or tds[0].a.get('href') is None:
                    continue
                answer = tds[1].string.strip()
                puzzle = {
                    'name': tds[0].a.string.strip(),
                    'link': tds[0].a.get('href'),
                    'round_names': [round_name],
                    'answer': answer,
                    'is_solved': bool(answer),
                    'is_meta': 'meta' in (tds[0].get('class') or []),
                }
                if round_name == 'Infinite Corridor':
                    continue
                    if ':' in puzzle['name']:
                        puzzle['name'] = puzzle['name'][puzzle['name'].find(':'):]

                results['puzzles'].append(puzzle)
    return results

async def parse_html_gphsite21(client, soup, *, _round=None):
    # parses gph-site 2021 and fetches round pages
    # recurses if _round is None
    results = defaultdict(list)
    main = soup.find('main')
    for list_div in soup.find_all('div', class_='puzzles-list'):
        round_names = []
        round_name = _round['name'] if _round else None
        if round_name:
            results['rounds'].append({'name': round_name})
            round_names.append(round_name)
        for entry_div in list_div.find_all('div', class_='puzzles-entry'):
            a = entry_div.find('a', class_='puzzles-link')
            answer_div = entry_div.find(class_='solved-title-answer')
            answer = answer_div and answer_div.text.strip()
            if a is not None:
                puzzle = {}
                puzzle['name'] = a.text.strip()
                puzzle['link'] = a.get('href')
                puzzle['round_names'] = round_names
                if 'puzzles-meta' in (entry_div.get('class') or []):
                    puzzle['is_meta'] = True
                if answer:
                    puzzle['answer'] = answer
                    puzzle['is_solved'] = True
                results['puzzles'].append(puzzle)
    if _round is None:
        for h2 in soup.find_all('h2'):
            a = h2.a
            if a is not None:
                _round = {
                    'name': a.text.strip(),
                    'link': a.get('href'),
                }
                round_html = await client.try_fetch(_round['link'])
                round_soup = BeautifulSoup(round_html, 'html5lib')
                round_results = await parse_html_gphsite21(client, round_soup, _round=_round)
                results['rounds'].extend(round_results['rounds'])
                results['puzzles'].extend(round_results['puzzles'])
    return results

def parse_html_dp20(soup):
    # parses DP Hunt 2020
    results = defaultdict(list)
    for h4 in soup.find_all('h4'):
        round_name = h4.text.strip()
        results['rounds'].append({'name': round_name})
    for table in soup.find_all('table', class_='gph-list-table'):
        h4 = table.find_previous_sibling('h4')
        round_names = []
        if h4 is not None:
            round_name = h4.text.strip()
            round_names.append(round_name)
        for tr_puzzle in table.find_all('tr'):
            tds = tr_puzzle.find_all('td')
            if not tds:
                continue
            a = tds[0].a
            elt_answer = tr_puzzle.find(class_='solved-title-answer')
            answer = elt_answer and elt_answer.text.strip()
            if a is not None:
                puzzle = {}
                puzzle['name'] = a.text.strip()
                puzzle['link'] = a.get('href')
                puzzle['round_names'] = round_names
                if answer:
                    puzzle['answer'] = answer
                    puzzle['is_solved'] = True
                if puzzle['name'].startswith('META:'):
                    puzzle['is_meta'] = True
                results['puzzles'].append(puzzle)
    return results

def parse_html_silph21(soup):
    results = defaultdict(list)
    for btn in soup.find_all('button', class_='tablink'):
        round_name = btn.text.strip()
        results['rounds'].append({'name': round_name})
    btn in soup.find('button', class_='tab-selected')
    round_name = btn.text.strip()
    for table in soup.find_all('table', class_='gph-list-table'):
        round_names = []
        round_names.append(round_name)
        for tr_puzzle in table.find_all('tr'):
            tds = tr_puzzle.find_all('td')
            if not tds:
                continue
            a = tds[0].a
            elt_answer = tr_puzzle.find(class_='solved-title-answer')
            answer = elt_answer and elt_answer.text.strip()
            if a is not None:
                puzzle = {}
                puzzle['name'] = a.text.strip()
                puzzle['link'] = a.get('href')
                puzzle['round_names'] = round_names
                if answer:
                    puzzle['answer'] = answer
                    puzzle['is_solved'] = True
                if puzzle['name'].startswith('META:'):
                    puzzle['is_meta'] = True
                results['puzzles'].append(puzzle)
    return results

def parse_html_starrats(soup):
    results = defaultdict(list)
    div_puzzles = soup.find(class_='puzzles')
    round_name = None
    for div in div_puzzles.children:
        if div.name != 'div':
            continue
        table = div.find('table')
        if table is None:
            continue
        for tr in table.tbody.find_all('tr'):
            td_or_th = tr.find_all(True, recursive=False)[0]
            if td_or_th.name == 'th':
                round_name = td_or_th.string
                _round = {'name': round_name}
                if td_or_th.a:
                    _round['link'] = td_or_th.a.get('href')
                results['rounds'].append(_round)
            else:
                a = td_or_th.a
                if a is not None:
                    puzzle = {}
                    puzzle['name'] = a.text.strip()
                    puzzle['link'] = a.get('href')
                    if round_name is not None:
                        puzzle['round_names'] = [round_name]
                    answer = None
                    if answer:
                        puzzle['answer'] = answer
                        puzzle['is_solved'] = True
                    if 'meta' in a.get('class', []):
                        puzzle['is_meta'] = True
                    results['puzzles'].append(puzzle)
    return results

async def parse_html_mh22(client, soup):
    results = defaultdict(list)
    content = soup.find(id='main-content')
    round_name = None
    for h2 in content.find_all('h2'):
        if h2.name == 'h2':
            # round
            round_name = h2.text.strip()
            _round = {'name': round_name}
            a = h2.a
            if h2.a:
                _round['link'] = h2.a.get('href')
            results['rounds'].append(_round)
            round_html = await client.try_fetch(_round['link'])
            round_soup = BeautifulSoup(round_html, 'html5lib')
            div = round_soup.find(class_='round-table-container')
            table = div.table
            if table:
                # list of puzzles
                for tr in table.tbody.find_all('tr')[1:]:
                    tds_or_ths = tr.find_all(True, recursive=False)
                    if len(tds_or_ths) != 2:
                        continue
                    puzzle = {}
                    puzzle['name'] = tds_or_ths[0].text.strip()
                    a = tds_or_ths[0].a
                    if a:
                        puzzle['link'] = a.get('href')
                    if round_name is not None:
                        puzzle['round_names'] = [round_name]
                    answer = tds_or_ths[1].text.strip()
                    if answer:
                        puzzle['answer'] = answer
                        puzzle['is_solved'] = True
                    if 'meta' in a.get('class', []):
                        puzzle['is_meta'] = True
                    results['puzzles'].append(puzzle)
    return results

def parse_json_mh23(data):
    # MH 2023 when live
    results = defaultdict(list)
    rounds = set()
    for puzzle in data:
        round_name = puzzle['round']
        if round_name not in rounds:
            results['rounds'].append({
                'name': round_name,
            })
        results['puzzles'].append({
            'name': puzzle['name'],
            'link': puzzle['url'],
            'round_names': [round_name],
            'is_meta': puzzle['isMeta'],
            'is_solved': bool(puzzle['answer']),
            'answer': puzzle['answer'] or '',
        })
    return results

async def parse_html_mh25(client, soup):
    results = defaultdict(list)
    content = soup.find(id='all-puzzles-root')
    round_name = None
    for h3 in content.find_all('h3'):
        if h3.name == 'h3':
            # round
            round_name = h3.text.strip()
            _round = {'name': round_name}
            if h3.a:
                _round['link'] = h3.a.get('href')
            results['rounds'].append(_round)
            table = None
            siblings = list(h3.next_siblings)
            if siblings and siblings[0].name == 'table':
                table = siblings[0]
            if table:
                # list of puzzles
                puzzle = {}
                for tr in table.tbody.find_all('tr'):
                    for td in tr.find_all('td'):
                        if td.get('class') == ['puzzle-name']:
                            if puzzle.get('name'):
                                results['puzzles'].append(puzzle)
                            title = td.find(class_='puzzle-link-title')
                            if title is None:
                                continue
                            puzzle = {}
                            puzzle['name'] = title.get_text(strip=True, separator=' ')
                            if title.get('href'):
                                puzzle['link'] = title.get('href')
                            if round_name is not None:
                                puzzle['round_names'] = [round_name]
                        elif td.get('class') == ['puzzle-answer']:
                            answer = td.get_text(strip=True, separator=' ')
                            if answer:
                                puzzle['answer'] = answer
                                puzzle['is_solved'] = True
                        elif td.get('class') == ['desc']:
                            puzzle['notes'] = td.text.strip()
                if puzzle.get('name'):
                    results['puzzles'].append(puzzle)
    return results

