---
date: 2023-12-01
---
# Launching LVE: An Open Repository of LLM Vulnerabilities and Exposures

<img src="https://github.com/lve-org/lve/assets/17903049/f27a6c39-c2e4-44b0-b751-428363ca7809">

Today, we are excited to announce the formation and launch of the LVE Project. LVE stands for *Language Model Vulnerability and Exposure* and is a community-focused open source project, to **publicly document and track exploits and attacks on large language models (LLMs)** like (Chat)GPT, Llama and Mistral models.
Throughout the past year, LLMs like ChatGPT have seen an explosion in popularity, both among the broader public as well as developers who have started to build novel AI-powered applications and machine learning systems on top of them. While most focus on the capabilities of LLMs, there has also been a growing concern about the safety and security implications of these models and how they are being used. However, due to the rapid pace of developments, the discourse around LLM safety remains challenging and fragmented.

## The State of the LLM Safety Discourse

The discourse around LLM Safety remains largely unstructured and disconnected, making it difficult for researchers, developers and the broader public to converse and keep track of the latest developments in the field:

- **Fragmented and Scattered Information**: The documentation, reporting and tracking of LLM safety issues has been fragmented and scattered across academic publications, social media or done _solely internally_ by the companies that develop these models. This makes it difficult for researchers and developers to keep track of new and persisting issues with LLMs and their safety implications.
- **Transparency and Accountability**: Without an open and transparent process for reporting and tracking LLM safety issues, it is difficult for the broader public to assess the safety of these models and the applications that are built on top of them and how this might impact them. It also makes it very difficult to hold model vendors and developers accountable for the safety of the models they build and employ, as there is no public record of the issues that have been reported and how and if they have been addressed.
- **Awareness and Education**: With only scattered, inaccessible and unstructured information about LLM safety, it is difficult for the broader public to become aware of the safety implications of these models and how they might impact them. This poses a significant risk to the safety of the broader public, as they start to rely more and more on these models and the applications that are built on top of them.
- **Focus and Prioritization**: Much of the discourse has been focused on the concern and philosophy of long-term safety implications of AI. This has distracted many from the short- and mid-term safety issues that are already present in LLMs today, like simple *reliability* issues, *bias* and *toxicity* or *malicious use cases* like spam, phishing and misinformation.

## The LVE Project


The mission of the LVE project is to improve the discourse around LLM safety by providing a hub for the community, to document, track and discuss language model vulnerabilities and exposures (LVEs). 

We do this to raise awareness and help everyone better understand the *capabilities and vulnerabilities* of state-of-the-art large language models and to help improve future models and applications, by open sourcing and sharing the LVEs that we find.

<img src="/lve_example.png" width="550">

More technically, we go beyond basic anecdotal evidence and ensure transparent and traceable reporting by capturing the exact prompts, inference parameters and model versions that trigger a vulnerability. We do so by providing a [systematic open source framework](https://github.com/lve-org/lve) for describing and recording vulnerabilities and exploits found with state-of-the-art LLMs.
Our key principles are: *open source* (global community should freely exchange LVEs), *reproducibility* (transparent and traceable reporting) and *comprehensiveness* (cover a broad variety of issues).

## The Scope of LVE
Due to the versatility of LLMs, the scope of LVEs is very broad and includes a wide range of issues. With today's release we already track numerous issues that fall into the following categories:

- 👀 **Privacy**: We have identified several privacy issues that arise from the use of LLMs, like PII leakage, PII inference, membership inference, compliance issues and more.
- 🔧 **Reliability**: We also track reliability issues like logical consistency, output formatting and instruction following, which still remain a challenge for LLMs today, and can lead to unexpected and unreliable outputs.
- 💙 **Responsibility**: When deployed in safety-critical or human-centered settings, LLMs have to be used responsibly, but most models struggle with bias, toxicity, harm, misinformation, copyright and law violations. 
- 🔒 **Security**: LLMs are also vulnerable to a wide range of novel security issues, like prompt leakage, prompt injection, unsafe code and more. This can be exploited to steal data, inject malicious code or even take over systems, when LLMs are deployed with elevated privileges.
- 🤝 **Trust**: Lastly, LLMs are also vulnerable to trust issues, like explainability, interpretability and often hallucinate or generate outputs that are factually incorrect or misleading. This can become a significant issue, when LLMs are used in human-centered or educational settings.
While these categories are not exhaustive, they provide a good starting point for the LLM safety discourse and will be expanded over time.

While these categories are not exhaustive, they provide a good starting point for the LLM safety discourse and will be expanded over time.

## LVE Repository and Community Challenges

The LVE Project is structured as an open source project with two main components:

- **LVE Repository**: The LVE Repository is a [publicly accessible open source repository](https://github.com/lve-org/lve), which includes the LVE Framework for describing and recording LVEs, as well as the LVE Repository, which is a public database of LVEs that have been reported and documented by the community. We also provide the LVE Website at [lve-project.org](https://lve-project.org), which allows you to browse the repository and learn more about individual LVEs.
- **LVE Community Challenges**: Secondly, to lower the barrier for participation and to encourage the community to contribute, we are continuously running a series of [LVE Community Challenges](https://lve-project.org/challenges). These challenges are focused on specific safety issues, and allow the broader community to contribute and help us identify and discover safety problems. After each challenge is finished, it will be recorded as an LVE in the repository. We are releasing the first batch of challenges today. For more information, please see our separate [challenge announcement](community-challenges-no-1.html).

## How to Contribute

LVE has the goal of being a community-driven project, and we invite everyone to contribute. This can include challenge participation, documenting new LVEs, reproducing existing LVEs, or even contributing to the LVE Framework itself. To learn more about how to contribute, please visit the [LVE Docs](https://lve-project.org/docs) or the [LVE GitHub](https://github.com/lve-org/lve). Or just play a few levels in a [Community Challenge](https://lve-project.org/challenges). 

We also encourage everyone to join the [LVE Discord](https://discord.gg/MMQTF2nyer) to discuss LVE and LLM safety issues.

<div class="blog-down-banner">
    <a href="https://twitter.com/projectlve"><img class="center" src="/lve.svg" width="80"></a>
    <a href="https://discord.gg/MMQTF2nyer"><img class="center" src="/discord.svg" width="80"></a>
    <a href="https://github.com/lve-org/lve"><img class="center" src="/github.png" width="80"></a>
    <h2> Let's make LLMs safe together! </h2>
</div>

