// UrlButton.tsx

import { Button } from "./Button";
import React, { useContext, FC } from "react";
import Link from "next/link";
import selectedPDFsContext from "@/context/selected-context";

export interface IUrlEntry {
  url: string;
  title: string;
  seeded: boolean;
  loading: boolean;
}

interface IURLButtonProps {
  entry: string;
  selected: string[] | null;
}

const UrlButton: FC<IURLButtonProps> = ({ entry, selected}) => {
  const { selectedPDFs, setSelectedPDFs } = useContext(selectedPDFsContext);
  function handleClick() {
    if (!selectedPDFs.includes(entry)) {

      setSelectedPDFs([...selectedPDFs, entry])
      console.log('PDF added. selected: ', selectedPDFs);
    }
    else {
      let filteredArray = selectedPDFs.filter(item => item !== entry)
      setSelectedPDFs(filteredArray)
      console.log('PDF removed. selected: ', selectedPDFs); // doesn't update until after?
    }
    
  }

  return (
  <div key={entry} className="pr-2 lg:flex-grow">
    <Button
      className={`relative overflow-hidden w-full my-1 lg:my-2 mx-2 ${selectedPDFs && selectedPDFs.includes(entry) 
        ? "bg-zinc-800" : "bg-zinc-400"}`}
      style={{color: "white"}}
      onClick={handleClick}
    >

      <div className="relative">{entry}</div>
    </Button>
  </div>
);
      };

export default UrlButton;
