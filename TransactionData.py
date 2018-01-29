import sys
import requests
import DataStore

class TransactionData:
	def __init__(self, league_id, data_store, year = '2017'):
		self.league_id = league_id
		self.year = year
		self.data_store = data_store
		self.ENDPOINT = 'http://games.espn.com/ffl/api/v2/'
		self.success = True
		self.transaction_data()

	def transaction_data(self):
		adds = list()
		drops = list()
		trades = list()
		player_ids = self.data_store.select_player_ids(self.league_id, self.year)
		for player_id in player_ids:
			request = self.request_data(player_id)

			status = request.status_code
			if status != 200:
				self.success = False

			if self.success:
				data = request.json()
				transactions = data['items']

				for transaction in transactions:
					transaction_type = transaction['transactionType']
					if transaction_type == 0 or transaction_type == 1:
						add = self.add_drop_data(transaction)
						adds.append(tuple(add))
					elif transaction_type == 3:
						drop = self.add_drop_data(transaction)
						drops.append(tuple(drop))
					elif transaction_type == 4 or transaction_type == 5:
						trade = self.trade_data(transaction)
						trades.append(tuple(trade))

		self.data_store.insert_adds(tuple(adds))
		self.data_store.insert_drops(tuple(drops))
		self.data_store.insert_trades(tuple(trades))

	def request_data(self, player_id):
		params = dict()
		params['leagueId'] = self.league_id
		params['seasonId'] = self.year
		params['playerId'] = player_id
		return requests.get('%splayer/transactions' % (self.ENDPOINT, ), params=params)

	def add_drop_data(self, transaction):
		team_id = transaction['teamId']
		player_id = transaction['playerId']
		date = transaction['transactionDate']
		data = (self.league_id, self.year, team_id, player_id, date)
		return data

	def trade_data(self, transaction):
		trade_id = transaction['transactionInfo']
		team_id = transaction['teamId']
		player_id = transaction['playerId']
		date = transaction['transactionDate']
		send_receive = 0
		if transaction['transactionType'] == 4:
			send_receive = 1
		data = (self.league_id, self.year, trade_id, team_id, player_id, send_receive, date)
		return data