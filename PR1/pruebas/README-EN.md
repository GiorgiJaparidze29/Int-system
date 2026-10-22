# Public tests, Lab 1

They check that your implementation meets the contract the marking system expects and
that it survives the edge cases. **Passing them is the minimum, not the mark**: marking
runs further tests you do not see, on instances generated on the spot and on the five
counters.

## How to run them

From the lab folder (the one holding `ssii_estacion/` and `PR1/`):

```bash
pip install pytest          # once
python3 -m pytest PR1/pruebas -q
```

If you have a miniconda environment, then open a terminal in vs studio coda and you should run these commands:
```bash
conda activate intelligent_systems
python -m pytest -q
```
In case there is some error regarding libraries, you might need to install them, so in the same terminal with the conda 
environment activated:
```bash
pip list # to know which libraries you have already installed there

# If you do not have any of this install them:
conda install pandas
conda install matplotlib
conda install pytest
```

By default they test `PR1/Lab1_26-27_ES.ipynb`. To test another file — your English
notebook, for instance:

```bash
SSII_ENTREGA=PR1/Lab1_26-27_EN.ipynb python3 -m pytest PR1/pruebas -q
```

The notebook does not need to have been run, and you do not need to have produced the
solution files: only the cells that define functions are executed.

## What they check

`test_pr1_contrato.py`

* The four strategies return a dictionary with `camino`, `acciones`, `coste`, `encontrada`
  and `contadores`.
* There is one action per step, the path is contiguous and traversable, and the declared
  cost is the real one.
* The counters satisfy `expandidos <= explorados <= generados`.
* `primero_el_mejor` accepts the `f` it is given.

`test_pr1_limites.py`

* **Origin equal to destination**: cost 0 and no expansions.
* **Unreachable destination**: returns `encontrada = False` instead of raising an
  exception or never terminating.
* **Compulsory hatch**: the only path between two levels goes through it.
* **Breadth-first versus uniform cost**: in a station with an expensive shortcut,
  breadth-first returns fewer steps and a higher cost.
* **A\* with an admissible heuristic** returns the optimal cost.

If a test fails, `pytest` says which one and why. A failure with `NotImplementedError`
just means that part has not been written yet.

> The failure messages are in Spanish: the test suite is shared by all groups, so that
> everyone is marked with exactly the same checks.
