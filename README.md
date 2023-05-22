# 🤖 Chrome-GPT: An experimental AutoGPT agent that interacts with Chrome
 
[![lint](https://github.com/richardyc/chrome-gpt/actions/workflows/lint.yml/badge.svg)](https://github.com/richardyc/chrome-gpt/actions/workflows/lint.yml) [![test](https://github.com/richardyc/chrome-gpt/actions/workflows/tests.yml/badge.svg)](https://github.com/richardyc/chrome-gpt/actions/workflows/tests.yml) [![Twitter](https://img.shields.io/twitter/url/https/twitter.com/RealRichomie.svg?style=social&label=Follow%20%40RealRichomie)](https://twitter.com/RealRichomie)

⚠️This is an experimental AutoGPT agent that might take incorrect actions and could lead to serious consequences. Please use it at your own discretion⚠️

Chrome-GPT is an AutoGPT experiment that utilizes [Langchain](https://github.com/hwchase17/langchain) and [Selenium](https://github.com/SeleniumHQ/selenium) to enable an AutoGPT agent take control of an entire Chrome session. With the ability to interactively scroll, click, and input text on web pages, the AutoGPT agent can navigate and manipulate web content.

<h2 align="center"> 🖥️ Demo </h2>

Input Prompt: `Find me a bar that can host a 20 person event near Chelsea, Manhattan evening of Apr 30th. Fill out contact us form if they have one with info: Name Richard, email he@hrichard.com.`

https://user-images.githubusercontent.com/14324698/234191011-ec73af54-4a8e-4298-be1d-4252050f08c1.mov

Demo made by [Richard He](https://twitter.com/RealRichomie)

<h2 align="center"> 🔮 Features </h2>

- 🌎 Google search
- 🧠 Long-term and short-term memory management
- 🔨 Chrome actions: describe a webpage, scroll to element, click on buttons/links, input forms, switch tabs
- 🤖 Supports multiple agent types: Zero-shot, BabyAGI and Auto-GPT
- 🔥 (IN PROGRESS) Chrome plugin support

<h2 align="center"> 🧱 Known Limitations </h2>

- There are limited web crawling features, with buttons and input fields sometimes failing to appear in prompt.
- The response time is slow, with each action taking between 1-10 seconds to run.
- At times, langchain agents are unable to parse GPT outputs (refer to langchain discussion: https://github.com/hwchase17/langchain/discussions/4065). If you run into this, try specifying a different agent; ie: `python -m chromegpt -a auto-gpt -v -t "{your request}"

<h2 align="center"> Requirements </h2>

- Chrome
- Python >3.8
- Install [Poetry](https://python-poetry.org/docs/#installation)

<h2 align="center"> 🛠️ Setup </h2>

1. Set up your OpenAI [API Keys](https://platform.openai.com/account/api-keys) and add `OPENAI_API_KEY` env variable
2. Install Python requirements via poetry `poetry install`
3. Open a poetry shell `poetry shell`
4. Run chromegpt via `python -m chromegpt`

<h2 align="center"> 🧠 Usage </h2>

- GPT-3.5 Usage (Default): `python -m chromegpt -v -t "{your request}"`
- GPT-4 Usage (Recommended, needs GPT-4 access): `python -m chromegpt -v -a auto-gpt -m gpt-4 -t "{your request}"`
- For help: `python -m chromegpt --help`
```
Usage: python -m chromegpt [OPTIONS]

  Run ChromeGPT: An AutoGPT agent that interacts with Chrome

Options:
  -t, --task TEXT                 The task to execute  [required]
  -a, --agent [auto-gpt|baby-agi|zero-shot]
                                  The agent type to use
  -m, --model TEXT                The model to use
  --headless                      Run in headless mode
  -v, --verbose                   Run in verbose mode
  --human-in-loop                 Run in human-in-loop mode, only available
                                  when using auto-gpt agent
  --help                          Show this message and exit.
```

<h2 align="center"> ⭐ Star History </h2>

[![Star History Chart](https://api.star-history.com/svg?repos=richardyc/Chrome-GPT&type=Date)](https://star-history.com/#richardyc/Chrome-GPT&Date)

