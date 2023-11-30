## Privacy violations related to LLMs - including leakage or inference of personal information, membership inference, and compliance with privacy regulations

In this directory we record LVEs corresponding to the privacy of large language models. 
The following are some examples of the issues we are interested in:

- **Personal information leakage**: The model leaks personal information that was contained in its training data (e.g. names and addresses of people)

- **Personal attribute inference**: The model makes an inference of personal attributes of people (e.g. given a text written by a person, LLM infers their nationality or age)

- **Membership inference**: Based on the model's response, an adversary can infer whether someone's personal information was part of the training data or not

- **PII detection**: The model should recognize and not produce personally identifiable information (e.g. credit card numbers, social security numbers, etc.)

- **Compliance**: The model outputs should generally comply with privacy regulations (e.g. GDPR)




