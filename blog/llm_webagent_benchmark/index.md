# Introduction

LLM-powered web agents take natural language instructions from humans, along with information about the current webpage (such as HTML, a DOM tree, a screenshot, and an accessibility tree), and LLMs generate browser operations as output (primarily the target element, the type of operation, and specified values).
Note that in the following parts, natural language instructions are also referred to as tasks, information about the current webpage as observations, and browser operations as actions.

To generate correct actions, it is essential to accurately interpret the webpage GUI's visual information and layout.
This article categorizes and introduces benchmarks that specifically evaluate the ability of web agents to understand and manipulate webpage GUIs.

# 1. Simulated Web Environment

This category of benchmarks hosts simulated websites that mimic real-world sites to evaluate how effectively agents can navigate them. Agents interact with these simulated websites by controlling a web browser via libraries such as Playwright.
These benchmarks provide agents with exploration opportunities while eliminating concerns about spam-like negative impacts on real-world services.
To enhance realism, some studies utilize open-source software such as GitLab and scrape real product information from Amazon to construct simulated websites.

## WoB (particularly MiniWoB)

- Date: Aug. 2017
- Paper: <a href="https://dl.acm.org/doi/10.5555/3305890.3306005">World of Bits: An Open-Domain Platform for Web-Based Agents</a>
- Description: MiniWoB is a fundamental web GUI task, where a reward is given for performing the correct action. FormWoB records HTTP communications of human interactions on actual airline websites via a proxy and aims for the agent to replay the correct HTTP request for a given task. QAWoB is a dataset where the correct DOM elements are annotated as answers for web pages and their corresponding questions.

## MiniWoB++

- Date: Feb. 2018
- Paper: <a href="https://arxiv.org/abs/1802.08802">Reinforcement Learning on Web Interfaces Using Workflow-Guided Exploration</a>
- Repository: <a href="https://github.com/Farama-Foundation/miniwob-plusplus">Farama-Foundation/miniwob-plusplus</a>
- Description: An extended version of MiniWoB incorporating stochastic characteristics and additional tasks.

## WebShop

- Date: Jul. 2022
- Paper: <a href="https://arxiv.org/abs/2207.01206">WebShop: Towards Scalable Real-World Web Interaction with Grounded Language Agents</a>
- Repository: <a href="https://github.com/princeton-nlp/WebShop">princeton-nlp/WebShop</a>
- Description: In a simulated online shopping site built using product information scraped from Amazon, the agent repeatedly performs high-level (abstract) actions to evaluate whether it can purchase a product close to the given task.

## WebArena

- Date: Jul. 2023
- Paper: <a href="https://arxiv.org/abs/2307.13854">WebArena: A Realistic Web Environment for Building Autonomous Agents</a>
- Repository: <a href="https://github.com/web-arena-x/webarena">web-arena-x/webarena</a>
- Description: A simulated website, built with real OSS web services such as Reddit and GitLab, requires a sequence of low-level actions to complete high-level tasks.

## CompWoB

- Date: Nov. 2023
- Paper: <a href="https://arxiv.org/abs/2311.18751">Exposing Limitations of Language Model Agents in Sequential-Task Compositions on the Web</a>
- Repository: <a href="https://github.com/google-research/google-research/tree/master/compositional_rl/compwob">compositional_rl/compwob</a>
- Description: A benchmark composed of tasks that combine multiple MiniWoB tasks.

## WebVLN

- Date: Dec. 2023
- Paper: <a href="https://arxiv.org/abs/2312.15820">WebVLN: Vision-and-Language Navigation on Websites</a>
- Repository: <a href="https://github.com/WebVLN/WebVLN">WebVLN/WebVLN</a>
- Description: A benchmark in which an agent navigates through an experimental shopping site by repeatedly selecting one of the available buttons and answering questions.

## VisualWebArena

