import sys
import requests

class LeagueData:
	def __init__(self, league_id, data_store, season = '2017'):
		self.league_id = league_id
		self.year = season
		self.data_store = data_store
		self.ENDPOINT = 'http://games.espn.com/ffl/api/v2/'
		self.success = True
		self.league_data()
	
	def league_data(self):
		request = self.request_data()
		status = request.status_code
		if status != 200:
			self.success = False

		if self.success:
			data = request.json()
			league = data['leaguesettings']
			self.store_league_data(league)
			self.store_teams(league)

	def store_league_data(self, league):
		name = league['name']
		scoring_period_id = league['firstScoringPeriodId']
		matchup_count = league['regularSeasonMatchupPeriodCount']
		position_slots = league['slotCategoryItems']

		league_info = [self.league_id, self.year, name, scoring_period_id, matchup_count]
		self.data_store.insert_league(league_info)

	def store_teams(self, league):
		def team_data(team):
			team_info = [
				self.league_id,
				self.year,
				team['teamId'],
				team['teamAbbrev'],
				team['teamLocation'] + ' ' + team['teamNickname'],
				team.get('logoUrl', 'http://g.espncdn.com/lm-static/ffl17/images/default.svg'),
				team['teamTransactions']['overallAcquisitionTotal'],
				team['teamTransactions']['trades'],
				team['record']['overallWins'],
				team['record']['overallLosses'],
				team['record']['pointsFor'],
				team['record']['pointsAgainst'],
				team['overallStanding']
			]

			return team_info

		teams = league['teams']
		for team in teams:
			team_info = team_data(teams[team])
			self.data_store.insert_team(team_info)

	def request_data(self):
		params = dict()
		params['leagueId'] = self.league_id
		params['seasonId'] = self.year
		return requests.get('%sleagueSettings' % (self.ENDPOINT, ), params=params)
		