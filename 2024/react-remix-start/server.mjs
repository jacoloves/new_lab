import { createRequestHandler } from "@remix-run/express";
import { broadcastDevReady } from "@remix-run/node";
import express from "express";

import * as build from "./build/index.js";

const app = express();
app.use(express.static("public"));

app.all("*", createRequestHandler({ build }));

app.listen(3000, () => {
    if (process.env.NODE_ENV === "development") {
        broadcastDevReady(build);
    }

    console.log("App listening on http://localhost:3000");
});