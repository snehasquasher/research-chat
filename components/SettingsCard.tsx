import React, { useContext ,ChangeEvent, useCallback, useEffect, useState, Dispatch, SetStateAction} from "react";
import UrlButton from "./UrlButton";
import selectedPDFsContext from '../context/selectedContext';
import { useRouter } from 'next/router';
import { Button } from "./Button";

interface ContextProps {
  className: string;
  selected: string[] | null;
  uploads: Array<string>
}

// Define a type for the context value
type MetaPromptContextType = {
  useMetaPrompt: boolean;
  setUseMetaPrompt: Dispatch<SetStateAction<boolean>>;
};

// Create the context with the default value and type
export const metaPromptContext = React.createContext<MetaPromptContextType>({
  useMetaPrompt: false,
  setUseMetaPrompt: () => {},
});

export const SettingsCard: React.FC<ContextProps> = ({ className, selected, uploads }) => {
  /*const [entries, setEntries] = useState([]);*/
  console.log("UPLOADS ", uploads);
  
  const { selectedPDFs, setSelectedPDFs } = useContext(selectedPDFsContext);
  const {useMetaPrompt, setUseMetaPrompt} = useContext(metaPromptContext);
  const router = useRouter();
  const [splittingMethod, setSplittingMethod] = useState("markdown");
  const [chunkSize, setChunkSize] = useState(256);
  const [overlap, setOverlap] = useState(1);
  const metaPromptValue = {useMetaPrompt, setUseMetaPrompt}

  console.log(useMetaPrompt);

  const handleSaveSettings = async () => {
    const payload = {
      files: selectedPDFs, // Assuming selectedPDFs is an array of filenames
      chunk_size: chunkSize,
      chunk_overlap: overlap,
      method: splittingMethod,
    };

    console.log(selectedPDFs,chunkSize,overlap,splittingMethod);
  
    try {
      const response = await fetch('/api/generate_embeddings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Include any authentication or other necessary headers here
        },
        body: JSON.stringify(payload),
      });
  
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
  
      const data = await response.json();
      console.log("Response data:", data);
      // Handle your success scenario here, like updating UI or state
    } catch (error) {
      console.error('Error saving settings:', error);
      // Handle your error scenario here, like showing a user message
    }
  };
  

  const DropdownLabel: React.FC<
    React.PropsWithChildren<{ htmlFor: string }>
  > = ({ htmlFor, children }) => (
    <label htmlFor={htmlFor} className="text-white p-2 font-bold">
      {children}
    </label>
  );

  const buttons = uploads.map((entry, key) => (
    <div className="" key={`${key}-${entry}`}>
      <UrlButton
        entry={entry}
        selected={selected}
      />
    </div>
  ));

  const clearIndex = async(e: Event) => {
    e.preventDefault();
    let req = await fetch('/api/clear_index', {
      method: 'post',
    });
  
    let response = await req.json();
    console.log(response);
  
    if (req.ok) {
      // status code was 200-299
      console.log("OK");
    }
    else {
      // status was something else
      console.log("error");
    }

    let reqDeleteFiles = await fetch('/api/clearFileNames', {
      method: 'post',
    });
  
    let resDeleteFiles = await reqDeleteFiles.json();
    console.log(resDeleteFiles);
  
    if (reqDeleteFiles.ok) {
      // status code was 200-299
      console.log("OK");
    }
    else {
      // status was something else
      console.log("error");
    }

    router.push("/")
  }


  return (
    <div
      className={`flex flex-col border-2 overflow-y-auto rounded-lg border-gray-500 w-full ${className}`}
    >
      <div className="flex flex-col items-start sticky top-0 w-full">
        <div className="space-y-4 p-7 sm:p-4 text-xl font-semibold text-white">Your Documents </div>
        <div className="flex flex-col items-start lg:flex-row w-full lg:flex-wrap p-2">
          {buttons}
        </div>
        <div className="flex-grow w-full px-4">
          <Button
            className="w-full my-2 uppercase active:scale-[98%] transition-transform duration-100"
            style={{
              backgroundColor: "#4f6574",
              color: "white",
            }}
            onClick={clearIndex}
          >
            Clear Index
          </Button>
        </div>
        <div className="flex p-2"></div>
        <div className="text-left w-full flex flex-col rounded-b-lg bg-gray-600 p-3 subpixel-antialiased">
          <DropdownLabel htmlFor="splittingMethod">
            Splitting Method:
          </DropdownLabel>
         
          <div className="relative w-full">
            <select
              id="splittingMethod"
              value={splittingMethod}
              className="p-2 bg-gray-700 rounded text-white w-full appearance-none hover:cursor-pointer"
              onChange={(e) => setSplittingMethod(e.target.value)}
            >
              <option value="recursive">Recursive Text Splitting</option>
              <option value="character">Character Text Splitting</option> 
              <option value="sentence">Sentence Text Splitting - spaCy</option> 
            </select>
          </div>
            <div className="my-4 flex flex-col">
              <div className="flex flex-col w-full">
                <DropdownLabel htmlFor="chunkSize">
                  Chunk Size: {chunkSize}
                </DropdownLabel>
                <input
                  className="p-2 bg-gray-700"
                  type="range"
                  id="chunkSize"
                  min={1}
                  max={2048}
                  value={chunkSize}
                  onChange={(e) => setChunkSize(parseInt(e.target.value))}
                />
              </div>
              <div className="flex flex-col w-full">
                <DropdownLabel htmlFor="overlap">
                  Overlap: {overlap}
                </DropdownLabel>
                <input
                  className="p-2 bg-gray-700"
                  type="range"
                  id="overlap"
                  min={1}
                  max={200}
                  value={overlap}
                  onChange={(e) => setOverlap(parseInt(e.target.value))}
                />
              </div>
              <div className="flex flex-row w-full">              
              <label  className="text-white p-2 font-bold"> 
                  Use Meta-Prompting (Warning: Takes long to run) </label>
                    <input
                       className="p-2"
                        type="checkbox" 
                        // value={}
                        name="time" 
                        onChange={(e) => setUseMetaPrompt(e.target.checked)}
                        id="promptOptimization"
                        // checked={item.checked}
                        />
                  
              </div>
            </div>
      
           <div className="w-full px-4 py-2">
       
        <Button
          className="w-full my-2 uppercase active:scale-[98%] transition-transform duration-100"
          style={{
            backgroundColor: "#4f6574",
            color: "white",
          }}
          onClick={handleSaveSettings} // Set the onClick handler to the save function
        >
          Save Settings
        </Button>
      </div>
        </div>
        
      </div>
    </div>
  );
};