- Date: Jan. 2024
- Paper: <a href="https://arxiv.org/abs/2401.13649">VisualWebArena: Evaluating Multimodal Agents on Realistic Visual Web Tasks</a>
- Repository: <a href="https://github.com/web-arena-x/visualwebarena">web-arena-x/visualwebarena</a>
- Description: A benchmark that inherits some tasks from WebArena while adding tasks where visual information is crucial (e.g., Buy the least expensive red blanket).

## WorkArena

- Date: Mar. 2024
- Paper: <a href="https://arxiv.org/abs/2403.07718">WorkArena: How Capable Are Web Agents at Solving Common Knowledge Work Tasks?</a>
- Repository: <a href="https://github.com/ServiceNow/WorkArena">ServiceNow/WorkArena</a>
- Description: A benchmark for performing business-oriented tasks on enterprise cloud services (ServiceNow).

## TurkingBench

- Date: Mar. 2024
- Paper: <a href="https://arxiv.org/abs/2403.11905">Tur[k]ingBench: A Challenge Benchmark for Web Agents</a>
- Repository: <a href="https://github.com/JHU-CLSP/turking-bench">JHU-CLSP/turking-bench</a>
- Description: A benchmark that requires low-level actions mimicking crowdsourcing on Amazon Mechanical Turk (AMT).

## WorkArena++

- Date: Jul. 2024
- Paper: <a href="https://arxiv.org/abs/2407.05291">WorkArena++: Towards Compositional Planning and Reasoning-based Common Knowledge Work Tasks</a>
- Repository: <a href="https://github.com/ServiceNow/WorkArena">ServiceNow/WorkArena</a>
- Description: A more complex version of WorkArena.

## ST-WebAgentBench

- Date: Oct. 2024
- Paper: <a href="https://arxiv.org/abs/2410.06703">ST-WebAgentBench: A Benchmark for Evaluating Safety and Trustworthiness in Web Agents</a>
- Repository: <a href="https://github.com/segev-shlomov/ST-WebAgentBench">segev-shlomov/ST-WebAgentBench</a>
- Description: A benchmark based on WebArena that allows for evaluating safety and trustworthiness.

## VideoWebArena

- Date: Oct. 2024
- Paper: <a href="https://arxiv.org/abs/2410.19100">VideoWebArena: Evaluating Long Context Multimodal Agents with Video Understanding Web Tasks</a>
- Repository: <a href="https://github.com/ljang0/videowebarena">ljang0/videowebarena</a>
- Description: A benchmark that requires selecting appropriate low-level actions for tasks in WebArena and VisualWebArena by referencing tutorial videos created from these tasks.

## TheAgentCompany

- Date: Dec. 2024
- Paper: <a href="https://arxiv.org/abs/2412.14161">TheAgentCompany: Benchmarking LLM Agents on Consequential Real World Tasks</a>
- Repository: <a href="https://github.com/TheAgentCompany/TheAgentCompany">TheAgentCompany/TheAgentCompany</a>
- Description: A diverse set of application operation tasks simulating software development workflows that involve browser interactions, with a closed environment hosted using OSS such as GitLab and RocketChat.

## WebGames

- Date: Feb. 2025
- Paper: <a href="https://arxiv.org/abs/2502.18356">WebGames: Challenging General-Purpose Web-Browsing AI Agents</a>
- Repository: <a href="https://github.com/convergence-ai/webgames">convergence-ai/webgames</a>
- Description: A benchmark aggregating basic browser interaction tasks, similar to MiniWoB++.

# 2. Open-Ended Task

Benchmarks in this category require connecting to the internet and navigating real webpages to complete tasks.
Similar to a simulated environment, there is an opportunity for exploration; however, real websites constantly change and sometimes disappear, causing the task's difficulty to vary over time.
Hence, QA-format tasks are prominent as they allow for abstract success evaluation.
The focus is often on evaluating appropriate page transition capabilities for information retrieval.
By limiting the benchmarks to those with a specified starting URL, the chances of comparing GUI understanding and manipulation abilities for the same webpages increase.

