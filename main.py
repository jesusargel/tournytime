from flask import Flask, render_template, redirect, request
app = Flask("TODO")

import os
import mysql.connector

cnx = mysql.connector.connect(option_files='%s/.my.cnf' % os.environ['HOME'],
                              database='cinf201_jargel')

@app.route('/')
def home():
    cursor = cnx.cursor(dictionary=True)
    cursor.execute('select id, tname, num_of_teams, status, prize from tournaments order by status, prize desc limit 10')
    tournaments = cursor.fetchall()
    cursor1 = cnx.cursor(dictionary=True)
    cursor1.execute('select id, teamname from teams order by teamname asc limit 8')
    teams = cursor1.fetchall()
    cursor2 = cnx.cursor(dictionary=True)
    cursor2.execute('select id, fname, lname from players order by lname asc limit 8')
    players = cursor2.fetchall()
    return render_template('home.html', tournaments = tournaments, teams = teams, players = players)

@app.route('/tournament/<id>')
def tournament(id):
    cursor = cnx.cursor(dictionary=True)
    cursor.execute('select id, tname, num_of_teams, status, prize from tournaments where id = {}'.format(id))
    tournaments = cursor.fetchall()
    cursor1 = cnx.cursor(dictionary=True)
    cursor1.execute('select teams.id, teamname from teams '
                    'join tournaments_teams on teams.id = tournaments_teams.team_id '
                    'join tournaments on tournaments_teams.tournaments_id = tournaments.id '
                    'where tournaments.id = {}'.format(id))
    teams = cursor1.fetchall()
    cursor2 = cnx.cursor(dictionary=True)
    cursor2.execute('select players.id, fname, lname from players '
                    'join teams_players on players.id = teams_players.player_id '
                    'join teams on teams_players.team_id = teams.id '
                    'join tournaments_teams on teams.id = tournaments_teams.team_id '
                    'join tournaments on tournaments_teams.tournaments_id = tournaments.id '
                    'where tournaments.id = {}'.format(id))
    players = cursor2.fetchall()
    return render_template('tournament.html', tournaments = tournaments, teams = teams, players = players)

@app.route('/team/<id>')
def team(id):
    cursor = cnx.cursor(dictionary=True)
    cursor.execute('select id, teamname from teams where id = {}'.format(id))
    teams = cursor.fetchall()
    cursor1 = cnx.cursor(dictionary=True)
    cursor1.execute('select tournaments.id, tname from tournaments '
                    'join tournaments_teams on tournaments.id = tournaments_teams.tournaments_id '
                    'join teams on tournaments_teams.team_id = teams.id '
                    'where teams.id = {} '
                    'order by tname'.format(id))
    tournaments = cursor1.fetchall()
    cursor2 = cnx.cursor(dictionary=True)
    cursor2.execute('select players.id, fname, lname from players '
                    'join teams_players on players.id = teams_players.player_id '
                    'join teams on teams_players.team_id = teams.id '
                    'where teams.id = {} '
                    'order by fname '.format(id))
    players = cursor2.fetchall()
    return render_template('team.html', tournaments = tournaments, teams = teams, players = players)

@app.route('/player/<id>')
def player(id):
    cursor = cnx.cursor(dictionary=True)
    cursor.execute('select fname, lname from players where id = {}'.format(id))
    players = cursor.fetchall()
    cursor1 = cnx.cursor(dictionary=True)
    cursor1.execute('select teams.id, teamname from teams '
                    'join teams_players on teams.id = teams_players.team_id '
                    'join players on teams_players.player_id = players.id '
                    'where players.id = {} '
                    'order by teamname'.format(id))
    teams = cursor1.fetchall()
    cursor2 = cnx.cursor(dictionary=True)
    cursor2.execute('select tournaments.id, tname from tournaments '
                    'join tournaments_teams on tournaments.id = tournaments_teams.tournaments_id '
                    'join teams on tournaments_teams.team_id = teams.id '
                    'join teams_players on teams.id = teams_players.team_id '
                    'join players on teams_players.player_id = players.id '
                    'where players.id = {} '
                    'order by tname'.format(id))
    tournaments = cursor2.fetchall()
    return render_template('player.html', tournaments = tournaments, teams = teams, players = players)

