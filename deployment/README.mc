# Deployment vom Porduktionsserver

Diese Readme gibt eine kurze Anleitung wie EventFlow auf dem seproject04 Server deployt werden kann.

## Kurzanleitung

```
# Korrekten Branch auschecken
git checkout min

# Ins deployment verzeichnis wechseln
cd /home/seproject/SE-G2-EventFlow/deployment

# Container neu starten
docker compose down
docker compose up -d

# Eventuelle Django migrationen anwenden
docker exec -it deployment-django-1 sh
django> python manage.py migrate
```

## Container neu bauen

Sollte sich etwas an der Struktur der Dockerfiles geändert haben, können die Images mit folgendem Befehl neu gebaut werden:

`docker compose build`

Beziehungsweise kann zum starten folgender Befehl genutzt werden:

`docker compose up -d --build`

