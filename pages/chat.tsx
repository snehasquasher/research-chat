
import React, { FormEvent, useRef, useState, useEffect } from "react";
import { Context } from "@/components/Context";
import { useChat, Message } from "ai/react";
import { loadEvaluator } from "langchain/evaluation";
import va from "@vercel/analytics";
import clsx from "clsx";
import ReactMarkdown from "react-markdown";
import Textarea from "react-textarea-autosize";
import * as url from "url";
import { useRouter } from 'next/router';
import ScoreDisplay from '../components/ScoreDisplayCard';
import selectedPDFsContext from '../context/selected-context'

const examples = [
  "Compare and contrast the abstracts of the documents I uploaded.",
  "Summarize the contents of my first document.",
  "What are some common limitations found in these research papers?",
];


export default function Chat() {
  const formRef = useRef<HTMLFormElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const [PDFCount, setPDFCount] = useState(0); // Initialize PDFCount to 0
  const [messages, setMessages] = useState<Message[]>([]);
  const [messageCount, setMessageCount] = useState(0);
  const { asPath } = useRouter();
  const [faithfulnessScore, setFaithfulnessScore] = useState(0);
  const [contextRelevanceScore, setContextRelevanceScore] = useState(0);
  const [answerRelevanceScore, setAnswerRelevanceScore] = useState(0);
  const [uploadedFileNames, setUploadedFileNames] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [context, setContext] = useState<string[] | null>(null);

  const [selectedPDFs, setSelectedPDFs] = useState<string[]>([]);
  const selectedValue = { selectedPDFs, setSelectedPDFs };

  useEffect(() => {
    // Fetch the list of uploaded file names and set them as selected
    const fetchUploadedFiles = async () => {
      try {
        const response = await fetch('/api/fetchFileNames');
        if (response.ok) {
          const files = await response.json();
          setSelectedFiles(files); // Set fetched files as selected
          setPDFCount(files.length); // Update PDFCount based on the number of files
          console.log("FILES: ", files);
        } else {
          console.error('Failed to fetch uploaded files');
        }
      } catch (error) {
        console.error('Error fetching uploaded files:', error);
      }
    };

    fetchUploadedFiles(); // Trigger the fetching of uploaded file names when the component mounts

  }, []);
  console.log(asPath);

  const evaluateAnswers = async (context: string, answer: string, question: string) => {
    try {
        const response = await fetch('/api/evaluate-answers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ context, answer, question })
        });

        if (!response.ok) {
            throw new Error(`Evaluation failed: ${response.status}`);
        }

        const {
            faithfulness_score,
            context_relevance_score,
            answer_relevance_score
        } = await response.json();

        // Update state or perform any necessary actions with the scores
        setFaithfulnessScore(faithfulness_score);
        setContextRelevanceScore(context_relevance_score);
        setAnswerRelevanceScore(answer_relevance_score);
    } catch (error) {
        console.error('Error evaluating answers:', error);
        // Handle the error or provide a default score
    }
};



  const { input, setInput, isLoading } = useChat({
    onResponse: (response) => {
      if (response.status === 429) {
        va.track("Rate limited");
        return;
      } else {
        va.track("Chat initiated");
      }
    },
    onError: (error) => {
      va.track("Chat errored", {
        input,
        error: error.message,
      });
    },
  });

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    let oldInput = input;
    setInput("");
  
    // Check if any elements in selectedFiles are None
    if (selectedFiles.some(file => !file)) {
      console.error("Selected files contain None values");
      return; // Don't proceed with the request
    }
  
    let data = JSON.stringify({
      messages: [{ role: "user", content: oldInput }],
      filenames: selectedFiles // Send array of selected filenames
    });
  
    let req = await fetch('/api/chat', {
      method: 'post',
      headers: {
        'Content-Type': 'application/json'
      },
      body: data
    });
  
    let response = await req.json();
    console.log(response);
  
    if (req.ok) {
      // status code was 200-299
      console.log("OK");
      const ai_response = response.response; // Extracting AI's response
      const ai_context = response.context;  
      const reqMessage: Message = {
        id: messages.length.toString(),
        role: 'user',
        content: oldInput,
      };
      const resMessage: Message = {
        id: (messages.length + 1).toString(),
        role: 'assistant',
        content: ai_response,
      };
      let messagesCopy = messages;
      messagesCopy.push(reqMessage);
      messagesCopy.push(resMessage);
      setMessages(messagesCopy);
      console.log(messages);
      setMessageCount(messages.length);
      await evaluateAnswers(ai_context, ai_response, oldInput); // Update scores based on the latest response
    } else {
      // status was something else
      console.log("error");
    }
  }
  
  const disabled = isLoading || input.length === 0;
  console.log("SELECTED FILES: ", selectedFiles)

  return (
    <selectedPDFsContext.Provider value={selectedValue}>
    <main className="flex flex-row justify-between">
       
    <div className="p-5 flex flex-col items-center justify-between pb-40">
      <div className="absolute top-5 hidden w-full justify-between px-5 sm:flex">
        <a
          href="/deploy"
          target="_blank"
          className="rounded-lg p-2 transition-colors duration-200 hover:bg-stone-100 sm:bottom-auto"
        >
        </a>
        <a
          href="/github"
          target="_blank"
          className="rounded-lg p-2 transition-colors duration-200 hover:bg-stone-100 sm:bottom-auto"
        >
        </a>
      </div>
      {messageCount > 0 ? (
      messages.map((message, i) => (
        <div key={i} className={clsx(
          "flex flex-col items-center w-full border-b border-gray-200 py-8",
          message.role === "user" ? "bg-purple" : "bg-black-100",
        )}>
          <div className="w-full max-w-screen-md px-5 sm:px-0">
            <div
              className={clsx(
                "p-1.5 text-black",
                message.role === "assistant" ? "bg-violet-200" : "bg-black",
              )}
            ></div>
            <ReactMarkdown
              className="prose mt-1 break-words prose-p:leading-relaxed"
              components={{
                a: (props) => (
                  <a {...props} target="_blank" rel="noopener noreferrer" />
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
          {message.role === "assistant" && (
            <div className="flex w-full max-w-screen-md justify-center space-x-4 px-5 pt-8 margin-top sm:px-0">
              <ScoreDisplay label="Faithfulness" score={faithfulnessScore} />
              <ScoreDisplay label="Context Relevance" score={contextRelevanceScore} />
              <ScoreDisplay label="Answer Relevance" score={answerRelevanceScore} />
            </div>
          )}
        </div>
      ))
      ) : (
         <div className="border-gray-200sm:mx-0 mx-5 mt-20 max-w-screen-md rounded-md border sm:w-full">
          <div className="flex flex-col space-y-4 p-7 sm:p-10">
            <h1 className="text-lg font-semibold ">
              Chat with your documents now!
            </h1>
            
          </div>
          <div className="flex flex-col space-y-4 border-t border-gray-200 bg-gray-100 bg-info p-7 sm:p-10">
            {examples.map((example, i) => (
              <button
                key={i}
                className="rounded-md border border-gray-200 bg-white px-5 py-3 text-left text-sm text-gray-500 transition-all duration-75 hover:border-black hover:text-gray-700 active:bg-gray-50"
                onClick={() => {
                  setInput(example);
                  inputRef.current?.focus();
                }}
              >
                {example}
              </button>
            ))}
          </div>
          <div className="flex flex-col space-y-4 p-7 sm:p-10">
            <p>Total documents: {PDFCount}</p>
            
          </div>
        </div>
      )}
      <div className="fixed-bottom flex w-full flex-col items-center space-y-3 bg-gradient-to-b from-transparent via-gray-100 to-gray-100 p-5 pb-3 sm:px-0">
        <form
          ref={formRef}
          onSubmit={handleSubmit}
          className="relative w-full max-w-screen-md rounded-xl border border-gray-200 bg-white px-4 pb-2 pt-3 shadow-lg sm:pb-3 sm:pt-4"
        >
          <Textarea
            ref={inputRef}
            tabIndex={0}
            required
            rows={1}
            autoFocus
            placeholder="Ask a question"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                formRef.current?.requestSubmit();
                e.preventDefault();
              }
            }}
            spellCheck={false}
            className="textarea w-full pr-10 focus:outline-none text-dark"
          />
          <button
            className={clsx(
              "absolute inset-y-0 right-3 my-auto flex h-8 w-8 items-center justify-center rounded-md transition-all",
              disabled
                ? "cursor-not-allowed bg-white"
                : "bg-green-500 hover:bg-green-600",
            )}
            disabled={disabled}
          >
            
          </button>
        </form>
        <p className="text-center text-xs text-gray-400">
          Built with{" "}
          <a
            href="https://platform.openai.com/docs/guides/gpt/function-calling"
            target="_blank"
            rel="noopener noreferrer"
            className="transition-colors hover:text-black"
          >
            OpenAI Functions
          </a>{" "}
          and{" "}
          <a
            href="https://sdk.vercel.ai/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="transition-colors hover:text-black"
          >
            Vercel AI SDK
          </a>
          .{" "}
          <a
            href="https://github.com/steven-tey/chathn"
            target="_blank"
            rel="noopener noreferrer"
            className="transition-colors hover:text-black"
          >
            View the repo
          </a>{" "}
          or{" "}
          <a
            href="https://vercel.com/templates/next.js/chathn"
            target="_blank"
            rel="noopener noreferrer"
            className="transition-colors hover:text-black"
          >
            deploy your own
          </a>
          .
        </p>
      </div>
      </div>
      <div className="absolute top-5 transform  ease-in-out right-0 w-1/3 h-full bg-gray-700 overflow-y-auto lg:static lg:translate-x-0 lg:w-2/5 lg:mx-2 rounded-lg">
          <Context className="" selected={selectedPDFs} uploads={selectedFiles} />
        </div>
    </main>
    </selectedPDFsContext.Provider>
  );
}
