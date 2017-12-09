import sys
import UrlBuilder
from bs4 import BeautifulSoup
import requests

class ActivityData:
	def __init__(self, league_id, season = '2017'):
		self.league_id = league_id
		self.season_year = season
		self.url_builder = UrlBuilder.UrlBuilder(league_id, season)
		
	def activity_table(self, url):
		page = requests.get(url)
		soup = BeautifulSoup(page.content, 'lxml')
		
		table = soup.select('table.tableBody')[0]
		rows = table.select('tr')
		
		return rows
		
	def set_player_data(self, name, position, team):
		player = dict()
		player['Name'] = name
		player['Position'] = position
		player['Team'] = team
		
		return player
		
	def parse_activity_date(self, date):
		children = self.get_child_list(date)
		date_tokens = (str(children[0])).split()
		
		return date_tokens[1] + ' ' + date_tokens[2]
			
	def parse_player_name(self, player_name_data):
		player_name = player_name_data.replace('<b>', '')
		player_name = player_name.replace('</b>', '')
		
		return player_name
	
	def get_child_list(self, transaction_data):
		children = list()
		for x in transaction_data.childGenerator():
			children.append(x)
		
		return children
		
	def get_waiver_data(self):
		waiver_activity_url = self.url_builder.activity_url('Waivers')
		waiver_rows = self.activity_table(waiver_activity_url)
		
		waivers = list()
		for i in range(2, len(waiver_rows)):
			waiver_row = waiver_rows[i].select('td')
			transaction_data = waiver_row[2]
			
			children = self.get_child_list(transaction_data)
			
			waiver = dict()
			j = 0
			while j < (len(children)):
				waiver['Date'] = self.parse_activity_date(waiver_row[0])
				waiver['Team'] = str(children[j]).split()[0]
				waiver['Player'] = self.set_player_data(self.parse_player_name(str(children[j+1])), str(children[j+2]).split()[2], str(children[j+2]).split()[1])
				
				waivers.append(dict(waiver))
				
				j = j + 4
				
		return waivers
		
	def get_trade_data(self):
		trade_activity_url = self.url_builder.activity_url('Trades')
		trade_rows = self.activity_table(trade_activity_url)
		
		trades = list()
		i = 2
		while i < (len(trade_rows)):
			trade_row = trade_rows[i].select('td')
			
			transaction_data = trade_row[2]
			children = self.get_child_list(transaction_data)
			
			trade_list = list()
			trade = dict()
			j = 0
			while j < (len(children)):
				trade['Date'] = self.parse_activity_date(trade_row[0])
				trade['Sender'] = str(children[j]).split()[0]
				trade['Receiver'] = str(children[j+2]).split()[4]
				trade['Player'] = self.set_player_data(self.parse_player_name(str(children[j+1])), str(children[j+2]).split()[2], str(children[j+2]).split()[1])
				
				trade_list.append(dict(trade))
				
				j = j + 4
			
			trades.append(trade_list)
			i = i + 2
		
		return trades