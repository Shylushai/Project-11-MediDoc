import { ThemeProvider, createTheme } from "@mui/material/styles";
import "./App.css";
import SignIn from "./pages/SignIn";

function App() {
  const defaultTheme = createTheme();

  return (
    <>
      <ThemeProvider theme={defaultTheme}>
        <SignIn />
      </ThemeProvider>
    </>
  );
}

export default App;
