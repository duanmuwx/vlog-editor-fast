import React from "react";
import ReactDOM from "react-dom/client";
import { ConfigProvider } from "antd";
import { Provider } from "react-redux";
import { HashRouter } from "react-router-dom";

import App from "./App";
import { store } from "./store/store";
import "./styles/global.css";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <Provider store={store}>
      <ConfigProvider
        theme={{
          token: {
            colorPrimary: "#1677ff",
          },
        }}
      >
        <HashRouter>
          <App />
        </HashRouter>
      </ConfigProvider>
    </Provider>
  </React.StrictMode>,
);
