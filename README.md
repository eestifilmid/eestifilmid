# Eesti filmid ja multikad

🎬 **[Sirvi filmide ja multikate nimekirja](https://eestifilmid.github.io/eestifilmid/)**

Veebileht loeb nimekirjad otse `filmid.txt` ja `multikad.txt` failidest, näitab postreid kaustast `web/assets/posters/` (failinimi = TMDb ID) ja lingib iga filmi TMDb lehele.

```
├── index.html          — avaleht
├── filmid.txt          — filmide nimekiri
├── multikad.txt        — multikate nimekiri
├── start.py            — ümbernimetamise tööriist
└── web/
    ├── filmid.html     — filmide galerii
    ├── multikad.html   — multikate galerii
    └── assets/
        └── posters/
            ├── filmid/<tmdb-ID>.jpg
            └── multikad/<tmdb-ID>.jpg
```

---

## start.py — filmide ümbernimetamise tööriist

Skript võrdleb videofaile nimekirjaga ja nimetab need vajadusel ümber õigesse formaati.

### Nõuded

- Python 3.8 või uuem
- Muid pakette pole vaja

### Soovituslik kaustade struktuur

```
Media/
├── Eesti Filmid/
│   ├── Mingi Film (2020) [Some Movie] {tmdb-12345}.mkv
│   └── ...
├── Eesti Multikad/
│   ├── Ämblikmees (2008) [The Spectacular Spider-Man] {tmdb-7446}.mkv
│   └── ...
└── Scripts/
    ├── start.py
    ├── filmid.txt
    └── multikad.txt
```

### Formaat

Nimekirjafailides (`filmid.txt`, `multikad.txt`) ja failinimedes kasutatakse sama formaati:

```
Eesti tiitel (aasta) [Inglise tiitel] {tmdb-ID}
```

- `{tmdb-ID}` on valikuline TMDb ID — kui see nimekirjas puudub, jäetakse see ka failinimest välja
- Näide (TMDb-ga): `Ämblikmees (2008) [The Spectacular Spider-Man] {tmdb-7446}`
- Näide (ilma TMDb-ta): `Kormoranid ehk Nahkpükse ei pesta (2011) [Farts of Fury]`
- Formaati txt-failis eraldi ei täpsustata — skript eeldab alati ülaltoodud struktuuri

### Failinime formaat pärast ümbernimetamist

Skript nimetab failid ümber täpselt nimekirjarea järgi, koos TMDb ID-ga:

```
Eesti tiitel (aasta) [Inglise tiitel] {tmdb-ID}.mkv
```

- Näide: `Ämblikmees (2008) [The Spectacular Spider-Man] {tmdb-7446}.mkv`

### Käivitamine

```
python3 start.py
```

1. Vali nimekiri: `1` filmid, `2` multikad
2. Sisesta kausta tee või vajuta Enter (kasutatakse vaikimisi kausta)
3. Vali toiming:
   - `1` — kontrolli hetke seisu (mis on olemas, mis puudu, mis valede nimedega)
   - `2` — nimeta failid ümber (näitab eelvaate, küsib kinnitust)

Mõlemad toimingud pakuvad lõpus võimaluse lisada nimekirjast puuduvad failid nimekirja.
