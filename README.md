
# Auto-émargement Pegasus (ESTIA)

Automatisez le processus d'émargement sur la plateforme Pegasus d'ESTIA grâce à ce programme, qui vous permet de ne plus jamais oublier de signer vos présences. 

En utilisant vos signatures enregistrées, il assure un émargement régulier et fiable sans effort. Dites adieu aux tâches chronophages de pointage manuel et concentrez-vous sur l'essentiel !

![logo](https://i.ibb.co/b1JpF9B/Logo.png)
### 🛠 Pré-requis

Avant de commencer, assurez-vous d'avoir les éléments suivants installés :

- **Python 3.12** ou version ultérieure
- **Google Chrome version 130** ou supérieure
- **Git** (pour cloner le dépôt)

### 🚀 Installation

Suivez ces étapes pour installer et configurer le programme sur votre machine :

1. **Ouvrir l'Invite de Commandes** :
   - Appuyez sur `Win + R`, tapez `cmd`, puis appuyez sur `Entrée`. Cela ouvrira la fenêtre de l'invite de commandes.


2. **Créer le Dossier de Projet** :
   - Utilisez les commandes suivantes pour créer le dossier principal du projet :
   ```bash
   mkdir C:\WORKSPACE\Python
   mkdir C:\WORKSPACE\Python\AutoEmargementPegasus

3. **Cloner le Dépôt GitHub** :
   - Dans l'invite de commandes, exécutez la commande suivante pour cloner le dépôt :
   ```bash
   git clone https://github.com/outout14/ton_depot.git C:\WORKSPACE\Python\AutoEmargementPegasus

4. **Naviguer vers le Dossier du Projet** :
   - Entrez dans le dossier du projet :
   ```bash
   cd C:\WORKSPACE\Python\AutoEmargementPegasus
   
5. **Installer les Dépendances** :
   - Installez toutes les dépendances en utilisant `pip` :
   ```bash
    pip install -r requirements.txt

6. **Lancer le Script de Configuration** :
   - Exécutez le script de configuration pour renseigner les informations nécessaires à l'automatisation :
   ```bash
   python setup_config.py

7. **Exécuter l’Automatisation d'Émargement** :
   - Lancez le script PowerShell `EmargementScheduler.ps1`, qui planifiera les émargements hebdomadaires :
   ```bash
   .\EmargementScheduler.ps1
   
## 🏃‍♂️ Démarrage

L'émargement automatique commencera automatiquement après la configuration. Pour émarger manuellement, lancez le script suivant :
   ```bash
   python run_AutoEmargementPegasus.py
   ```

## 🛠 Fabriqué avec

[![forthebadge](https://forthebadge.com/images/badges/it-works-dont-know-how.svg)](https://forthebadge.com)

## 📌 Versions

**Dernière version :** 1.0


## 👤 Auteurs

* **Valentin** _alias_ [@outout14](https://github.com/outout14)

## 📝 License

Ce projet est sous licence ``WTFTPL`` - voir le fichier [LICENSE.md](LICENSE.md) pour plus d'informations.


