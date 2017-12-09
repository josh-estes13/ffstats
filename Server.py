from flask import Flask, jsonify, render_template, request, send_from_directory
import json
import sys
import LeagueData
import GameData
import ActivityData
import time
import statistics
import os

app = Flask(__name__)
 
@app.route('/')
def index():
	return render_template('index.html')
 
@app.route('/echo/', methods=['GET'])
def echo():

	def write_to_file(path, data):
		f = open(path, 'w')
		f.write(str(data))
		f.close()

	def read_file_data(path):
		f = open(path, 'r')
		data = f.read()
		f.close()

		return data

	league_id = request.args.get('echoValue')

	owners = None

	file_path = 'league_data//' + league_id
	owner_file = 'league_data//' + league_id + '//owners'
	games_file = 'league_data//' + league_id + '//games'
	trades_file = 'league_data//' + league_id + '//trades'
	waivers_file = 'league_data//' + league_id + '//waivers'

	if not os.path.exists(owner_file):
		os.makedirs(file_path, exist_ok=True)

		league_data = LeagueData.LeagueData(league_id, '2017')
		game_data = GameData.GameData(league_id, '2017')
		activity_data = ActivityData.ActivityData(league_id, '2017')

		owners = json.dumps(league_data.get_league_members())
		games = json.dumps(game_data.get_game_data())
		trades = json.dumps(activity_data.get_trade_data())
		waivers = json.dumps(activity_data.get_waiver_data())

		write_to_file(owner_file, owners)
		write_to_file(games_file, games)
		write_to_file(trades_file, trades)
		write_to_file(waivers_file, waivers)

	else:
		owners = read_file_data(owner_file)

	return jsonify(owners)

@app.route('/manager/', methods=['GET', 'POST'])
def manager():
	return jsonify({})

@app.route('/expected/', methods=['GET', 'POST'])
def expected():
	return jsonify({})

if __name__ == '__main__':
    app.run(port=8000, debug=True)