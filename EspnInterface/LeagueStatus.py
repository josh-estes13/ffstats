import sys
import requests

class LeagueStatus:
	def __init__(self, league_id, year = 2017):
		self.ENDPOINT = 'http://games.espn.com/ffl/api/v2/'
		self.league_id = league_id
		self.year = year
		self._status = True
		self.league_status()

	@property
	def status(self):
		return self._status

	def league_status(self):
		request = self.request_data()
		if request.status_code != 200:
			self._status = False

	def request_data(self):
		params = dict()
		params['leagueId'] = self.league_id
		params['seasonId'] = self.year
		return requests.get('%sleagueSettings' % (self.ENDPOINT, ), params=params)