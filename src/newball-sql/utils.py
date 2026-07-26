import re
import subprocess
import unicodedata
import yaml


def readYAML(racine:str, fichiers:list) -> dict:
	"""
	Dans tous les fichiers dispos, lit le YAML et renvoie les données
	"""
	if fichiers.__len__() == 0:
		raise Exception("Pas de fichier (" + racine + ")")
	
	for fichier in fichiers:
		ext = fichier.split('.')[-1]
		if ext == "yaml" or ext == "yml":
			with open(racine + '/' + fichier) as stream:
				return yaml.safe_load(stream)
		
	raise Exception("Pas de fichier YAML (" + racine + ")")

def slugify(text:str) -> str:
	"""
	Slugifie un texte
	"""
	text = unicodedata.normalize('NFD', text)

	text = ''.join(
		c for c in text
		if unicodedata.category(c) != "Mn"
	)

	text = text.lower()

	text = re.sub(r'[^a-z0-9]+', '-', text)

	text = text.strip('-')
	text = re.sub(r'-{2,}', '-', text)

	return text

def findImage(racine:str, fichiers:list, dossierImage:str, customNom:str=None) -> str | None:
	"""
	Trouve l'image parmi les fichiers si elle existe et la copie à l'emplacement prévu
	"""
	# On force le / à la fin de la destination
	if dossierImage[-1] != '/':
		dossierImage = dossierImage + '/'
	for fichier in fichiers:
		ext = fichier.split('.')[-1]
		if ext in ["png", "jpg", "jpeg", "webp"]:
			# Si on a pas de nom custom, le nom custom est le nom de base
			if not customNom:
				customNom = fichier
			else:
				customNom = customNom + '.' + ext
			copieImage(
				racine + '/' + fichier,
				dossierImage + customNom
			)
			return customNom

def copieImage(source:str, destination:str):
	"""
	Copie une image dans un dossier

	:source: chemin de la source *(mieux vaut mettre depuis /)*
	:destination: chemin de la destination *(mieux vaut mettre depuis /)*
	"""
	commandCopie = ["rsync", "--mkpath", source, destination]
	subprocess.run(commandCopie)

def createDossier(path:str):
	"""
	Créé les dossiers nécessaires pour des ajouts de fichier
	"""
	commandCopie = ["mkdir", "-p", path]
	subprocess.run(commandCopie)
