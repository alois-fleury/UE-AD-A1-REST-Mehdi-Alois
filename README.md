# UE-AD-A1-REST - Mehdi BAGHDADI et Aloïs Fleury

[Lien du TP](https://helene-coullon.fr/pages/ue-ad-fil-25-26/tp-rest/)

## Initialisation et lancement du projet

Pour lancer chaque microservice : se placer dans le dossier et exécuter le fichier du même nom avec Python. Exemple sur Windows :
```bash
cd .\booking\
python .\booking.py
```

Attention, il faut bien veiller à ce que le service user soit lancé lorsqu'on veut tester (car pour certaines requêtes, les droits utilisateurs sont vérifiés).

## Architecture utilisée

L'architecture suivie est en microservices et son schéma est le suivant : 

![Schéma de l'architecure du projet](images/schema-architecture-projet.png)

## Tests et exemples

Les tests ont été réalisés sur Insomnia (voir dossier [./insomnia](./insomnia)).

Pour la première partie ne vous souciez pas des fichiers Docker, cela sera abordé par la suite en séance 4.
