\# Issues found in scheduler\_system.py



Baseline (original file): Pylint 5.60/10 · Bandit 1 High + 1 Low · Flake8 13 findings

After fixes: Pylint 10.00/10 · Bandit 0 issues · Flake8 0 issues



Line numbers refer to the ORIGINAL file.



\## Found by the tools



| Issue | Type | Line(s) | Description | Fix Approach |

| ----- | ---- | ------- | ----------- | ------------ |

| Shell command injection (Bandit B605, \*\*High\*\*) | Security | 43 | `os.system("cat " + file)` builds a shell command from a string. A file name such as `x; rm -rf \~` would run arbitrary commands. | Removed the shell call. Re-open the log with `open()` and print its contents. |

| Mutable default argument (Pylint W0102) | Bug | 11 | `equipment\_list=\[]` is created once and shared by every call. The same list object is also stored inside each reservation. | Default is `None`; a fresh `list(...)` copy is made per call. |

| Bare `except: pass` (Pylint W0702, Flake8 E722, Bandit B110) | Bug / Security | 27-28 | Swallows every error, so `cancel\_reservation(77)` fails silently. It also hides real bugs and even Ctrl+C. | Use `dict.pop(id, None)`, return True/False, and log a warning when the id does not exist. |

| Files opened without `with` (Pylint R1732) | Resource leak | 35, 40 | `logConflicts` never closes its file at all; `export\_schedule` leaks it if `write` raises. | `with open(...)` context managers. |

| No encoding on `open()` (Pylint W1514) | Portability | 35, 40 | Uses the platform default encoding, so behaviour differs between machines. | `encoding="utf-8"`. |

| Global state and `global` statement (Pylint W0603, C0103) | Design | 5-9, 12 | Module-level mutable globals make the code hard to test and reset. | Moved everything into a `RoomScheduler` class. |

| Function name `logConflicts` (Pylint C0103) | Style | 39 | camelCase breaks snake\_case convention. | Renamed `log\_conflicts`. |

| Unused variables `a`, `a\_more`, `c` (Pylint W0612, Flake8 F841) | Dead code | 46, 47, 49 | Return values assigned and never used. | Dropped the assignments. |

| Old `%` string formatting (Pylint C0209) | Style | 15 | Harder to read than f-strings. | f-strings. |

| Iterating dict keys then indexing (Pylint C0206) | Style | 13-14 | Looks up `reservations\[r]` repeatedly. | Iterate `.values()`. |

| Missing docstrings (Pylint C0114, C0116) | Docs | 1, 11, 22, 30, 34, 39, 45 | No module or function documentation. | Added docstrings. |

| Line too long (Pylint C0301, Flake8 E501) | Style | 14, 18 | Over 79 characters. | Wrapped and shortened. |

| Missing blank lines (Flake8 E302, E305) | Style | 11, 22, 30, 34, 39, 45, 59 | PEP 8 wants two blank lines around top-level defs. | Reformatted. |



\## NOT flagged by any tool (found by running the program)



| Issue | Type | Line(s) | Description | Fix Approach |

| ----- | ---- | ------- | ----------- | ------------ |

| `os.system("cat ...")` not portable | Portability bug | 43 | On Windows the program prints `'cat' is not recognized as an internal or external command`, so the conflict log is never shown. | Read and print the file with Python's `open()`; works on every OS and removes the shell call. |

| Reversed slot accepted | Logic bug | 48 | `"14-12"` is booked and `slot\_hours` returns \*\*-2\*\*. | `parse\_slot()` requires `start < end` within 00-24, otherwise raises `ValueError`. |

| Wrong slot type accepted | Logic bug | 49 | `1530` (an int) is stored as a slot; `slot\_hours(1530)` would crash on `.split`. | `parse\_slot()` rejects non-strings and anything not matching `HH-HH`. |

| Equipment can go negative | Logic bug | 16-17 | A second webcam booking leaves `webcam: -1`; nothing checks availability. | Check availability for the whole request first, then decrement (all-or-nothing). |

| Unknown equipment crashes mid-booking | Logic bug | 16-17 | `KeyError` after earlier items were already decremented, leaving the pool corrupted. | Validate every item up front, so a failed booking changes nothing. |

| Double booking is still booked | Logic bug | 13-18 | The conflict is logged but the reservation is created anyway, consuming equipment. | A conflict now refuses the booking (returns `None`) after logging it. |

| Conflicts re-logged on every call | Logic bug | 41-42 | `conflicts` is never cleared, so each `logConflicts` call appends the same entries again. | Clear the list after writing. |

| Unvalidated user input | Input validation | 52 | The `input()` slot goes straight into `schedule\_room`. | Validated by `parse\_slot()`; `main` catches `ValueError` and reports it. |

| `main()` runs on import | Design | 59 | Importing the module runs the whole demo and prompts for input. | `if \_\_name\_\_ == "\_\_main\_\_":` guard. |

| No logging configured | Quality | n/a | Errors had nowhere to go. | `logging.basicConfig` in `main()`; `logger.warning/error` for failures. |