@app.route('/tournament')
def tournaments():
    cursor = cnx.cursor(dictionary=True)
    cursor.execute('select id, tname, num_of_teams, status, prize from tournaments order by tname, prize desc')
    tournaments = cursor.fetchall()
    return render_template('tournaments.html', tournaments = tournaments)

 
@app.route('/team')
def teams():
    cursor = cnx.cursor(dictionary=True)
    cursor.execute('select id, teamname from teams order by teamname desc')
    teams = cursor.fetchall()
    return render_template('teams.html', teams = teams)


@app.route('/player')
def players():
    cursor = cnx.cursor(dictionary=True)
    cursor.execute('select id, fname, lname from players order by fname desc')
    players = cursor.fetchall()
    return render_template('players.html', players = players)


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        search = "'%" + request.form['search'] + "%'"
        cursor = cnx.cursor(dictionary=True)
        cursor.execute('select id, fname, lname from players where fname like {} or lname like {} order by fname, lname'.format(search, search))
        players = cursor.fetchall() 
        cursor1 = cnx.cursor(dictionary=True)
        cursor1.execute('select id, tname, num_of_teams, status, prize from tournaments where tname like {} order by tname'.format(search))
        tournaments = cursor1.fetchall()
        cursor2 = cnx.cursor(dictionary=True)
        cursor2.execute('select id, teamname from teams where teamname like {} order by teamname'.format(search))
        teams = cursor2.fetchall()
        return render_template('search.html', players = players, tournaments = tournaments, teams = teams)


@app.route('/createtournament')
def createtournament():
    return render_template('createtournament.html')


@app.route('/addtotournaments', methods=['POST', 'GET'])
def addtournament():
    if request.method == 'POST':
        cursor = cnx.cursor()
        cursor.execute('insert into tournaments (tname, num_of_teams, status, prize) values ("{}", {}, "Active", {})'.format(request.form['TournamentName'], request.form['NumOfTeams'], request.form['Prize']))
        cnx.commit()
    return redirect('/')


@app.route('/createteam')
def createteam():
    return render_template('createteam.html')


@app.route('/addtoteams', methods=['POST', 'GET'])
def addteam():
    if request.method == 'POST':
        cursor = cnx.cursor()
        print(request.form['TeamName'])
        cursor.execute('insert into teams (teamname) values ("{}");'.format(request.form['TeamName']))
        cnx.commit()
    return redirect('/')


@app.route('/createplayer')
def createplayer():
    return render_template('createplayer.html')


@app.route('/addtoplayers', methods=['POST', 'GET'])
def addplayer():
    if request.method == 'POST':
        cursor = cnx.cursor()
        cursor.execute('insert into players (fname, lname) values (%s, %s)', (request.form['FirstName'], request.form['LastName']))
        cnx.commit()
    return redirect('/')

    
@app.route('/updatetournament')
def updatetournament():
    cursor = cnx.cursor(dictionary=True)
    cursor.execute('select tname from tournaments order by tname')
    tournaments = cursor.fetchall()
    return render_template('updatetournament.html', tournaments = tournaments)


@app.route('/updatedtournament', methods=['POST', 'GET'])
def updatedtournament():
    if request.method == 'POST':
        cursor = cnx.cursor()
        cursor.execute('select id from tournaments where tname = "{}"'.format(request.form['TournamentToUpdate']))
        tournaments = cursor.fetchall()
        cursor1 = cnx.cursor()
        cursor1.execute('update tournaments set tname = "{}", num_of_teams = {}, status = "{}", prize = {} where id = {}'.format(request.form['TournamentName'], request.form['NumOfTeams'], request.form['Status'], request.form['Prize'], tournaments[0][0]))
        cnx.commit()
    return redirect('/')


@app.route('/updateteam')
def updateteam():
    cursor = cnx.cursor(dictionary=True)
    cursor.execute('select id, teamname from teams order by teamname asc')
    teams = cursor.fetchall()
    return render_template('updateteam.html', teams = teams)


