from flask import Flask, jsonify, render_template, request, send_from_directory, send_file
import json
import sys
import time
import statistics
import os
import psycopg2
import LeagueData
import DataStore
import GameData
import TransactionData
import LeagueStats

try:
	conn = psycopg2.connect("dbname='ffstats' user='joshestes' host='localhost' password='London.513'")
	cursor = conn.cursor()
except e:
	pass

app = Flask(__name__)
 
@app.route('/')
@app.route('/index/')
def index():
	return send_file('index.html')

@app.route('/js/<path:path>')
def send_js(path):
	return send_from_directory('js', path)

@app.route('/css/<path:path>')
def send_css(path):
	return send_from_directory('css', path)

@app.route('/fonts/<path:path>')
def send_fonts(path):
	return send_from_directory('fonts', path)
 
@app.route('/leagueId/', methods=['GET'])
def leagueId():
	year = '2017'
	league_id = request.args.get('id')
	data_store = DataStore.DataStore(conn, cursor)

	if not data_store.league_exists(league_id, year):
		LeagueData.LeagueData(league_id, data_store, year)
		GameData.GameData(league_id, data_store, year)
		TransactionData.TransactionData(league_id, data_store, year)

	teams = data_store.select_teams(league_id, year)

	return jsonify(teams)

@app.route('/teams/', methods=['GET'])
def teams():

	league_id = request.args.get('id')
	team_id = request.args.get('team')

	return render_template('team.html', leagueId=league_id, teamId=team_id)

@app.route('/team/', methods=['GET', 'POST'])
def team_page():
	year = '2017'
	league_id = request.args.get('id')
	team_id = request.args.get('team')

	data_store = DataStore.DataStore(conn, cursor)

	expected_record = LeagueStats.ExpectedRecord(league_id, data_store)
	expected_record.calculate_expected_record(team_id)

	league_averages = LeagueStats.LeagueAverages(league_id, data_store, year)
	league_averages.calculate_player_scores(team_id)
	league_averages.calculate_median_scores()
	league_averages.team_position_scores(team_id)
	league_averages.league_position_scores()

	transaction_stats = LeagueStats.TransactionStats(league_id, data_store, year)
	transaction_stats.points_from_trades(team_id)
	transaction_stats.points_from_adds(team_id)
	transaction_stats.trades(team_id)

	optimal_lineup = LeagueStats.OptimalLineups(league_id, data_store, year)
	optimal_lineup.optimal_lineups(team_id)

if __name__ == '__main__':
    app.run(port=8000, debug=True)