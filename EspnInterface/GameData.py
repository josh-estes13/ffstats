import sys
import requests
import DataStore

class GameData:
	def __init__(self, league_id, data_store, year = '2017'):
		self.league_id = league_id
		self.year = year
		self.data_store = data_store
		self.ENDPOINT = 'http://games.espn.com/ffl/api/v2/'
		self.success = True
		self.game_data()

	def game_data(self):
		team_ids = self.data_store.select_team_ids(self.league_id, self.year)
		last_matchup_id = self.data_store.select_league_matchup_ids(self.league_id, self.year)

		pro_games = dict()
		games = list()
		for team_id in team_ids:
			for i in range(0, last_matchup_id):
				matchup_period_id = i + 1
				request = self.request_data(matchup_period_id, team_id)

				status = request.status_code
				print('STATUS: ' + str(status))
				if status != 200:
					self.success = False

				if self.success:
					data = request.json()
					boxscore = data['boxscore']
					teams = boxscore['teams']
					progames = boxscore['progames']

					matchups = list()
					rosters = list()
					eligibles = list()
					players = list()
					for team in teams:
						if team['team']['teamId'] == team_id:
							matchups_data = self.matchup_data(boxscore, team, team_id)
							rosters_data, positions_data = self.roster_data(boxscore, team, team_id)
							players_data = self.player_data(team)
							matchups.append(tuple(matchups_data))
							rosters.append(tuple(rosters_data))
							eligibles.append(tuple(positions_data))
							players.append(tuple(players_data))

					for game_id in progames:
						if game_id not in pro_games:
							pro_games[game_id] = self.pro_game_data(progames[game_id], matchup_period_id)

					self.data_store.insert_matchup_data(matchups)
					self.data_store.insert_roster_data(rosters)
					self.data_store.insert_eligible_data(eligibles)
					self.data_store.insert_player_data(players)

		if self.success:
			for game_id in pro_games:
				games.append(tuple(pro_games[game_id]))
			self.data_store.insert_pro_game_data(games)

	def matchup_data(self, boxscore, team, team_id):
		teams = boxscore['teams']
		matchup_period = boxscore['matchupPeriodId']
		scoring_period = boxscore['scoringPeriodId']
		points = team['appliedActiveRealTotal']
		matchup = (self.league_id, self.year, team_id, matchup_period, scoring_period, points)
		return matchup

	def roster_data(self, boxscore, team, team_id):
		players = list()
		positions = list()
		roster_slot = tuple()
		slots = team['slots']
		for slot in slots:
			matchup_period = boxscore['matchupPeriodId']
			player = slot.get('player', False)
			if player is not False:
				player_id = player['playerId']
				points = slot['currentPeriodRealStats'].get('appliedStatTotal', 0.00)
				projected_points = slot['currentPeriodProjectedStats'].get('appliedStatTotal', 0.00)
				slot_id = slot['slotCategoryId']
				eligible_slot_data = player['eligibleSlotCategoryIds']
				for position in eligible_slot_data:
					eligible_slot = (self.league_id, self.year, team_id, player_id, position, matchup_period)
					positions.append(tuple(eligible_slot))
				roster_slot = (self.league_id, self.year, team_id, matchup_period, player_id, points, slot_id, projected_points)
			players.append(tuple(roster_slot))
		return players, positions

	def player_data(self, team):
		players = list()
		player_info = tuple()
		slots = team['slots']
		for slot in slots:
			player = slot.get('player', False)
			if player is not False:
				player_id = player['playerId']
				first = player['firstName']
				last = player['lastName']
				position = player['defaultPositionId']
				team_id = player['proTeamId']
				player_info = (player_id, first, last, position, team_id)
			players.append(tuple(player_info))
		return players

	def pro_game_data(self, game, matchup_period_id):
		game_id = game['gameId']
		away_team_id = game['awayProTeamId']
		home_team_id = game['homeProTeamId']
		date = game['gameDate']
		return (self.league_id, self.year, game_id, matchup_period_id, away_team_id, home_team_id, date)

	def request_data(self, matchup_period_id, team_id):
		params = dict()
		params['leagueId'] = self.league_id
		params['seasonId'] = self.year
		params['matchupPeriodId'] = matchup_period_id
		params['teamId'] = team_id
		print('-------PARAMS-------')
		print('MATCHUP ID: ' + str(matchup_period_id) + ' TEAM ID: ' + str(team_id))
		return requests.get('%sboxscore' % (self.ENDPOINT, ), params=params)
