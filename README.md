# 🤖 Chrome-GPT: An AutoGPT agent that interacts with Chrome
 
Chrome-GPT is a powerful AutoGPT agent that utilizes [Langchain](https://github.com/hwchase17/langchain) and [Selenium](https://github.com/SeleniumHQ/selenium) to enable control of an entire Chrome session. With the ability to interactively scroll, click, and input text on web pages, the AutoGPT agent can navigate and manipulate web content.

<h2 align="center"> 🖥️ Demo </h2>

Input Prompt: `Find me a bar that can host a 20 person event near Chelsea, Manhattan evening of Apr 30th. Fill out contact us form if they have one with info: Name Richard, email he@hrichard.com.`

https://user-images.githubusercontent.com/14324698/234191011-ec73af54-4a8e-4298-be1d-4252050f08c1.mov

Demo made by [Richard He](https://twitter.com/RealRichomie)

<h2 align="center"> 🔮 Features </h2>

- 🌎 Google search
- 🧠 Long-term and short-term memory management
- 🔨 Chrome actions: describe a webpage, scroll to element, click on buttons/links, input forms, switch tabs

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
- GPT-4 Usage (Recommended): `python -m chromegpt -v -a auto-gpt -m gpt-4 -t "{your request}"`
- For help: `python -m chromegpt --help`