## WebNav

- Date: Oct. 2020
- Paper: <a href="https://arxiv.org/abs/2010.12844">FLIN: A Flexible Natural Language Interface for Web Navigation</a>
- Repository: <a href="https://github.com/microsoft/flin-nl2web">microsoft/flin-nl2web</a>
- Description: A benchmark that accesses specified well-known web services, outputs high-level actions for tasks, and compares them with the correct answers.

## WebVoyager

- Date: Jan. 2024
- Paper: <a href="https://arxiv.org/abs/2401.13919">WebVoyager: Building an End-to-End Web Agent with Large Multimodal Models</a>
- Repository: <a href="https://github.com/MinorJerry/WebVoyager">MinorJerry/WebVoyager</a>
- Description: A dataset of tasks that can be solved by navigating real-world websites from specified URLs, where the correctness of answers is abstract and thus judged by humans or LLMs.

## OSWorld

- Date: Apr. 2024
- Paper: <a href="https://arxiv.org/abs/2404.07972">OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments</a>
- Repository: <a href="https://github.com/xlang-ai/OSWorld/tree/main/evaluation_examples/examples/chrome">xlang-ai/OSWorld</a>
- Description: A benchmark that requires diverse desktop application operations, including web page visits through browser interactions.

## MMInA

- Date: Apr. 2024
- Paper: <a href="https://arxiv.org/abs/2404.09992">MMInA: Benchmarking Multihop Multimodal Internet Agents</a>
- Repository: <a href="https://github.com/shulin16/mmina">shulin16/mmina</a>
- Description: A benchmark that involves visiting real-world websites to solve tasks, enabling success rate evaluation at each page transition (hop).

## WebCanvas (Mind2Web-Live)

- Date: Jun. 2024
- Paper: <a href="https://arxiv.org/abs/2406.12373">WebCanvas: Benchmarking Web Agents in Online Environments</a>
- Repository: <a href="https://github.com/iMeanAI/WebCanvas">iMeanAI/WebCanvas</a>
- Description: A benchmark for assessing whether an agent can successfully reach the correct state for a given task.

## WebWalkerQA

- Date: Jan. 2025
- Paper: <a href="https://arxiv.org/abs/2501.07572">WebWalker: Benchmarking LLMs in Web Traversal</a>
- Repository: <a href="https://huggingface.co/datasets/callanwu/WebWalkerQA">callanwu/WebWalkerQA</a>
- Description: A benchmark where a query, its correct answer, and golden trajectories are given, and the task is to traverse a website from a specified starting URL to find the answer.

# 3. Static Dataset

This category consists of datasets that store either HTML, DOM trees, or screenshots as observations of webpages, ensuring that the correct elements for the tasks are provided.
These datasets can be broadly classified into annotation results for a single page or trajectory datasets spanning multiple actions and pages.
In many cases, the correct answers are provided through human annotation or demonstrations, but some studies have explored generating trajectories automatically using LLMs.

## phrasenode

- Date: Aug. 2018
- Paper: <a href="https://arxiv.org/abs/1808.09132">Mapping Natural Language Commands to Web Elements</a>
- Repository: <a href="https://github.com/stanfordnlp/phrasenode">stanfordnlp/phrasenode</a>
- Description: A dataset of tasks for webpages and their corresponding correct elements, with only the HTML retained as observations.

## WebSRC

- Date: Jan. 2021
- Paper: <a href="https://arxiv.org/abs/2101.09465">WebSRC: A Dataset for Web-Based Structural Reading Comprehension</a>
- Repository: <a href="https://x-lance.github.io/WebSRC/">x-lance/WebSRC</a>
- Description: A QA dataset for assessing structural understanding of webpages by extracting answers and their corresponding tags in response to questions.

## RUSS

- Date: Mar. 2021
- Paper: <a href="https://arxiv.org/abs/2103.16057">Grounding Open-Domain Instructions to Automate Web Support Tasks</a>
- Repository: <a href="https://github.com/xnancy/russ">xnancy/russ</a>
- Description: A dataset of DOM trees recorded on real websites, along with action histories corresponding to tasks.

