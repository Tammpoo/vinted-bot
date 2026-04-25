# Vinted Notifications Bot

Bot per monitorare Vinted e ricevere notifiche in tempo reale quando vengono pubblicati nuovi articoli che corrispondono alle tue ricerche.

## Funzionalita

- **Monitoraggio Real-Time**: Controlla Vinted ogni X secondi per nuovi articoli
- **Web UI**: Interfaccia web per gestire query, configurazione e visualizzare articoli
- **Notifiche Telegram**: Ricevi alert direttamente su Telegram
- **Feed RSS**: Sottoscrivi i risultati con qualsiasi lettore RSS
- **Multi-Paese**: Funziona su tutti i domini Vinted (IT, FR, DE, ES, ecc.)
- **Filtri Avanzati**: Parole vietate, allowlist paesi, banwords
- **Supporto Proxy**: Per evitare rate limiting

## Deploy su Railway

### 1. Crea un account Railway

Vai su [railway.app](https://railway.app) e registrati (puoi usare GitHub).

### 2. Crea un nuovo progetto

1. Clicca "New Project"
2. Seleziona "Deploy from GitHub repo"
3. Collega la tua repository o carica i file manualmente

### 3. Deploy

Railway rilevera automaticamente il `Dockerfile` e il `railway.toml` e effettuera il deploy.

### 4. Configura le variabili d'ambiente (opzionale)

Nel pannello Railway, vai su "Variables" e aggiungi:

| Variabile | Descrizione | Default |
|-----------|-------------|---------|
| `PORT` | Porta per la Web UI | `8000` |

### 5. Configura il bot dalla Web UI

1. Apri l'URL fornito da Railway
2. Vai su "Configurazione"
3. Inserisci il **Token del bot Telegram** (ottenuto da @BotFather)
4. Inserisci il **Chat ID** Telegram
5. Abilita Telegram
6. Aggiungi le query di ricerca dalla sezione "Query"

### 6. Telegram Bot

1. Cerca @BotFather su Telegram
2. Crea un nuovo bot con `/newbot`
3. Copia il token e inseriscilo nella Web UI
4. Ottieni il tuo Chat ID scrivendo al bot e usando @userinfobot

## Comandi Telegram

| Comando | Descrizione |
|---------|-------------|
| `/start` | Mostra aiuto |
| `/hello` | Verifica se il bot funziona |
| `/add_query <url>` | Aggiungi una query |
| `/remove_query <num>` | Rimuovi una query |
| `/remove_query all` | Rimuovi tutte le query |
| `/queries` | Lista query |
| `/create_allowlist` | Crea allowlist paesi |
| `/delete_allowlist` | Elimina allowlist |
| `/add_country <XX>` | Aggiungi paese |
| `/remove_country <XX>` | Rimuovi paese |
| `/allowlist` | Mostra allowlist |

## Esempio Query

Aggiungi questa URL come query per monitorare Nike sotto i 50 euro:

```
https://www.vinted.it/catalog?search_text=nike&price_to=50&currency=EUR&order=newest_first
```

Puoi copiare qualsiasi URL di ricerca Vinted e usarla come query!

## Struttura del Progetto

```
vinted-bot/
|-- vinted_notifications.py    # Entry point
|-- core.py                     # Logica scraping
|-- db.py                       # Database SQLite
|-- logger.py                   # Logging
|-- proxies.py                  # Gestione proxy
|-- requirements.txt            # Dipendenze Python
|-- Dockerfile                  # Container
|-- railway.toml                # Config Railway
|-- pyVintedVN/                 # Moduli scraping Vinted
|-- telegram_bot_plugin/        # Bot Telegram
|-- rss_feed_plugin/            # Feed RSS
|-- web_ui_plugin/              # Interfaccia Web
|-- migrations/                 # Migrazioni DB
|-- data/                       # Database (creato runtime)
|-- logs/                       # Log (creato runtime)
```

## Tecnologie

- **Python 3.11**
- **Flask** - Web UI
- **python-telegram-bot** - Bot Telegram
- **APScheduler** - Scheduling
- **SQLite** - Database
- **Docker** - Containerizzazione

## License

AGPL-3.0
