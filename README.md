# mutate

DSL for genetic algorithms.

```
cost function definition: f: (x1, x2, ..., xn) -> <expr> [<xn-range>]*

f: (x, y) -> -x * (y / 2 - 10) [10, 20] [-5, 7]
```

```
generate population for cost function: p: <n-pop> [<xn-range>]* <bits>

p: 100 [10, 20] [-5, 7] 4
```

