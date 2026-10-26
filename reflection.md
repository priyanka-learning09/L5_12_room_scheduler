\# Reflection



\## 1. Which issues were easiest to fix, and which were hardest?

Style problems (blank lines, line length, naming, f-strings, docstrings) were quick and mostly mechanical. The hardest were the ones that needed a design decision: removing the global state meant moving everything into a class, and deciding what a double booking should do (log only, or refuse) was a behaviour choice that no tool could make for me.



\## 2. Did the tools report any false positives, or miss real problems?

Nothing was a clear false positive, but some findings were low value for this file (the missing-docstring warnings, and Bandit's Low B110, which duplicates Pylint's bare-except warning). More important, the tools missed the real logic bugs: the slot 14-12 giving a length of -2, 1530 being stored as an int, equipment counts going negative, and a double booking still consuming equipment. Those only showed up by running the program and reading its output.



\## 3. How would you integrate static analysis into a real workflow?

Run Flake8 and Pylint in a pre-commit hook so style issues never reach review, and run all three tools in CI (for example GitHub Actions) with the build failing on any Bandit High/Medium finding and on Pylint dropping below an agreed score. Bandit matters most for anything handling user input or files. Tune the rules in a config file rather than silencing warnings inline.



\## 4. What did you learn about code quality and security?

Security bugs are often one line: os.system("cat " + file) was the only High-severity finding and is a real command-injection risk. It also failed on my Windows machine because cat does not exist there. Swallowing exceptions with except: pass hides failures rather than preventing them. Static analysis is a good first filter, but a 10/10 Pylint score does not mean the code is correct; it needs to be paired with testing and with actually running the program.

