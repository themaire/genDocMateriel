# Generateur de fiche de remise de materiel

J'utilise ce projet pour generer des fiches de remises de materiel sans efforts. Utilisant une base de données chez airtable.com de type nocode, le script Python utilise l'api de Airtable pour recuperer les informations afin de les montrer sous forme de page HTML au format A4 grâce à la bibliothèque Flask.

Au demarrage du script Flask, les données sont rapatriés en mémoire. La route /refresh premet de mettre à jour cette liste et de pouvoir lister les fiches qui sont en attente de signature.

Pour visualiser une fiche il suffit de se rendre de taper le type de fiche ( mobile ou info) et les initiales de la personne par exemple : /info/ab.

Le fichier Dockerfile permet de fabriquer l'image adequat prendant en compte les dépendances à utiliser.