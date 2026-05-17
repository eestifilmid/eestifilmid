# Eesti filmide ümbernimetamise tööriist

Skript võrdleb videofaile nimekirjaga ja nimetab need vajadusel ümber õigesse formaati.

## Nõuded

- Python 3.8 või uuem
- Muid pakette pole vaja

## Soovituslik kaustade struktuur

```
Media/
├── Eesti Filmid/
│   ├── Mingi Film (Some Movie) (2020).mkv
│   └── ...
├── Eesti Multikad/
│   ├── Ämblikmees (The Spectacular Spider-Man) (2008).mkv
│   └── ...
└── Scripts/
    ├── start.py
    ├── filmid.txt
    └── multikad.txt
```

## Nimekirjafailide formaat

`filmid.txt` ja `multikad.txt` — iga film omareal:

```
Eesti tiitel (Inglise tiitel) (aasta) (tmdb)
```

- `(tmdb)` on valikuline TMDb ID number
- Näide: `Ämblikmees (The Spectacular Spider-Man) (2008) (7446)`

## Failinime formaat pärast ümbernimetamist

Skript nimetab failid ümber järgmisse formaati (TMDb ID failinimi ei sisalda):

```
Eesti tiitel (Inglise tiitel) (aasta).mkv
```

- Näide: `Ämblikmees (The Spectacular Spider-Man) (2008).mkv`

## Käivitamine

```
python3 start.py
```

1. Vali nimekiri: `1` filmid, `2` multikad
2. Sisesta kausta tee või vajuta Enter (kasutatakse vaikimisi kausta)
3. Vali toiming:
   - `1` — kontrolli hetke seisu (mis on olemas, mis puudu, mis valede nimedega)
   - `2` — nimeta failid ümber (näitab eelvaate, küsib kinnitust)
