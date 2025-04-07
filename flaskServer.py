import os
import sys
import locale
from datetime import datetime
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

CURRENT_YEAR = datetime.now().year

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
BASE_ID = os.getenv("BASE_ID")
INVENTORY_ID = os.getenv("INVENTORY")

# print(ACCESS_TOKEN)
# print(BASE_ID)

from pyairtable import Api
api = Api(ACCESS_TOKEN)


# Functions
def getSalaries(table):
    """
    Fonction pour récupérer les informations des salariés à partir d'une table Airtable.
    Cette fonction construit un dictionnaire contenant les informations des salariés actifs.

    Args:
        table (list): Liste des enregistrements de la table Airtable.

    Returns:
        dict: Dictionnaire contenant les informations des salariés avec leur ID comme clé.
    """
    print("Fonction getSalarie( contenu de la table des salaries ) ")
    salaries = {}
    try:
        # Parcourt chaque enregistrement de la table
        for salarie in table:
            print(salarie)
            # Vérifie si le champ 'cd_salarie' est présent dans les données
            if 'cd_salarie' in salarie['fields']:
                # Ajoute les informations du salarié au dictionnaire
                salaries[salarie['id']] = {
                    'nom': salarie['fields']['prenom'] + ' ' + salarie['fields']['nom'].upper(),
                    'cd_salarie': salarie['fields']['cd_salarie']
                }
            else:
                # Si 'cd_salarie' est manquant, lève une exception avec un message d'erreur
                full_name = salarie['fields']['prenom'] + ' ' + salarie['fields']['nom'].upper()
                raise ValueError(f"La chaîne '{full_name}' n'a pas de cd_salarie.")
    except Exception as e:
        # Capture et affiche les erreurs, puis arrête le programme
        print("Erreur dans la fonction getSalaries : ", e)
        sys.exit(1)  # Arrête le programme avec un code d'erreur
    return salaries

def getEquipements(table):
    equipements = {}
    for equip in table:
        if('Spécifications' in equip['fields'].keys()):
            specs = equip['fields']['Spécifications']
        else:
            specs = ''
        equipements[equip['id']] = {'nom' : equip['fields']['Nom du modèle'], 'type' : equip['fields']['Type'], 'specs' : specs}
    return equipements

def getAttribution(table, equipements, salaries, type):
    """
    Recupère la (grande) liste des attributions par type de materiel.
    """

    allAttributions = []
    for attribution in table.all(sort=["Date attribuée"], formula="{bon à faire signer}", max_records=70):
        attrib = {}

        if(attribution['fields']['Employé désigné'][0] == 'recyOYBn5FsjPDusm' or attribution['fields']['Employé désigné'][0] == 'recZaeCVZUr5dSm1E'):
            # Si c'est l'antenne de Chaumont ou le salarié inconnu
            print(attribution['fields']['Motif'] + ", on passe.")
            continue

        # print(attribution['fields'])
        print(attribution)

        if('Employé désigné' in attribution['fields'].keys()):
        # Traitement si un employé est assigné sinon on "continue"

            # print("attribution['fields']['Employé désigné'][0] =", attribution['fields']['Employé désigné'][0])
            print("On s'occupe de l'employé", salaries[  attribution['fields']['Employé désigné'][0]  ])
            print("On s'occupe de l'employé", salaries[  attribution['fields']['Employé désigné'][0]  ]['nom'])
            attrib['cd_salarie'] = salaries[  attribution['fields']['Employé désigné'][0]  ]['cd_salarie']

            if(attribution['fields']['Employé désigné'][0] in salaries.keys()):
                # print(salaries[  attribution['fields']['Employé désigné'][0]  ]['nom'])
                attrib['salarie'] = salaries[  attribution['fields']['Employé désigné'][0]  ]['nom']
            
            if('Date attribuée' in attribution['fields'].keys()):
                # print(attribution['fields']['Date attribuée'])
                # Afficher la date par exemple comme ceci : 11 janvier 2024
                # strPtime dans strFtime _   🎈😀
                attrib['date'] = datetime.strftime( datetime.strptime( attribution['fields']['Date attribuée'], "%Y-%m-%d" ), "%B %Y" ).title()
            else:
                attrib['date'] = "Pas de date d'affectation."
            
            if('Modèle' in attribution['fields'].keys()):
                listModeles = []

                # Bouclier sur les ID de la table des modeles d'équipements
                for modeleID in attribution['fields']['Modèle']:
                    # Verifier que l'ID de modele en question existe dans toute la table des modèles d'equipements
                    if(modeleID in equipements.keys()):
                        listModeles.append( equipements[ modeleID ] )
                    
                attrib['modele'] = listModeles
            else:
                attrib['modele'] = 'Pas de modèle communiqué.'

            # Test en fonction du type de materiel
            if(type == 'info'):
                attrib['Type materiel'] = attribution['fields']['Type materiel']

                if('Numéro de série PC' in attribution['fields'].keys()):
                    # print(attribution['fields']['Numéro de série PC'])
                    attrib['serial'] = attribution['fields']['Numéro de série PC']
                else:
                    attrib['serial'] = 'Pas de numéro de serie communiqué.'

            elif(type == 'mobile'):
                if('IMEI 1' in attribution['fields'].keys()):
                    attrib['IMEI'] = attribution['fields']['IMEI 1']

                if('Numéro téléphone (from carte_SIM)' in attribution['fields'].keys()):
                    attrib['no_ligne'] = attribution['fields']['Numéro téléphone (from carte_SIM)']

        else:
            print("on continue car pas d'employé désigné dans", attribution)
            continue
        allAttributions.append(attrib)
    return allAttributions

