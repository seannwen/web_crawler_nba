#!/usr/bin/env python2

import json
import requests
from bs4 import BeautifulSoup, element
from datetime import datetime, timedelta
from nba_email import send_email
from prettytable import PrettyTable


def get_web_data(date):
    # get the score data from the nba website
    res = requests.get('https://data.nba.net/prod/v2/{}/scoreboard.json'.format(date))
    json_object = json.loads(res.text)
    # print (json_object)
    # print json.dumps(json_object, indent=4)
    return json_object


def team_name():
    # get the NBA team names and Abbreviations
    res = requests.get('https://en.wikipedia.org/wiki/Wikipedia:WikiProject_National_Basketball_Association/National_Basketball_Association_team_abbreviations')
    bs4_html = BeautifulSoup(res.text, "html.parser")
    table = bs4_html.find('table', {'class': 'wikitable sortable'})
    team_dict = dict()
    table_with_label = table.find_all('tr')
    for team in table_with_label:
        if team.find('a'):
            team_abbr = team.find('td').text.rstrip()
            team_full = team.find('a').text
            team_dict[team_abbr] = team_full
    return team_dict


def insert_sting_middle(str, word):
    return str[:2] + word + str[2:]


def get_daily_score(web):
    # get the score data from the nba website
    message.append('Date: {0}/{1}/{2}'.format(date[:4], date[4:6], date[6:]))
    message.append('{0}Schedule{0}\n'.format('-' * 30))
    # get the data of daily games
    for index, game in enumerate(web['games']):
        host = game['hTeam']
        visitor = game['vTeam']
        info = game['nugget']
        location = game['arena']
        start_time = game['startTimeUTC']
        utc_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        utc_time = datetime.strptime(start_time, utc_format)
        local_time = utc_time + timedelta(hours=-8)
        table = PrettyTable(['Team', 'W/L', 'Score'])

        table.add_row([
            '({:>3}) {:^23}'.format(visitor['triCode'], team_dict[visitor['triCode']]),
            'W{}/L{}'.format(visitor['win'], visitor['loss']),
            'N/A' if not visitor['score'] else visitor['score']
        ])
        table.add_row([
            '({:>3}) {:^23}'.format(host['triCode'], team_dict[host['triCode']]),
            'W{}/L{}'.format(host['win'], host['loss']),
            'N/A' if not host['score'] else host['score']
        ])

        message.append('{0} Game {1:02} {0}\n'.format('=' * 21, index + 1))
        message.append(table.get_string())
        message.append('Location: {}'.format(location['name']))
        message.append('Time: {}'.format(local_time.strftime('%Y/%m/%d %H:%M')))
        message.append('Info: {}\n'.format('N/A' if not info['text'] else info['text']))


def next_game(team):
    # find the following game
    message.append('{0}Preview{0}\n'.format('-' * 40))
    i = 1
    while True:
        now = datetime.now()
        # date = datetime.now()
        aDay = timedelta(days=i)
        now = now + aDay
        date = now.strftime('%Y%m%d')

        for game in get_web_data(date)['games']:
            for x in game:
                host = game['hTeam']
                visitor = game['vTeam']
                if host['triCode'] == '{}'.format(team) or visitor['triCode'] == '{}'.format(team):

                    location = game['arena']
                    team_A = team_dict[(host['triCode'])]
                    team_B = team_dict[(visitor['triCode'])]

                    start_time = game['startTimeUTC']
                    utc_format = '%Y-%m-%dT%H:%M:%S.%fZ'
                    utc_time = datetime.strptime(start_time, utc_format)
                    local_time = utc_time + timedelta(hours=-8)
                    if host['triCode'] == '{}'.format(team):
                        series_win = host['seriesWin']
                        series_loss = host['seriesLoss']
                    else:
                        series_win = visitor['seriesWin']
                        series_loss = visitor['seriesLoss']

                    message.append("The next game for the {}({}) will be on {}/{}/{}\n{} (W{}\
/L{}) vs {} (W{}/L{})\nThe {}({}) in this series (W{}/L{})\nLocation: {}\nTime: {} \n"
                        .format(team_dict[(team)],
                                team,
                                date[:4], date[4:6], date[6:],
                                team_dict[(visitor['triCode'])],
                                visitor['win'],
                                visitor['loss'],
                                team_dict[(host['triCode'])],
                                host['win'],
                                host['loss'],
                                team_dict[(team)],
                                team,
                                series_win,
                                series_loss,
                                location['name'],
                                local_time.strftime('%H:%M')))
                    return team_A, team_B
        i += 1


def get_hist_score(team_A, team_B):

    message.append('{0}History of Two Teams{0}\n'.format('-' * 30))
    month = ['june', 'may', 'april', 'march', 'feburary', 'january', 'december', 'november', 'october']
    year = ['2018', '2017']

    win = 0
    for i in range(len(year)):
        for j in range(len(month)):
            try:
                res = requests.get('https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html'.format(year[i], month[j]))
                bs4_html = BeautifulSoup(res.text, "html.parser")
                history_games = bs4_html.find_all('tr')

                for game in history_games[1:]:
                    # put data into dictioners of home and visitor
                    home = {
                        'date': game.find('th', {'data-stat': 'date_game'}).text,
                        'name': game.find('td', {'data-stat': 'home_team_name'}).text,
                        'points': game.find('td', {'data-stat': 'home_pts'}).text
                    }

                    visitor = {
                        'name': game.find('td', {'data-stat': 'visitor_team_name'}).text,
                        'points': game.find('td', {'data-stat': 'visitor_pts'}).text
                    }

                    if (
                        (team_A == home['name'] and team_B == visitor['name']) or
                        (team_B == home['name'] and team_A == visitor['name'])

                    ):
                        if home['points'] > visitor['points']:
                            win += 1.0
                        else:
                            pass
                        'N/A' if not home['points'] else visitor['points']

                        message.append('{:>17} : {:>23} - {:>3}  vs  {:>23} - {:>3}'.format(
                                home['date'],
                                home['name'],
                                home['points'],
                                visitor['name'],
                                visitor['points']))
                        # percentage = (win / ) * 100

            except AttributeError:
                pass
    # message.append('The winning percentage is {0}%'.format(percentage))


if __name__ == "__main__":
    message = []

    team_dict = team_name()
    date = input('Please enter the date(Ex: 20180101)(Default: Present): \n')
    if not date:
        datetime = datetime.today()
        date = datetime.strftime("%Y%m%d")
    else:
        date

    # date = '20170306'

    team_abbr = input("Please enter a team name with abbreviation(Default: LAL): \n")
    if not team_abbr:
        team = 'LAL'
    else:
        team = team_abbr
    # team = insert_sting_middle('''''', team_abbr.upper())

    web = get_web_data(date)  # get the data from website
    get_daily_score(web)
    # print '\n'.join(message)
    next_game = next_game(team)  # get the data of next game
    # get_hist_score(next_game[0], next_game[1])

    print ('\n'.join(message))

    # email_subject = 'NBA daily report!!\n'
    # send_email(email_subject, '\n'.join(message))
