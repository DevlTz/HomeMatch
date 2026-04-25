import React from "react";
import { LandingScreen } from "./screens/LandingScreen";
 
export default function App() {
  return <LandingScreen onEnter={() => console.log("entrou")} />;
}