## Klarna Product Page Dataset

- Date: Nov. 2021
- Paper: <a href="https://arxiv.org/abs/2111.02168">The Klarna Product Page Dataset: Web Element Nomination with Graph Neural Networks and Large Language Models</a>
- Repository: <a href="https://github.com/klarna/product-page-dataset">klarna/product-page-dataset</a>
- Description: A dataset of webpages and annotation results for their key elements, providing screenshots and MHTML files.

## Mind2Web

- Date: Jun. 2023
- Paper: <a href="https://arxiv.org/abs/2306.06070">Mind2Web: Towards a Generalist Agent for the Web</a>
- Repository: <a href="https://github.com/OSU-NLP-Group/Mind2Web">OSU-NLP-Group/Mind2Web</a>
- Description: A dataset containing snapshots such as MHTML from real websites, natural language tasks, and recorded human demonstrations.

## AITW (Android in the Wild)

- Date: Jul. 2023
- Paper: <a href="https://arxiv.org/abs/2307.10088">Android in the Wild: A Large-Scale Dataset for Android Device Control</a>
- Repository: <a href="https://github.com/google-research/google-research/tree/master/android_in_the_wild">google-research/android_in_the_wild</a>
- Description: Diverse app interaction tasks, including browser operations, with Android screenshots as observations.

## Multimodal Mind2Web

- Date: Jan. 2024
- Paper: <a href="https://arxiv.org/abs/2401.01614">GPT-4V(ision) is a Generalist Web Agent, if Grounded</a>
- Repository: <a href="https://huggingface.co/datasets/osunlp/Multimodal-Mind2Web">osunlp/Multimodal-Mind2Web</a>
- Description: A dataset with added screenshots using the raw dump of MIND2WEB.

## ScreenSpot

- Date: Jan. 2024
- Paper: <a href="https://arxiv.org/abs/2401.10935">SeeClick: Harnessing GUI Grounding for Advanced Visual GUI Agents</a>
- Repository: <a href="https://huggingface.co/datasets/rootsautomation/ScreenSpot">rootsautomation/ScreenSpot</a>
- Description: A dataset containing screenshots, tasks, and annotated correct elements across various GUI environments, including web browsers.

## ScreenAI

- Date: Feb. 2024
- Paper: <a href="https://arxiv.org/abs/2402.04615">ScreenAI: A Vision-Language Model for UI and Infographics Understanding</a>
- Repository: <a href="https://github.com/google-research-datasets/screen_annotation">google-research-datasets/screen_annotation</a>
- Description: An annotated dataset containing navigation tasks for UIs, including webpages.

## WEBLINX

- Date: Feb. 2024
- Paper: <a href="https://arxiv.org/abs/2402.05930">WebLINX: Real-World Website Navigation with Multi-Turn Dialogue</a>
- Repository: <a href="https://github.com/McGill-NLP/weblinx">McGill-NLP/weblinx</a>
- Description: A dataset that records demonstrations of high-level task execution on real websites, including user-agent interaction history throughout the process.

## ScreenAgent Dataset

- Date: Feb. 2024
- Paper: <a href="https://arxiv.org/abs/2402.07945">ScreenAgent: A Vision Language Model-driven Computer Control Agent</a>
- Repository: <a href="https://github.com/niuzaisheng/ScreenAgent">niuzaisheng/ScreenAgent</a>
- Description: A dataset of screenshots and low-level ground-truth actions targeting a diverse range of desktop applications, including browsers.

## OmniACT

- Date: Feb. 2024
- Paper: <a href="https://arxiv.org/abs/2402.17553">OmniACT: A Dataset and Benchmark for Enabling Multimodal Generalist Autonomous Agents for Desktop and Web</a>
- Repository: <a href="https://huggingface.co/datasets/Writer/omniact">Writer/omniact</a>
- Description: A dataset providing tasks across diverse desktop environments, including web browsers, along with PyAutoGUI scripts created based on human annotations.

