# Deployment vom Porduktionsserver

Diese Readme gibt eine kurze Anleitung wie EventFlow auf dem seproject04 Server deployt werden kann.

## Kurzanleitung Produktionsserver

```
# Korrekten Branch auschecken
git checkout main
# Ins deployment verzeichnis wechseln
cd /home/seproject/SE-G2-EventFlow/deployment

# Link anlegen
ln -s docker-compose.yml.prod docker-compose.yml

# Container neu starten
docker compose down
docker compose up -d

# Eventuelle Django migrationen anwenden
docker exec -it deployment-django-1 sh
django> python manage.py migrate
```


### Container neu bauen

Sollte sich etwas an der Struktur der Dockerfiles geändert haben, können die Images mit folgendem Befehl neu gebaut werden:

`docker compose build`

Beziehungsweise kann zum starten folgender Befehl genutzt werden:

`docker compose up -d --build`


## Kurzanleitung Lokal

### Erstes Setup

1. Installiere docker.

2. Setze dev docker-compose
```
cd deployment
ln -s -f docker-compose.yml.dev docker-compose.yml
```

3. Baue Images
```
docker compose build
```

4. Erstelle config Dateien
```
cp .env.django.example .env.django
# Secret key setzen und und db passwort eintragen

# Schreibe db Passwort in diese Datei
echo "<password>" > postgres_db_password.txt
```

5. Starte stack
```
docker compose up -d
```

## Checkout von neuen Branches

Bei checkouts von anderen Branches kann es zu unterschiedlichen Datenbank-Ständne kommen, um das zu beheben muss man den Stack starten

```
cd deployment & docker compose up -d
```

Und dann in den docker container springen und migrations erstellen und ausführen

```
docker exec -it deployment-django-1 sh

python manage.py makemigrations
python manage.py migrate
```

Dann sollte die DB auf dem korrekten Stand des Branches sein.