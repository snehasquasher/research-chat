import React from "react";

const selectedPDFsContext = React.createContext({
    selectedPDFs: [] as string[],
    setSelectedPDFs: (selectedPDFs: string[]) => {},
  });


export default selectedPDFsContext;