@app.route('/updatedteam', methods=['POST', 'GET'])
def updatedteam():
    if request.method == 'POST':
        cursor = cnx.cursor()
        cursor.execute('select id from teams where teamname = "{}"'.format(request.form['TeamToUpdate']))
        teams = cursor.fetchall()
        cursor1 = cnx.cursor()
        cursor1.execute('update teams set teamname = "{}" where id = {}'.format(request.form['TeamName'], teams[0][0]))
        cnx.commit()
    return redirect('/')


@app.route('/updateplayer')
def updateplayer():
    cursor = cnx.cursor(dictionary=True)
    cursor.execute('select id, fname, lname from players order by fname asc')
    players = cursor.fetchall()
    return render_template('updateplayer.html', players = players)


@app.route('/updatedplayer', methods=['POST', 'GET'])
def updatedplayer():
    if request.method == 'POST':
        cursor = cnx.cursor()
        selected_player = request.form['PlayerToUpdate']
        sp = selected_player.split()
        cursor.execute('select id from players where fname = "{}" and lname = "{}"'.format(sp[0], sp[1]))
        spid = cursor.fetchall()
        print(spid[0][0])
        cursor1 = cnx.cursor()
        cursor1.execute('update players set fname = "{}", lname = "{}" where id = {}'.format(request.form['FirstName'], request.form['LastName'], spid[0][0] ))
        cnx.commit()
    return redirect('/')


@app.route('/deletetournament')
def deletetournament():
    cursor = cnx.cursor(dictionary=True)
    cursor.execute('select tname from tournaments order by tname')
    tournaments = cursor.fetchall()
    return render_template('deletetournament.html', tournaments = tournaments)


@app.route('/deletedtournament', methods=['POST', 'GET'])
def deletedtournament():
    if request.method == 'POST':
        cursor = cnx.cursor()
        cursor.execute('select id from tournaments where tname = "{}"'.format(request.form['TournamentToUpdate']))
        tournaments = cursor.fetchall()
        cursor1 = cnx.cursor()
        cursor1.execute('delete from tournaments_teams where tournaments_id = {}'.format(tournaments[0][0]))
        cursor2 = cnx.cursor()
        cursor2.execute('delete from tournaments where id = {}'.format(tournaments[0][0]))
        cnx.commit()
    return redirect('/')


@app.route('/deleteteam')
def deleteteam():
    cursor = cnx.cursor(dictionary=True)
    cursor.execute('select id, teamname from teams order by teamname asc')
    teams = cursor.fetchall()
    return render_template('deleteteam.html', teams = teams)


@app.route('/deletedteam', methods=['POST', 'GET'])
def deletedteam():
    if request.method == 'POST':
        cursor = cnx.cursor()
        cursor.execute('select id from teams where teamname = "{}"'.format(request.form['TeamToUpdate']))
        teams = cursor.fetchall()
        cursor1 = cnx.cursor()
        cursor1.execute('delete from tournaments_teams where team_id = {}'.format(teams[0][0]))
        cursor2 = cnx.cursor()
        cursor2.execute('delete from teams_players where team_id = {}'.format(teams[0][0]))
        cursor3 = cnx.cursor()
        cursor3.execute('delete from teams where id = {}'.format(teams[0][0]))
        cnx.commit()
    return redirect('/')


@app.route('/deleteplayer')
def deleteplayer():
    cursor = cnx.cursor(dictionary=True)
    cursor.execute('select id, fname, lname from players order by fname asc')
    players = cursor.fetchall()
    return render_template('deleteplayer.html', players = players)


@app.route('/deletedplayer', methods=['POST', 'GET'])
def deletedplayer():
    if request.method == 'POST':
        cursor = cnx.cursor()
        selected_player = request.form['PlayerToUpdate']
        sp = selected_player.split()
        cursor.execute('select id from players where fname = "{}" and lname = "{}"'.format(sp[0], sp[1]))
        spid = cursor.fetchall()
        print(spid[0][0])
        cursor1 = cnx.cursor()
        cursor1.execute('delete from teams_players where player_id = {}'.format(spid[0][0]))
        cursor2 = cnx.cursor()
        cursor2.execute('delete from players where id = {}'.format(spid[0][0]))
        cnx.commit()
    return redirect('/')
