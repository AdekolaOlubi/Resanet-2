#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import *
from modeles import modeleResanet
from technique import datesResanet
import requests

app = Flask( __name__ )
app.secret_key = 'resanet'


@app.route( '/' , methods = [ 'GET' ] )
def index() :
	return render_template( 'vueAccueil.html' )

@app.route( '/usager/session/choisir' , methods = [ 'GET' ] )
def choisirSessionUsager() :
	return render_template( 'vueConnexionUsager.html' , carteBloquee = False , echecConnexion = False , saisieIncomplete = False )

@app.route( '/usager/seConnecter' , methods = [ 'POST' ] )
def seConnecterUsager() :
	numeroCarte = request.form[ 'numeroCarte' ]
	mdp = request.form[ 'mdp' ]

	if numeroCarte != '' and mdp != '' :
		usager = modeleResanet.seConnecterUsager( numeroCarte , mdp )
		if len(usager) != 0 :
			if usager[ 'activee' ] == True :
				session[ 'numeroCarte' ] = usager[ 'numeroCarte' ]
				session[ 'nom' ] = usager[ 'nom' ]
				session[ 'prenom' ] = usager[ 'prenom' ]
				session[ 'mdp' ] = mdp
				
				return redirect( '/usager/reservations/lister' )
				
			else :
				return render_template('vueConnexionUsager.html', carteBloquee = True , echecConnexion = False , saisieIncomplete = False )
		else :
			return render_template('vueConnexionUsager.html', carteBloquee = False , echecConnexion = True , saisieIncomplete = False )
	else :
		return render_template('vueConnexionUsager.html', carteBloquee = False , echecConnexion = False , saisieIncomplete = True)


@app.route( '/usager/seDeconnecter' , methods = [ 'GET' ] )
def seDeconnecterUsager() :
	session.pop( 'numeroCarte' , None )
	session.pop( 'nom' , None )
	session.pop( 'prenom' , None )
	return redirect( '/' )


@app.route( '/usager/reservations/lister' , methods = [ 'GET' ] )
def listerReservations() :
	tarifRepas = modeleResanet.getTarifRepas( session[ 'numeroCarte' ] )
	
	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )
	
	solde = '%.2f' % ( soldeCarte , )

	aujourdhuifr= datesResanet.getDateAujourdhuiFR()
	
	aujourdhui = datesResanet.getDateAujourdhuiISO()
	
	days=['Lundi','Mardi','Mercredi','Jeudi','vendredi']

	datesPeriodeISO = datesResanet.getDatesPeriodeCouranteISO()
	
	datef = modeleResanet.getjourferie( datesPeriodeISO[ 0 ] , datesPeriodeISO[ -1 ] )
	
	datesResas = modeleResanet.getReservationsCarte( session[ 'numeroCarte' ] , datesPeriodeISO[ 0 ] , datesPeriodeISO[ -1 ] )
	
	dates = []
	for uneDateISO in datesPeriodeISO :
		uneDate = {}
		uneDate[ 'iso' ] = uneDateISO
		uneDate[ 'fr' ] = datesResanet.convertirDateISOversFR( uneDateISO )
		
		if uneDateISO <= aujourdhui :
			uneDate[ 'verrouillee' ] = True
		else :
			uneDate[ 'verrouillee' ] = False

		if uneDateISO in datesResas :
			uneDate[ 'reservee' ] = True
		else :
			uneDate[ 'reservee' ] = False
			
		if uneDateISO in datef :
			uneDate[ 'ferie' ] = True
		else:
			uneDate[ 'ferie' ] = False
			
		if soldeCarte < tarifRepas and uneDate[ 'reservee' ] == False :
			uneDate[ 'verrouillee' ] = True
			
			
		dates.append( uneDate )
	
	if soldeCarte < tarifRepas :
		soldeInsuffisant = True
	else :
		soldeInsuffisant = False
		
	
	return render_template( 'vueListeReservations.html' , laSession = session , leSolde = solde , lesDates = dates , soldeInsuffisant = soldeInsuffisant ,aujourdhuifr=aujourdhuifr,days=days)

	
@app.route( '/usager/reservations/annuler/<dateISO>' , methods = [ 'GET' ] )
def annulerReservation( dateISO ) :
	modeleResanet.annulerReservation( session[ 'numeroCarte' ] , dateISO )
	modeleResanet.crediterSolde( session[ 'numeroCarte' ] )
	return redirect( '/usager/reservations/lister' )
	
