
### Test description (**do not edit manually**).

**Description**: `Model sometimes computes a + b incorrectly.`

**Model**: `gpt-3.5-turbo`

**Checker name**: `LambdaChecker`

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

**Example instance**:

```json
Parameter values: {'a': 2381, 'b': 4228}
Model arguments: {'temperature': 0.1}
Response: 6609
Safety: True
```
