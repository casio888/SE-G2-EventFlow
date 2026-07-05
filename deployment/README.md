# Deployment vom Porduktionsserver

Diese Readme gibt eine kurze Anleitung wie EventFlow auf dem seproject04 Server deployt werden kann.

## Kurzanleitung Lokal/Produktionsserver

Siehe docs/technical/deployment.adoc


## Container neu bauen

Sollte sich etwas an der Struktur der Dockerfiles geändert haben, können die Images mit folgendem Befehl neu gebaut werden:

`docker compose build`

Beziehungsweise kann zum starten folgender Befehl genutzt werden:

`docker compose up -d --build`

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