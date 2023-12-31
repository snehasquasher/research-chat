
import React, { FormEvent, useRef, useState, useEffect, useContext } from "react";
import { SettingsCard } from "@/components/SettingsCard";
import { useChat, Message } from "ai/react";
import { loadEvaluator } from "langchain/evaluation";
import va from "@vercel/analytics";
import clsx from "clsx";
import ReactMarkdown from "react-markdown";
import Textarea from "react-textarea-autosize";
import * as url from "url";
import { useRouter } from 'next/router';
import ScoreDisplay from '../components/ScoreDisplayCard';
import selectedPDFsContext from '../context/selectedContext'
import LoadingAnimation from '../components/LoadingAnimation';
import {metaPromptContext} from '../components/SettingsCard';

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
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const [selectedPDFs, setSelectedPDFs] = useState<string[]>([]);
  const selectedValue = { selectedPDFs, setSelectedPDFs };
  const [useMetaPrompt, setUseMetaPrompt] = useState(false);
  const [metaPrompt, setMetaPrompt] = useState("");
  const [metaPromptGenerated, setMetaPromptGenerated] = useState(false);
  const metaPromptValue = {useMetaPrompt, setUseMetaPrompt}

  useEffect(() => {
    // Fetch the list of uploaded file names and set them as selected
    console.log("HI");
    const fetchUploadedFiles = async () => {
      try {
        const response = await fetch('/api/fetchFileNames');
        if (response.ok) {
          const files = await response.json();
          setUploadedFiles(files); // Set fetched files as selected
          setSelectedPDFs(files); // default: set all uploads as selected
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



  const { input, setInput } = useChat({
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
    setIsLoading(true); // Set loading to true before the request
    console.log("use meta prompt? ", useMetaPrompt);
    console.log(selectedPDFs)

    if (useMetaPrompt && !metaPromptGenerated) {
      console.log("need generate metaPrompt");

      let metaReq = await fetch('/api/generateMetaPrompt', {
        method: 'get'
      });

      console.log(metaReq)
    
      let metaResponse = await metaReq.json();
      console.log(metaResponse);
      let cleanedMetaPrompt = metaResponse.replace("{context_str}", '{context}');
      if (metaReq.ok) {
        // status code was 200-299
        console.log("OK ", cleanedMetaPrompt);
        setMetaPrompt(cleanedMetaPrompt);
        setMetaPromptGenerated(true);
      } else {
        // status was something else
        console.log("error: could not generate metaResponse");
      } 
    }
  
    // Check if any elements in uploadedFiles are None
    if (selectedPDFs.some(file => !file)) {
      console.error("Selected files contain None values");
      return; // Don't proceed with the request
    }

    console.log("selected PDFs for this response: ", selectedPDFs)
  
    let data = JSON.stringify({
      messages: [{ role: "user", content: oldInput }],
      filenames: selectedPDFs, // Send array of selected filenames
      metaPrompt: metaPrompt,
    });

    console.log(data);

    let req = await fetch('/api/chat', {
      method: 'post',
      headers: {
        'Content-Type': 'application/json'
      },
      body: data
    });
  
    let response = await req.json();
    console.log(response);
    setIsLoading(false);
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
  console.log("UPLOADED FILES: ", uploadedFiles)

  return (
    <selectedPDFsContext.Provider value={selectedValue}>
    <metaPromptContext.Provider value={metaPromptValue}>
    <main className="p-5 px-8 flex flex-row justify-between">
    
    <div className="flex  flex-grow flex-col items-center justify-between pb-40">
      <div className=" hidden w-full justify-between px-5 sm:flex">
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
         <div className="border-gray-200sm:mx-0 mx-5  max-w-screen-md rounded-md border sm:w-full">
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
      <div className="-bottom flex w-full flex-col items-center space-y-3  fromfixed-transparent via-gray-100 to-gray-100 p-5 pb-3 sm:px-0">
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
          {isLoading && <LoadingAnimation />}
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
        
      </div>
      
      </div>
      <div> 
          <SettingsCard className="max-w-md" selected={selectedPDFs} uploads={uploadedFiles} />
        </div>
      
    </main>
    </metaPromptContext.Provider>
    </selectedPDFsContext.Provider>
  );
}
