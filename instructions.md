write a basic RAG system

* use tavily for search. 
* see the pseudo code below for the structure
* use python
* use openai compliant llm for the llm. 
- so the base url, model, and api key are read for a .env file. 
* add a basic ui. which is a fastapi app . 
- the ui use websockets to show the progress of the search agent. 
* log everything for a session to a single file in the 'logs' dir. 

* always search the code before writing new code. 
* the senior engineer has directe that we shoudl keep a changelog.md after each sprint. 

* this is a demo app, so keep it simple. 
* only use the requests library for http request to the llm . 

* pydantic modeling is perfered. 
* keep files less than 300 lines long. after years or experience, this is a good length for readability adn maintainability.
* always use uv for python package management.
* use python 3.12

