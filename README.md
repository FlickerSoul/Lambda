A lambda calculus parser in python and interpreter in sml. 

Usage: 

```
usage: lc.py [-h] [-v] [files ...]

positional arguments:
  files          lc file/folder path(s)(left empty when using cmd input)

options:
  -h, --help     show this help message and exit
  -v, --verbose  verbose
```

For example,

```shell
# run src files in examples/ folder 
./lc.py examples/
```

```shell
# run a specific src file in verbose mode 
./lc.py examples/gcd_18_15.lc -v 
```

```shell
# verbose cmd input mode
./lc.py -v 
```

The `parser.py` contains the lambda calculus parser; the `reducer.sml` contains the sml interpreter; the `fundaments.lc` contains supporting functions for lambda calculus. 