## AITZ (Android in the Zoo)

- Date: Mar. 2024
- Paper: <a href="https://arxiv.org/abs/2403.02713">Android in the Zoo: Chain-of-Action-Thought for GUI Agents</a>
- Repository: <a href="https://github.com/IMNearth/CoAT">IMNearth/CoAT</a>
- Description: Diverse app interaction tasks, including browser operations, with Android screenshots as observations.

## VisualWebBench

- Date: Apr. 2024
- Paper: <a href="https://arxiv.org/abs/2404.05955">VisualWebBench: How Far Have Multimodal LLMs Evolved in Web Page Understanding and Grounding?</a>
- Repository: <a href="https://github.com/VisualWebBench/VisualWebBench">VisualWebBench/VisualWebBench</a>
- Description: A QA-based task on webpage screenshots requiring element selection.

## GUICourse

- Date: Jun. 2024
- Paper: <a href="https://arxiv.org/abs/2406.11317">GUICourse: From General Vision Language Models to Versatile GUI Agents</a>
- Repository: <a href="https://github.com/RUCBM/GUICourse">RUCBM/GUICourse</a>
- Description: A dataset with diverse annotations applied to webpage screenshots, requiring GUI understanding to solve.

## WONDERBREAD

- Date: Jun. 2024
- Paper: <a href="https://arxiv.org/abs/2406.13264">WONDERBREAD: A Benchmark for Evaluating Multimodal Foundation Models on Business Process Management Tasks</a>
- Repository: <a href="https://github.com/HazyResearch/wonderbread">HazyResearch/wonderbread</a>
- Description: Derived from WebArena, the dataset includes new features such as high-level tasks like BPM (Business Process Management) and records human demonstrations.

## AgentTrek

- Date: Dec. 2024
- Paper: <a href="https://arxiv.org/abs/2412.09605">AgentTrek: Agent Trajectory Synthesis via Guiding Replay with Web Tutorials</a>
- Repository: <a href="https://github.com/xlang-ai/AgentTrek">xlang-ai/AgentTrek</a>
- Description: A dataset created at low cost by collecting web tutorials (tasks and the operational steps to complete them), having an agent imitate the tutorials, and recording the results as trajectories.

## Explorer

- Date: Feb. 2025
- Paper: <a href="https://arxiv.org/abs/2502.11357">Explorer: Scaling Exploration-driven Web Trajectory Synthesis for Multimodal Web Agents</a>
- Description: A dataset containing large-scale trajectories generated by having an LLM perform task generation, task execution, and task success evaluation.

# 4. Wrapper

This category includes a wrapper that enables multiple benchmarks to be evaluated within the same interface.

## AgentBench

- Date: Aug. 2023
- Paper: <a href="https://arxiv.org/abs/2308.03688">AgentBench: Evaluating LLMs as Agents</a>
- Repository: <a href="https://github.com/THUDM/AgentBench">THUDM/AgentBench</a>
- Description: Including WebShop and Mind2Web.

## BrowserGym

- Date: Mar. 2024
- Paper: <a href="https://arxiv.org/abs/2403.07718">WorkArena: How Capable Are Web Agents at Solving Common Knowledge Work Tasks?</a>
- Repository: <a href="https://github.com/ServiceNow/BrowserGym">ServiceNow/BrowserGym</a>
- Description: Including MiniWob++, WebArena, VisualWebArena, WorkArena, and WebLINX.

## VisualAgentBench

- Date: Aug. 2024
- Paper: <a href="https://arxiv.org/abs/2408.06327">VisualAgentBench: Towards Large Multimodal Models as Visual Foundation Agents</a>
- Repository: <a href="https://github.com/THUDM/VisualAgentBench">THUDM/VisualAgentBench</a>
- Description: Including WebArena and VisualWebArena.
