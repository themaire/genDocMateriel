import os
import locale
locale.setlocale(locale.LC_TIME,'')
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
BASE_ID = os.getenv("BASE_ID")
INVENTORY_ID = os.getenv("INVENTORY")

# print(ACCESS_TOKEN)
# print(BASE_ID)

from pyairtable import Api
api = Api(ACCESS_TOKEN)

tableInformatique = api.table(INVENTORY_ID, 'Informatique')
tableMobiles = api.table(INVENTORY_ID, 'Mobiles')
tableSalarieAntenne = api.table(INVENTORY_ID, 'Salariés et antennes')

def getSalaries(table):
    salaries = {}
    for salarie in table:
        salaries[salarie['id']] = {'nom' : salarie['fields']['prenom'] + ' ' + salarie['fields']['nom'].upper(), 'cd_salarie' : salarie['fields']['cd_salarie']}
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

salaries = getSalaries(tableSalarieAntenne.all(formula="{statut}"))

def getAttribution(table):
    allAttributions = []
    for attribution in table.all(formula="{bon à faire signer}"):
        attrib = {}
        if('Employé désigné' in attribution['fields'].keys()):
            attrib['cd_salarie'] = salaries[  attribution['fields']['Employé désigné'][0]  ]['cd_salarie']
        else:
            print("on continue")
            continue
        allAttributions.append(attrib)
    return allAttributions

allAttributionInfo = getAttribution(tableInformatique)
allAttributionMobile = getAttribution(tableMobiles)

types = ('info','mobile')
listeSalaries = {}
for type in types:
    if type == 'info':
        attribType = allAttributionInfo
    elif type == 'mobile':
        attribType = allAttributionMobile

    salariesAfaire = []
    for i in attribType :
        if i['cd_salarie'] not in salariesAfaire:
            salariesAfaire.append(i['cd_salarie'])
    listeSalaries[type] = salariesAfaire

    
# print("Liste des", len(salariesAfaire), "salariesAfaire pour fabriquer les documents PDF automatiquement :", salariesAfaire)
# print()

import asyncio
from pyppeteer import launch

date=datetime.now()
date=datetime.strftime( date, "%Y%m%d" )

async def generate_pdf(url, pdf_path):
    browser = await launch()
    page = await browser.newPage()
    
    await page.goto(url)
    
    await page.pdf({'path': pdf_path, 'format': 'A4'})
    
    await browser.close()

    print("Fichier terminé :", pdf_path)

# Run the function two times (info and mobile)
cpt = 0
for type in types:
    for i in listeSalaries[type]:
        url = 'http://localhost:5000/' + type + '/' + i
        file = date + '_' + type + '_' + i + '_remise_materiel' + '.pdf'
        asyncio.get_event_loop().run_until_complete(generate_pdf(url, 'pdf/' + file))
        cpt += 1

print(str(cpt), "fichiers générés. :-)")