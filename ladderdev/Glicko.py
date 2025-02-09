#!/usr/bin/python
# -*- coding: latin-1 -*-

#Glicko

import math
from common import victoryChance
import copy

q=math.log(10.0)/400
RDmin=25
RDmax=100
c=20

def g(RD):
	return pow(1.0+3.0*q*q*RD*RD/math.pi/math.pi,-0.5)
def expectedScore(R1,R2,RD2):
	return 1.0/(1.0+pow(10,-g(RD2)*(R1-R2)/400))

def newPlayer():
	return {'R':1500.0,'RD':RDmax,'A':0.0,'d2':0.0,'w':0,'l':0,'elo':1000}

def update(p1rating,p2rating,outcome):
	S={}
	outcome=int(outcome)
	if outcome == 1:
		S['p1']=1.0
	elif outcome == 2:
		S['p1']=0.0
	else: #if outcome == 0
		S['p1']=0.5
	S['p2']=1.0-S['p1']

	E={}
	E['p1']=expectedScore(p1rating['R'],p2rating['R'],p2rating['RD'])
	E['p2']=expectedScore(p2rating['R'],p1rating['R'],p1rating['RD'])

	p1rating['A']+=g(p2rating['RD'])*(S['p1']-E['p1'])
	p1rating['d2']+=pow(g(p2rating['RD']),2)*E['p1']*(1.0-E['p1'])

	p2rating['A']+=g(p1rating['RD'])*(S['p2']-E['p2'])
	p2rating['d2']+=pow(g(p1rating['RD']),2)*E['p2']*(1.0-E['p2'])	

	# W/L
	p1rating['w']+=S['p1']
	p1rating['l']+=S['p2']
	p2rating['w']+=S['p2']
	p2rating['l']+=S['p1']

	# ELO
	qa = pow(10, p1rating['elo']/480)
	qb = pow(10, p2rating['elo']/480)
	ea = qa/(qa+qb)
	eb = qb/(qa+qb)
	p1rating['elo'] += 32 * (S['p1'] - ea) 
	p2rating['elo'] += 32 * (S['p2'] - eb) 

	#return p1rating,p2rating,victoryChance(p1rating['R'],p1rating['RD'],p2rating['R'],p2rating['RD'])
	return p1rating,p2rating,E['p1']

def newRatingPeriod(rating):

	if rating['d2'] == 0.0:
		if rating['A'] != 0:
			print('WTF?')
			print(rating['A'],rating['d2'])
		rating['RD']=math.sqrt(pow(rating['RD'],2)+c*c)
	else:
		d2=pow(q*q*rating['d2'],-1.0)
		rating['R']+=q/(pow(rating['RD'],-2)+1.0/d2)*rating['A']
		rating['RD']=pow(pow(rating['RD'],-2)+1.0/d2,-0.5)
	
	if rating['RD']>RDmax:
		rating['RD']=RDmax
	if rating['RD']<RDmin:
		rating['RD']=RDmin

	rating['A']=0
	rating['d2']=0

	#print rating['RD']
	return rating

def provisional(rating):
	return newRatingPeriod(copy.deepcopy(rating))

def headers():
	return 'Glicko R,Glicko RD'
def printRating(rating):
	return str(rating['R'])+','+str(rating['RD'])

def write(ratings, filename):
	usagefile=open(filename,'w')
	usagefile.write(" + ---- + ------------------ + ---- + ------------ + ----- + ----- + -------- + \n")
	usagefile.write(" | Rank | Username           | ELO  | Glicko       | W     | L     | Win Rate |\n")
	usagefile.write(" + ---- + ------------------ + ---- + ------------ + ----- + ----- + -------- + \n")
	# for username, d in ratings.items():
	for i, (username, d) in enumerate(sorted(ratings.items(), key=lambda x: x[1]['elo'], reverse=True)):
		usagefile.write(' | %-4d | %-18s | %-4d | %-4d \u00B1 %5.1f | %-5.1f | %-5.1f | %7.3f%% |\n' % (i+1, username, d['elo'], d['R'], d['RD'], d['w'], d['l'], 100*d['w'] / (d['w']+d['l'])))
	usagefile.write(" + ---- + ------------------ + ---- + ------------ + ----- + ----- + -------- + \n")
	usagefile.close()

