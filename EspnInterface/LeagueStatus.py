import sys
import requests
from bs4 import BeautifulSoup

class LeagueStatus:
	def __init__(self, league_id):
		self.ENDPOINT = 'http://games.espn.com/ffl/api/v2/'
		self.URL = 'http://games.espn.com/ffl/'
		self.league_id = league_id
		self._status = True
		self._seasons = list()
		self.get_seasons()

	@property
	def status(self):
		return self._status

	@property
	def seasons(self):
		return self._seasons

	def get_seasons(self):
		team_page_url = self.request_seasons()
		if team_page_url.status_code == 200:
			soup = BeautifulSoup(team_page_url.content, 'lxml')

			season_menu = soup.find('select', id='seasonHistoryMenu')
			if season_menu is not None:
				season_options = season_menu.findAll('option')
				if len(season_options) > 1:
					for option in season_options:
						self._seasons.append(option.text)
				else:
					self._seasons.append('2017')
			else:
				self._seasons.append('2017')
		else:
			self._status = False

	def request_seasons(self):
		params = dict()
		params['leagueId'] = self.league_id
		return requests.get('%sleagueoffice' % (self.URL, ), params=params)