# Eksāmenu grafika sastādīšana ar Simulated Annealing

**Uzdevums.** Doti eksāmeni, studenti ar saviem eksāmeniem un sesijas periodu skaits P. Katram eksāmenam jāpiešķir periods.

- **Hard:** nevienam studentam nav divu eksāmenu vienā periodā.
- **Soft:** studenta eksāmeni pēc iespējas tālāk viens no otra — par diviem eksāmeniem 1, 2, 3, 4, 5 periodu attālumā
  sods 16, 8, 4, 2, 1.
- **Mērķis:** minimizēt vidējo sodu uz studentu (Carter, Laporte, Lee 1996 — Toronto formulation).

## Algoritms

- **Domēns:** `period[e] ∈ {0, …, P−1}`; meklē tikai derīgajos grafikos. Sākums — Saturation Degree heuristic
  (+ konfliktu novēršana ar SA, ja vajag).
- **Novērtēšana:** `F = Σ s_ef · w(|period[e] − period[f]|) / S`; gājiena Δ rēķina tikai pārvietotajam eksāmenam.
- **Gājiens:** eksāmenu pārceļ uz periodu bez konfliktiem (98 %) vai pārceļ uz citu periodu kopā ar eksāmeniem, kuriem ar to ir kopīgi studenti (2 %).
- **Algoritms:** Simulated Annealing — gājienu ar `Δ > 0` pieņem ar varbūtību `exp(−Δ/T)`, `T ← α·T`.

Viss implementēts patstāvīgi ar Python standarta bibliotēku; gatavas optimizācijas bibliotēkas netiek izmantotas.

## Palaišana

Vajadzīgs Python 3.10+, ārējas pakotnes nav vajadzīgas.

```bash
python src/schedule.py                                       # gatavi piemēri: SA pret precīzo optimumu
python src/schedule.py --periods 4 Mat,Fiz Fiz,Prog Mat,Prog  # savi studenti: katrs arguments = viena studenta eksāmeni
python src/schedule.py data/hec92.stu                         # dati no faila (periodu skaits no src/instances.py)
python src/schedule.py data/yor83.stu --solution data/solutions/yor83.sol   # gatava grafika soda aprēķins
python src/run_tests.py                                       # visi testi (~20 min) → results/
python src/run_tests.py --only mazs_06,hec92 --runs 2
python src/test_inputs.py                                     # ievades un novērtēšanas testi
python src/generate.py                                        # no jauna ģenerē data/mazs_*.stu
```

## Faili

| Fails | Saturs |
|---|---|
| `src/timetable.py` | Datu nolasīšana, kopīgo studentu tabula, soda aprēķins, pārbaudes |
| `src/construct.py` | Sākuma grafiks (Saturation Degree) |
| `src/feasible.py` | Konfliktu novēršana ar SA, ja sākuma grafikā tie palikuši |
| `src/sa.py` | Simulated Annealing |
| `src/solver.py` | Viss kopā: sākuma grafiks → konfliktu novēršana → SA |
| `src/exact.py` | Precīzs optimums ar exhaustive search (tikai maziem datiem, pārbaudei) |
| `src/instances.py` | Testa dati: periodu skaits un labākais zināmais rezultāts |
| `src/generate.py` | Mazie ģenerētie testa dati |
| `src/run_tests.py` | Testi, rezultāti mapē `results/` |
| `src/schedule.py` | Grafika sastādīšana piemēriem, saviem datiem vai failam |
| `src/test_inputs.py` | Ievades un novērtēšanas testi |
| `data/*.stu` | Testa dati: viena rinda = viens students un viņa eksāmeni |
| `data/solutions/*.sol` | Literatūrā publicēti grafiki novērtēšanas pārbaudei |
| `results/` | Rezultāti (`results.csv`, `results.md`, `parametri.md`) |

Testa dati:
- `mazs_06`, `mazs_09`, `mazs_12` — ģenerēti (6–12 eksāmeni); optimumu aprēķina `src/exact.py`;
- 13 Toronto datu kopas (oriģinālā versija I, https://people.cs.nott.ac.uk/pszrq/data.htm) — 81–2419 eksāmeni;
  labākie zināmie rezultāti no S. Ceschia, L. Di Gaspero, A. Schaerf, arXiv:2201.07525 (2022), 9. tabula.