def regroupAttrib(cd_salarie, attributions):
    # Est utilisé au moment de charger une fiche.
    # Regroupe toutes les attributions de materiel de la meme personne
    regroup = []
    for i in attributions:
        if(cd_salarie in i.values()):
            regroup.append(i)

    return regroup

def showAttributions(attributions, mode = 'all'):
    if mode == "all":
        # Affiche la liste des attribution :
        print("Liste des attributions :")
        for i in attributions.values():
            print(i)
    elif mode == "cd":
        # Affiche la liste des attribution :
        print("Liste des attributions :")
        for key in attributions.keys():
            for i in attributions[key]:
                print(i['cd_salarie'])
    print()

def refreshData():

    tableInformatique = api.table(INVENTORY_ID, 'Informatique')
    tableMobiles = api.table(INVENTORY_ID, 'Mobiles')
    tableSalarieAntenne = api.table(INVENTORY_ID, 'Salariés et antennes')

    tableEquipements = api.table(INVENTORY_ID, 'Equipements')
    equipements = tableEquipements.all()

    # salaries = getSalaries(tableSalarieAntenne.all(formula="{statut}"))
    salaries = getSalaries(tableSalarieAntenne.all(view="Personnes actives"))

    # print("Liste des", len(salaries), "salaries :", salaries)
    # print()

    equipements = getEquipements(tableEquipements.all())
    
    # print("Liste des", len(equipements), "equipements :", equipements)
    # print()

    global allAttribs
    allAttribs = {}
    allAttribs['info'] = getAttribution(tableInformatique, equipements, salaries, 'info')
    allAttribs['mobile'] = getAttribution(tableMobiles, equipements, salaries, 'mobile')

    return 0

# Main programm
# Start with get all data
refreshData()
# showAttributions(allAttribs)

from flask import Flask, render_template

app = Flask(__name__)

@app.context_processor
def inject_current_year():
    return {'current_year': CURRENT_YEAR}

@app.route('/refresh')
def refresh():

    refreshData()
    return render_template('refresh.html')

@app.route('/list')
def list():
    refreshData()
    return render_template('list_salaries.html', attributions=allAttribs)

@app.route('/info/<id>')
def info(id=None):

    thisAttribs = regroupAttrib(id, allAttribs['info'])
    print(str(len(thisAttribs)), "attribs de ",id, thisAttribs)

    # return render_template('bon_informatique.html', id=id, attribs=attribs)
    return render_template('remise_info.html', id=id, attribs=thisAttribs)

@app.route('/mobile/<id>')
def mobile(id=None):

    thisAttribs = regroupAttrib(id, allAttribs['mobile'])
    # print(str(len(attribs)), "attribs de ",id, attribs)

    # return render_template('bon_informatique.html', id=id, attribs=attribs)
    return render_template('remise_mobile.html', id=id, attribs=thisAttribs)

# Les fiches peuvent maintenant etre requetés par exemple sur l'url http://192.168.27.66:5000/info/SOPY