@app.route( '/usager/reservations/enregistrer/<dateISO>' , methods = [ 'GET' ] )
def enregistrerReservation( dateISO ) :
	modeleResanet.enregistrerReservation( session[ 'numeroCarte' ] , dateISO )
	modeleResanet.debiterSolde( session[ 'numeroCarte' ] )
	return redirect( '/usager/reservations/lister' )

@app.route( '/usager/mdp/modification/choisir' , methods = [ 'GET' ] )
def choisirModifierMdpUsager() :
	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )
	solde = '%.2f' % ( soldeCarte , )
	
	return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = '' )

@app.route( '/usager/mdp/modification/appliquer' , methods = [ 'POST' ] )
def modifierMdpUsager() :
	ancienMdp = request.form[ 'ancienMDP' ]
	nouveauMdp = request.form[ 'nouveauMDP' ]
	
	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )
	solde = '%.2f' % ( soldeCarte , )
	
	if ancienMdp != session[ 'mdp' ] or nouveauMdp == '' :
		return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = 'Nok' )
		
	else :
		modeleResanet.modifierMdpUsager( session[ 'numeroCarte' ] , nouveauMdp )
		session[ 'mdp' ] = nouveauMdp
		return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = 'Ok' )

@app.route( '/gestionnaire/session/choisir' , methods = [ 'GET' ] )
def choisirSessionGestionnaire() :
	return render_template( 'vueConnexionGestionnaire.html' , echecConnexion = False , saisieIncomplete = False )


@app.route( '/gestionnaire/seconnecter' , methods = [ 'POST' ] )
def seConnecterGestionnaire() :
	login = request.form[ 'login' ]
	mdp = request.form[ 'mdp' ]

	if login != '' and mdp != '' :
		gestionnaire = modeleResanet.seConnecterGestionnaire( login , mdp )
		if len(gestionnaire) != 0 :
				session[ 'login' ] = gestionnaire[ 'login' ]
				session[ 'nom' ] = gestionnaire[ 'nom' ]
				session[ 'prenom' ] = gestionnaire[ 'prenom' ]
				session[ 'mdp' ] = mdp
				
				return redirect('/gestionnaire/liste/avecCarte')
				
		else :
			return render_template('vueConnexionGestionnaire.html',echecConnexion = True , saisieIncomplete = False )
	else :
		return render_template('vueConnexionGestionnaire.html',echecConnexion = False , saisieIncomplete = True)


@app.route( '/gestionnaire/seDeconnecter' , methods = [ 'GET' ] )
def seDeconnecterGestionnaire() :
	session.pop( 'numeroCarte' , None )
	session.pop( 'nom' , None )
	session.pop( 'prenom' , None )
	return redirect( '/' )

@app.route( '/gestionnaire/liste/avecCarte' , methods = [ 'GET' ] )
def listePersonnelAvecCarte() :
	personnel = modeleResanet.getPersonnelsAvecCarte()
	aujourdhuifr= datesResanet.getDateAujourdhuiFR()
	return render_template( 'vuePersonnelAvecCarte.html',personnel = personnel,aujourdhuifr = aujourdhuifr )

@app.route( '/gestionnaire/liste/sansCarte' , methods = [ 'GET' ] )
def listePersonnelSansCarte() :
	personnelsans = modeleResanet.getPersonnelsSansCarte()
	aujourdhuifr= datesResanet.getDateAujourdhuiFR()
	return render_template( 'vuePersonnelSansCarte.html',personnelsans = personnelsans,aujourdhuifr = aujourdhuifr )
		
@app.route( '/gestionnaire/compte/blocquer/<numero>' , methods = [ 'POST' ] )
def blocquerCompte(numero):
	modeleResanet.bloquerCarte(  numero )
	return redirect( '/gestionnaire/liste/avecCarte' )
	
@app.route( '/gestionnaire/compte/activer/<numero>', methods = [ 'POST' ] )
def activeCompte(numero):
	modeleResanet.activerCarte( numero )
	return redirect( '/gestionnaire/liste/avecCarte' )
	
@app.route( '/gestionnaire/compte/initmdp/<numero>/<nom>/<prenom>', methods = [ 'POST' ] )
def initmdp(numero,nom,prenom):
	modeleResanet.reinitialiserMdp( numero )
	personnel = modeleResanet.getPersonnelsAvecCarte()
	aujourdhuifr= datesResanet.getDateAujourdhuiFR()
	return render_template( 'vuePersonnelAvecCarte.html',personnel = personnel,aujourdhuifr = aujourdhuifr,mdpinit = True,nom = nom, prenom = prenom)
	
