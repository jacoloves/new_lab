import { useState } from "react";

export const SimpleButton: () => JSX.Element = () => {
  const [state, setState] = useState(true);
  const handleClick = () =>{
    setState((prevState) => !prevState);
  };
  return <button onClick={handleClick}>{state ? "ON" : "OFF"}</button>;
};
