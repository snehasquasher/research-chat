import React, { ChangeEvent, useCallback, useEffect, useState} from "react";
import UrlButton from "./UrlButton";
import { useRouter } from 'next/router';

import { Button } from "./Button";
interface ContextProps {
  className: string;
  selected: string[] | null;
  uploads: Array<string>
}

export const SettingsCard: React.FC<ContextProps> = ({ className, selected, uploads }) => {
  /*const [entries, setEntries] = useState([]);*/
  console.log("UPLOADS ", uploads);
  const router = useRouter();
  const [splittingMethod, setSplittingMethod] = useState("markdown");
  const [chunkSize, setChunkSize] = useState(256);
  const [overlap, setOverlap] = useState(1);

  // Scroll to selected card
  /*useEffect(() => {
    const element = selected && document.getElementById(selected[0]);
    element?.scrollIntoView({ behavior: "smooth" });
  }, [selected]);*/

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
              <option value="markdown">Markdown Splitting</option>
            </select>
          </div>
          {splittingMethod === "recursive" && (
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
                  onChange={(e) => setOverlap(parseInt(e.target.value))}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
