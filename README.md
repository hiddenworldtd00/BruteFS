# BRUTEFORCE - Accès Base de Données Web

> **Développé par hacker_tchadien** - Outil de test de sécurité des bases de données web

## Description

BRUTEFORCE est un outil Python avancé permettant de tester la sécurité des bases de données web par force brute. Il suffit de fournir l'URL du site web et l'outil détecte automatiquement :

- Le type de base de données (MySQL, PostgreSQL, MSSQL, Oracle, MongoDB)
- Les ports ouverts
- Les panneaux d'administration (phpMyAdmin, Adminer, etc.)
- Les endpoints d'API exposés
- Les fichiers de configuration sensibles (.env, config.php, etc.)

## Fonctionnalités

### 1. Détection automatique
- Scan des ports de base de données courants
- Détection du type de base de données
- Recherche de panneaux d'administration web
- Découverte d'endpoints d'API

### 2. Attaque par dictionnaire
- Liste de mots de passe intégrée (1000+ mots courants)
- Support de listes personnalisées
- Attaque multi-threadée rapide
- Génération de combinaisons intelligentes

### 3. Attaque par force brute
- Génération de mots de passe par patterns
- Brute force sur les hashes
- Support de différents algorithmes de hash

### 4. Rapports détaillés
- Export JSON, CSV, TXT
- Historique complet des tentatives
- Statistiques de l'attaque

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

### Lancer l'outil

```bash
python bruteforce.py
```

### Exemple de session

```
╔══════════════════════════════════════════════════════════════╗
║           BRUTEFORCE - Base de Données Web v1.0              ║
║              Développé par hacker_tchadien                   ║
╚══════════════════════════════════════════════════════════════╝

[1] Scanner un site web (URL)
[2] Brute force base de données
[3] Attaque par dictionnaire
[4] Tester une connexion manuelle
[5] Historique
[6] Aide
[7] Quitter

Choix : 1

URL du site web (ex: https://monsite.com) : https://example.com

Scan en cours...

╔══════════════════════════════════════════════════════════════╗
║                    RÉSULTATS DU SCAN                         ║
╚══════════════════════════════════════════════════════════════╝

URL cible : https://example.com
IP : 93.184.216.34

Ports ouverts :
  [+] Port 3306 (MySQL) - OUVERT
  [+] Port 5432 (PostgreSQL) - OUVERT
  [+] Port 22 (SSH) - OUVERT

Panneaux d'administration trouvés :
  [+] https://example.com/phpmyadmin
  [+] https://example.com/adminer.php

Endpoints d'API :
  [+] https://example.com/api/v1/users
  [+] https://example.com/api/v1/login

Fichiers sensibles :
  [+] https://example.com/.env (EXPOSÉ !)
  [+] https://example.com/config.php

╔══════════════════════════════════════════════════════════════╗
║                 INFORMATIONS EXTRAITES                       ║
╚══════════════════════════════════════════════════════════════╝

Fichier .env trouvé !
Contenu :
  DB_HOST=localhost
  DB_NAME=example_db
  DB_USER=admin
  DB_PASS=********

Clés API trouvées :
  [+] sk_live_51H7...XYZ (Stripe)
  [+] AKIA...123 (AWS)
```

## Modes d'attaque

### Attaque par dictionnaire
Utilise une liste de mots de passe courants pour tester les combinaisons.

### Attaque par force brute pure
Génère toutes les combinaisons possibles de caractères.

### Attaque hybride
Combine dictionnaire + mutations (ajout de chiffres, symboles, etc.).

## Avertissement Légal

**Cet outil est strictement destiné à des fins de test de sécurité sur vos propres systèmes.**

- Utilisez BRUTEFORCE uniquement sur des systèmes que vous possédez ou avec autorisation écrite explicite
- L'accès non autorisé à un système informatique est un délit pénal dans la plupart des pays
- L'auteur décline toute responsabilité en cas d'utilisation malveillante ou illégale
- Respectez toujours les lois locales en vigueur

## Auteur

**hacker_tchadien** - Expert en sécurité informatique

## Licence

Usage éducatif et tests de sécurité autorisés uniquement.
