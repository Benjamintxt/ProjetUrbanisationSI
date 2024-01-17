# Simulateur de Webhook Petzi

Projet dans le cadre du cours "Urbanisation des SI" à la haute école d'arc de gestion, Neucâtel. Ce projet utilise un simulateur de Webhook Petzi afin de simuler l'achat d'un billet 
et d'envoyer une requête de webhook à un serveur Flask puis de persister grâce à SQLite. 
Le projet comprend un backend Flask, un message broker Kafka et une interface utilisateur Vue.js pour la visualisation en temps réel des données (websocket).

## Utilisation

### 1. Simuler des événements de webhook

Exécutez le simulateur de webhook Petzi avec la commande suivante :

```bash
python petzi_simulator.py http://127.0.0.1:5000/webhook GoofyKey
```
Cette commande simule l'achat d'un billet et envoie une requête de webhook simulée au serveur Flask spécifié.

### 2. Exécuter avec Docker

Utilisez Docker pour configurer facilement le projet avec le fichier docker-compose.yml fourni. Assurez-vous que Docker est installé sur votre machine.

```bash
docker-compose -f docker-compose.yml up -d
```

Cette commande démarrera le backend Flask, le message Broker Kafka et d'autres composants nécessaires.

### 3. Exécuter le Backend

Exécutez le backend Flask en exécutant la commande suivante dans le répertoire flask_backend :

```bash
python app.py
```

Cette commande démarre le serveur Flask, qui écoute les événements de webhook entrants, valide les signatures et envoie des données à Kafka.

### 4. Exécuter le Frontend

Accédez au répertoire vue_frontend et exécutez l'interface utilisateur Vue.js avec les commandes suivantes :

```bash
npm install  # Installer les dépendances (uniquement nécessaire la première fois)
npm run dev   # Démarrer le serveur de développement
```

Cette commande installe les dépendances et démarre le serveur de développement Vue.js pour la visualisation en temps réel des données.

## Composants

Backend Flask : Écoute les événements de webhook entrants, valide les signatures et envoie des données à Kafka.

Message Broker Kafka : Stocke et distribue des événements entre les composants.

Frontend Vue.js : Fournit une visualisation en temps réel des ventes de billets à l'aide de connexions WebSocket.

## Note importante
Assurez-vous de remplacer la clé secrète fictive (GoofyKey) par votre clé secrète réelle dans les commandes et configurations.