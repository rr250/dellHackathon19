const express = require("express");
const bcrypt = require("bcrypt");
const bodyParser = require("body-parser");
const assert = require("assert");
const MongoClient = require("mongodb").MongoClient;
const url = "mongodb://localhost:27017";
const client = new MongoClient(url, {
    useNewUrlParser: true,
    useUnifiedTopology: true
});
const dbName = "dell";
// const cors = require('cors');

const register = require("./controllers/register");
const signin = require("./controllers/signin.js");
const items = require("./controllers/items.js");

const app = express();
// app.use(cors());
app.use(bodyParser.json());

app.get("/", (req, res) => {
    res.json("It's working");
});
app.get("/item/:id", (req, res) => {
    items.handleItemGet(req, res, db);
});
app.post("/signin", (req, res) => {
    signin.handleSigninPost(req, res, db, bcrypt);
});
app.post("/register", (req, res) => {
    register.handleRegisterPost(req, res, db, bcrypt);
});
app.post("/order", (req, res) => {
    orders.handleOrderPost(req, res, db);
});

client.connect((err, client) => {
    if (err) return console.log(err);
    db = client.db(dbName); // whatever your database name is
    app.listen(3000, err => {
        if (err) {
            throw err;
        } else {
            console.log(`App is listening on Port 3000`);
        }
    });
});
