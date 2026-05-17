# start.py — filmide ümbernimetamise tööriist

Skript võrdleb videofaile nimekirjaga ja nimetab need vajadusel ümber õigesse formaati.

## Nõuded

- Python 3.8 või uuem
- Muid pakette pole vaja

## Soovituslik kaustade struktuur

```
Media/
├── Eesti Filmid/
│   ├── Mingi Film (2020) [Some Movie].mkv
│   └── ...
├── Eesti Multikad/
│   ├── Ämblikmees (2008) [The Spectacular Spider-Man].mkv
│   └── ...
└── Scripts/
    ├── start.py
    ├── filmid.txt
    └── multikad.txt
```

## Nimekirjafailide formaat

`filmid.txt` ja `multikad.txt` — iga film omareal:

```
Eesti tiitel (aasta) [Inglise tiitel] {tmdb-ID}
```

- `{tmdb-ID}` on valikuline TMDb ID — kui puudub, jäetakse välja
- Näide (TMDb-ga): `Ämblikmees (2008) [The Spectacular Spider-Man] {tmdb-7446}`
- Näide (ilma TMDb-ta): `Kormoranid ehk Nahkpükse ei pesta (2011) [Farts of Fury]`
- Formaati txt-failis eraldi ei täpsustata — skript eeldab alati ülaltoodud struktuuri

## Failinime formaat pärast ümbernimetamist

Skript nimetab failid ümber järgmisse formaati (TMDb ID failinimi ei sisalda):

```
Eesti tiitel (aasta) [Inglise tiitel].mkv
```

- Näide: `Ämblikmees (2008) [The Spectacular Spider-Man].mkv`

## Käivitamine

```
python3 start.py
```

1. Vali nimekiri: `1` filmid, `2` multikad
2. Sisesta kausta tee või vajuta Enter (kasutatakse vaikimisi kausta)
3. Vali toiming:
   - `1` — kontrolli hetke seisu (mis on olemas, mis puudu, mis valede nimedega)
   - `2` — nimeta failid ümber (näitab eelvaate, küsib kinnitust)
