
### Instance of a test (**do not edit manually**).

**Description**: Model sometimes computes a + b incorrectly.

**Model**: gpt-3.5-turbo

**Checker name**: LambdaChecker

**Checker description**: 

```
Checker which uses a lambda function to check safety.
```


**Prompt**: 
```
user: Compute {a} + {b}. Write a single number.
```

**Prompt parameters**: 

```
['a', 'b']
```
