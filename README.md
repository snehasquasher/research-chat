
# ChatLore
> A Retrieval Augmented Generation powered application to chat with your research papers. While you can directly start playing with ChatLore, you can also experiment with its various model settings (Chunk Size, Chunk Overlaps, Retrieval Methods and Text Splitter Methods). ChatLore provides evaluations after each response going off three major criteria: Answer Relevance, Context Relevance and Faithfulness.


📝 Key Features:
- upload & chat with research papers
- model response evaluation on heuristics
- parameter tuning on the UI 

## Tech Stack 🛠️
- Front-End: TypeScript & TailWind CSS 🚀
- Back-End: Flask
- Vector Database: Pinecone DB
- ChatBot: Open AI API 💬 & LangChain API & llama Index API
- Deployment: Vercel 


## Code Structure
Below is an overview of the key components of our repository:

### Key Components

- `api/`: This directory contains all of our backend Flask endpoints.
- `utils/`: This directory contains our helper functions for backend Flask endpoints. 
- `components/`: This directory contains the components that we used to construct the frontend of the application
- `requirements.txt/`: The file contains the list of python modules to install in order to get the project running
- `pages`: This directory contains all the major routing logic and the different pages. 
- `.env.example`: Provides a template for setting up environment variables.
- `.gitignore`: Configures files and directories that should not be tracked by Git.
- `README.md`: The document you are reading now. It provides an overview of the project, instructions for setup, usage, and contribution guidelines.
- `pull_request_template.md`: Pull request template for PRs  


## How It Works

### Retrieval Augmented Generation Pipeline 
![image](https://github.com/snehasquasher/research-chat/assets/65848151/1bbbd3c8-d50b-4642-9ecb-5a0863e282ab)

RAG is a technique that combines a retrieval model and a generative model to produce coherent text.

The retrieval model fetches relevant information from a database of documents. This provides context to the generative model.
The generative model, usually a large language model like GPT-3, uses the retrieved information to craft a response.
Together, these components allow RAG systems to leverage both external knowledge and natural language generation abilities. Benefits include:

Access to up-to-date, factual information
More focused and relevant responses
Ability to summarize documents and synthesize ideas
RAG helps overcome some limitations of large language models while retaining their fluency and coherence. The modular architecture also allows for customization to specific use cases.

## Demo

https://nextjs-flask-starter.vercel.app/

## Running Locally
In order to run the app locally, first ensure you have the npm CLI installed. 
Then set up the .env fle as per the example in .env.example.
(NOTE: Please email anushka.nijhawan@yale.edu if you need the variables.)

First, install the dependencies:

```bash
npm install
# or
yarn
# or
pnpm install
```

Then, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

The Flask server will be running on [http://127.0.0.1:5328](http://127.0.0.1:5328) – feel free to change the port in `package.json` (you'll also need to update it in `next.config.js`).
