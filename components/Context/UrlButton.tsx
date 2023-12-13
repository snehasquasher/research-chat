// UrlButton.tsx

import { Button } from "./Button";
import React, { FC } from "react";
import Link from "next/link";

export interface IUrlEntry {
  url: string;
  title: string;
  seeded: boolean;
  loading: boolean;
}

interface IURLButtonProps {
  entry: string;
}

const UrlButton: FC<IURLButtonProps> = ({ entry}) => (
  <div key={entry} className="pr-2 lg:flex-grow">
    <Button
      className={`relative overflow-hidden w-full my-1 lg:my-2 mx-2 `}
      style={{
        backgroundColor: "bg-gray-800",
        color: "white",
      }}
    >
      <div className="relative">{entry}</div>
    </Button>
  </div>
);

export default UrlButton;
