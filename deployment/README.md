# Deployment vom Porduktionsserver

Diese Readme gibt eine kurze Anleitung wie EventFlow auf dem seproject04 Server deployt werden kann.

## Kurzanleitung Produktionsserver

```
# Korrekten Branch auschecken
git checkout main

# Ins deployment verzeichnis wechseln
cd /home/seproject/SE-G2-EventFlow/deployment

# Container neu starten
docker compose down
docker compose up -d

# Eventuelle Django migrationen anwenden
docker exec -it deployment-django-1 sh
django> python manage.py migrate
```


# ## Container neu bauen

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
ln -s docker-compose.yml docker-compose.yml.dev
```

3. Baue Images
```
docker compose build
```

4. Starte stack
```
docker compose up -d
```