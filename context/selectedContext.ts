import React, { Dispatch, SetStateAction } from "react";

// Define a type for the context value
type SelectedPDFsContextType = {
    selectedPDFs: string[];
    setSelectedPDFs: Dispatch<SetStateAction<string[]>>;
};

// Create the context with the default value and type
const selectedPDFsContext = React.createContext<SelectedPDFsContextType>({
    selectedPDFs: [],
    setSelectedPDFs: () => {},
});

export default selectedPDFsContext;
