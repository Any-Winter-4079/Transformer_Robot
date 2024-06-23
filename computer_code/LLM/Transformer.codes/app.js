const environment = process.env.NODE_ENV || 'development';
if (environment === "production") {
    console.log("We are in production.");
} else {
    console.log("We are in development.");
}

// ###################
// ### to set Port ###
// ###################
const port = process.env.PORT || 3000;
// #######################
// ### to identify App ###
// #######################
const appName = process.env.APP_NAME;
// port needs updating (= server.js)
// ########################
// ### to share socials ###
// ########################
const githubUrl = process.env.GITHUB_URL;
// ##############
// ### Checks ###
// ##############
const requiredEnvVars = [
    "APP_NAME",
    "GITHUB_URL",
];
requiredEnvVars.forEach((varName) => {
    if (!process.env[varName]) {
        throw new Error(`${varName} environment variable is required.`);
    }
});

// ################
// ### Packages ###
// ################
import express from "express"; // Node.js framework
import helmet from "helmet"; // HTTP response headers
import assert from "assert"; // assertions
import winston from "winston"; // logging
import slugify from "slugify"; // url slugs
import fs from "fs"; // read posts
import path from "path"; // read posts

// #################
// ### Variables ###
// #################
import {
    otherPostsMenu,
    otherPostsPath,
} from "./config.js";
// ###############
// ### General ###
// ###############
const app = express();
app.set("trust proxy", 1);
app.set("view engine", "ejs");
app.use(helmet());
app.use(express.json());
app.use(express.static("public"));

// ###############
// ### Logging ###
// ###############
const logger = winston.createLogger({
    level: 'silly', // minimum level to log
    format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple(), // or winston.format.json()
      ),
    transports: [
    new winston.transports.Console()
    ],
    exceptionHandlers: [
    // new winston.transports.File({ filename: 'exceptions.log' }),
    new winston.transports.Console()
    ],
    exitOnError: true
});
logger.on('error', function (err) { console.log("Logger error.", err) });
// #############
// ### Slugs ###
// #############
const slugifyOptions = {
    replacement: '-',
    remove: undefined,
    lower: true,
    strict: false,
    locale: 'en'
};
const customSlugify = (string) => slugify(string, slugifyOptions);
// #############
// ### Posts ###
// #############
let otherDocSlugToFileMap = {};
let legalDocSlugToFileMap = {};
async function loadDocSlugs(postsPath) {
    const postSlugToFileMap = {};
    try {
        const files = await fs.promises.readdir(postsPath);
        for (const file of files) {
            const filePath = postsPath + file;

            // Remove file extension to get the base name
            const baseName = path.basename(file, path.extname(file));
            // Generate a slug from the base name
            const slug = customSlugify(baseName);

            // Map the slug to the file path
            postSlugToFileMap[slug] = filePath;
        }
    } catch (err) {
        console.error("Could not list the directory.", err);
        process.exit(1);
    }
    return postSlugToFileMap;
}
loadDocSlugs(otherPostsPath).then(postSlugToFileMap => {
    otherDocSlugToFileMap = postSlugToFileMap;
    console.log("Other posts successfully loaded.");
    console.log(otherDocSlugToFileMap);
});

// best article
app.get("/", (req, res) => {
    res.setHeader("Content-Security-Policy", "script-src 'self' 'unsafe-eval' 'unsafe-inline'");
    res.render("index.ejs", {
        title: appName + " - Home",
        appName: appName
    });
});

// if isLegalDoc: Support button at the top
// else: Github and Youtube buttons
function renderDoc(isLegalDoc) {
    return async function(req, res) {
        let userSlug;
        try {
            userSlug = req.params.slug;
            // Check if the slug only has allowed characters
            assert(/^[\w-]+$/.test(userSlug));

            let postsMenu;
            let postSlugToFileMap;
            if (isLegalDoc) {
                postSlugToFileMap = legalDocSlugToFileMap;
                postsMenu = legalPostsMenu;
            }
            else {
                postSlugToFileMap = otherDocSlugToFileMap;
                postsMenu = otherPostsMenu;
            }

            // Check if the slug exists in our map
            assert(postSlugToFileMap.hasOwnProperty(userSlug));
            
            try {
                // Load the post associated with the slug
                const post = await import(postSlugToFileMap[userSlug]);
        
                // Render the post
                // res.setHeader("Content-Security-Policy", "script-src 'self' 'unsafe-eval'");
                res.setHeader("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-eval' https://unpkg.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; style-src 'self' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com;");
                // res.setHeader("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-eval' https://unpkg.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; style-src 'self' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; frame-src 'self' https://www.youtube.com;");
                
                res.render("post.ejs", {
                    title: appName + " - " + post.default.name,
                    appName: appName,
                    postsMenu: postsMenu,
                    isLegalDoc: isLegalDoc,
                    currentDoc: post.default,
                    supportEmailAddress: isLegalDoc ? supportEmailAddress : null,
                    githubUrl: isLegalDoc ? null : githubUrl,
                });
            } catch (err) {
                console.error(err);
                res.status(500).json({ error: "Internal error." });
            }
        } catch {
            console.log("Invalid slug.");
            // res.status(404).render("404.ejs", {
            //     title: appName + " - Page Not Found",
            //     appName: appName
            // });
        }
    }
}
app.get("/posts/:slug", renderDoc(false));

// app.get("/ip", (req, res) => {
//     console.log(req.ip);
//     res.send(req.ip);
// });

// 14. export
export { app, port, environment };
