import { program } from "commander";
import * as fs from "node:fs/promises";
import { md2html } from "./md2html.js";

program.option("--gfm", "GFM option enable");
program.parse(process.argv);
const filePath = program.args[0];

const cliOptions = {
    gfm: false,
    ...program.opts(),
};

fs.readFile(filePath, { encoding: "utf8" }).then(file => {
    const html = marked.parse(file,{
        gfm: cliOptions.gfm,
    });
    console.log(html);
}).catch(err => {
    console.error(err.message);
    process.exit(1);
});
