#!/usr/bin/env python

import json
import requests
from bs4 import BeautifulSoup, element
from datetime import datetime, timedelta
from time import time
from nba_email import send_email
from prettytable import PrettyTable


def get_web_data(date):
    # get the score data from the nba website
    res = requests.get('https://data.nba.net/prod/v2/{}/scoreboard.json'.format(date))
    json_object = json.loads(res.text)
    # print json.dumps(json_object, indent=4)
    return json_object


def team_name(team_name_abbr):
    # get the NBA team names and Abbreviations
    res = requests.get('https://en.wikipedia.org/wiki/Wikipedia:WikiProject_National_Basketball_Association/National_Basketball_Association_team_abbreviations')
    bs4_html = BeautifulSoup(res.text, "html.parser")
    table = bs4_html.find('table', {'class': 'wikitable sortable'})

    team_dict = dict()
    for team in table:
        if isinstance(team, element.Tag) and team.find('a'):
            team_abbr = team.find('td').text
            team_full = team.find('a')['title']
            team_dict[team_abbr] = team_full

    return team_dict[team_name_abbr]


def insert_sting_middle(str, word):
    return str[:2] + word + str[2:]


def get_daily_score(web):
    # get the score data from the nba website
    message.append('Date: {0}/{1}/{2}'.format(date[:4], date[4:6], date[6:]))
    message.append('--------------------------------------Schedule--------------------------------------\n')
    # get the data of daily games
    for index, game in enumerate(web['games']):
        host = game['hTeam']
        visitor = game['vTeam']
        info = game['nugget']
        location = game['arena']
        start_time = game['startTimeUTC'].encode('utf-8')
        utc_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        utc_time = datetime.strptime(start_time, utc_format)
        local_time = utc_time + timedelta(hours=-8)

        table = PrettyTable(['Team', 'W/L', 'Score'])
        table.add_row([
            '({}) {}'.format(visitor['triCode'], team_name(visitor['triCode'])),
            'W{}/L{}'.format(visitor['win'], visitor['loss']),
            '{}'.format(visitor['score'])
        ])
        table.add_row([
            '({}) {}'.format(host['triCode'], team_name(host['triCode'])),
            'W{}/L{}'.format(host['win'], host['loss']),
            '{}'.format(host['score'])
        ])

        message.append('{0} Game {1:02} {0}\n'.format('=' * 20, index + 1))
        message.append(table.get_string())
        message.append('Location: {}'.format(location['name']))
        message.append('Time: {}'.format(local_time.strftime('%H:%M')))
        message.append('Info: {}\n'.format(info['text']))


def next_game(team):
    # find the following game
    message.append('-----------------------------------------Preview------------------------------------------\n')
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
                    team_A = team_name(host['triCode'])
                    team_B = team_name(visitor['triCode'])

                    start_time = game['startTimeUTC'].encode('utf-8')
                    utc_format = '%Y-%m-%dT%H:%M:%S.%fZ'
                    utc_time = datetime.strptime(start_time, utc_format)
                    local_time = utc_time + timedelta(hours=-8)
                    if host['triCode'] == '{}'.format(team):
                        series_win = host['seriesWin']
                        series_loss = host['seriesLoss']
                    else:
                        series_win = visitor['seriesWin']
                        series_loss = visitor['seriesLoss']

                    message.append('The next game for the {0}({1}) will be on {2}/{3}/{4}\n{5} (W{6}/L{7}) vs {8} (W{9}/L{10})\nThe {11}({12}) in this series (W{13}/L{14})\nLocation: {15}\nTime: {16} PST\n'\
                        .format(team_name(team),
                                team,
                                date[:4], date[4:6], date[6:],
                                team_name(visitor['triCode']),
                                visitor['win'],
                                visitor['loss'],
                                team_name(host['triCode']),
                                host['win'],
                                host['loss'],
                                team_name(team),
                                team,
                                series_win,
                                series_loss,
                                location['name'],
                                local_time.strftime('%H:%M')))
                    return team_A, team_B
        i += 1


def get_hist_score(team_A, team_B):

    message.append('--------------------------------History of Two Teams--------------------------------\n')

    month = ['june', 'may', 'april', 'march', 'feburary', 'january', 'december', 'november', 'october']
    year = ['2018', '2017', '2016']

    for i in xrange(len(year)):
        for j in xrange(len(month)):
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
                        # if home['points'].encode('utf-8') is not None:
                            message.append('{:>17} : {:>23} - {:>3}  vs  {:>23} - {:>3}'.format(
                                home['date'],
                                home['name'],
                                home['points'],
                                visitor['name'],
                                visitor['points']))

            except AttributeError:
                pass


if __name__ == "__main__":
    # start_time = time()
    message = []
    datetime = datetime.today()
    # print datetime
    date = datetime.strftime("%Y%m%d")

    # date = raw_input('Please enter the date(Ex: 20180101): \n')
    # date = '20180305'

    # team_abbr = raw_input("Please enter the team abbreviation(Ex: CLE): \n")
    # team = insert_sting_middle('''''', team_abbr.upper())
    team = 'CLE'

    web = get_web_data(date)  # get the data from website
    get_daily_score(web)
    # print '\n'.join(message)
    next_game = next_game(team)
    # get_hist_score(next_game[0], next_game[1])
    print '\n'.join(message)

    # end_time = time()
    # print 'Time: {0}'.format(end_time - start_time)

    # with open('nba_report.txt', 'w') as f:
    #     for i in message:
    #         f.write(i)
    #         f.write('\n')
    #
    # email_subject = 'NBA daily report!!\n'
    # send_email(email_subject, 'nba_report.txt')