@app.route( '/gestionnaire/compte/creerCompte/<m>/<n>/<p>/<s>', methods = [ 'POST' ] )
def creercompte(m,n,p,s):
	aujourdhuifr= datesResanet.getDateAujourdhuiFR()
	return render_template( 'vueCreationCompteRestauration.html',aujourdhuifr = aujourdhuifr,m = m,n = n,p = p,s =s)
	
@app.route( '/gestionnaire/compte/creer/<numero>', methods = [ 'POST' ] )
def creer(numero):
	etat = request.form['etat']
	if etat == '1':
		i = True
	else :
		i = False
	ex = modeleResanet.ext(numero)
	if ex == True:
		return redirect ('/gestionnaire/liste/avecCarte')
	else:
		modeleResanet.creerCarte( numero , i )
		personnel = modeleResanet.getPersonnelsAvecCarte()
		aujourdhuifr= datesResanet.getDateAujourdhuiFR()
		return render_template( 'vuePersonnelAvecCarte.html',personnel = personnel,aujourdhuifr = aujourdhuifr)


@app.route( '/gestionnaire/compte/crediter/<m>/<n>/<p>/<s>', methods = [ 'POST' ] )
def crediter(m,n,p,s):
	aujourdhuifr= datesResanet.getDateAujourdhuiFR()
	return render_template( 'vueOperationCreditCarte.html',aujourdhuifr = aujourdhuifr,m = m,n = n,p = p,s =s)
	
	
@app.route( '/gestionnaire/compte/solde/<numero>/<n>/<p>', methods = [ 'POST' ] )
def credit(numero,n,p):
	solde = request.form['solde']
	modeleResanet.crediterCarte( numero , solde )
	return redirect ('/gestionnaire/liste/avecCarte')


@app.route( '/gestionnaire/compte/history/<m>/<n>/<p>/<s>', methods= [ 'POST' ] )							
def history(m,n,p,s):
	
	history = modeleResanet.getHistoriqueReservationsCarte(m)
	aujourdhuifr = datesResanet.getDateAujourdhuiFR()
	return render_template( 'vueHistoriqueCarte.html',aujourdhuifr = aujourdhuifr,history = history,m = m,n = n,p = p,s =s)



@app.route( '/gestionnaire/reservation/dateperso', methods = [ 'GET' ] )
def reservationParDate():
	aujourdhuifr = datesResanet.getDateAujourdhuiFR()
	return render_template( 'vueReservationParDate.html',aujourdhuifr = aujourdhuifr)

@app.route( '/gestionnaire/liste/reservation/date', methods = [ 'POST' ] )
def resereDate():
	date = request.form['date']
	perso = modeleResanet.getReservationsDate( date )
	aujourdhuifr = datesResanet.getDateAujourdhuiFR()
	return render_template( 'vuePersonneReserveDate.html',aujourdhuifr = aujourdhuifr, perso = perso, date = date)


@app.route( '/gestionnaire/reservation/dateferie', methods = [ 'GET' ] )
def dateFerie():
	date = modeleResanet.getdateferie()
	aujourdhuifr = datesResanet.getDateAujourdhuiFR()
	return render_template( 'vueJourferie.html',aujourdhuifr = aujourdhuifr, date = date)

@app.route( '/gestionnaire/reservation/timer/<d>', methods = [ 'POST' ] )
def dateFerieSupprimer(d):
	n = modeleResanet.deldateferie( d )
	return redirect ('/gestionnaire/reservation/dateferie')
	
@app.route( '/gestionnaire/reservation/dateferieInsert', methods = [ 'GET' ] )
def inserteUneDate():
	aujourdhuifr = datesResanet.getDateAujourdhuiFR()
	return render_template( 'vueDateInsert.html',aujourdhuifr = aujourdhuifr)

@app.route( '/gestionnaire/reservation/dateferieInsert/insert', methods = [ 'POST' ] )
def inserteDate():
	date = request.form['date']
	libelle = request.form['libelle']
	modeleResanet.creerdateferie( date , libelle )
	return redirect( '/gestionnaire/reservation/dateferie')

	
	

if __name__ == '__main__' :
	app.run( debug = True , host = '0.0.0.0' , port = 5000 )
