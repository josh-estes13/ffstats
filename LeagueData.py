import sys
import UrlBuilder
from bs4 import BeautifulSoup
import requests
from collections import OrderedDict

class LeagueData:
	def __init__(self, league_id, season = '2017'):
		self.league_id = league_id
		self.season_year = season
		self.url_builder = UrlBuilder.UrlBuilder(league_id, season)
	
	def get_league_members(self):
		
		def get_team_initials(team_page):
			team_page_url = self.url_builder.team_page_url(team_page)
			page = requests.get(team_page_url)
			soup = BeautifulSoup(page.content, 'lxml')

			team = soup.select('h3.team-name')[0]
			initials = team.find('em').text
			
			initials = initials[:-1]
			initials = initials[1:]
			return initials
		
		owners = list()
		
		league_standings_url = self.url_builder.league_standings_url()
		page = requests.get(league_standings_url)
		soup = BeautifulSoup(page.content, 'lxml')
		
		owner_rows = soup.select('tr.tableBody')
		ranking = 1
		for owner_row in owner_rows:
			owner_data = owner_row.select('td')
			owner = dict()
			owner['Rank'] = ranking
			owner['Team'] = owner_data[0].find('a').text
			owner['Page'] = owner_data[0].find('a')['href']
			owner['Initials'] = get_team_initials(owner['Page'])
			owner['Wins'] = owner_data[1].text
			owner['Losses'] = owner_data[2].text
			
			owners.append(owner)
			
			ranking = ranking + 1
		
		return owners