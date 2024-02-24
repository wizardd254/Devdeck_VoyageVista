const express = require("express");
const app = express();
const path = require("path");
const ejs = require("ejs");
const templatepath= path.join(__dirname,'./templates')
const collection = require("./src/mongodb");
const mongoose = require('mongoose');
const { ObjectId } = mongoose.Types;

app.use(express.json());
app.set("view engine","ejs");
app.set("views",templatepath);
app.use(express.urlencoded({extended:false}));

// Set the path to the directory containing your static files
const publicDirectoryPath = path.join(__dirname, "./public");

// Serve static files from the public directory
app.use(express.static(publicDirectoryPath));
app.get("/",(req,res)=>{
    res.render("login");
});

app.get("/signup",(req,res)=>{
    res.render("signup");
});

app.post("/signup",async (req,res)=>{
try{
const data = {
    name:req.body.name,
    password:req.body.password
}
await collection.insertMany([data])

console.log("added to database");
res.redirect('/search');
}
catch(err){
    console.log(err.body);
    res.render("signup");
}
})

app.post("/login",async (req,res)=>{
    try {
        const check = await collection.findOne({name:req.body.name});
        if (check.password==req.body.password) {
           res.redirect(`/search/${check._id}`);
        } else {
            console.log("wrongpassword");
            res.redirect('/login');
        }

    } catch (error) {
        console.log("invalid");
        res.redirect('/login');
    }
      
})

// You need to add a GET route for login
app.get("/login", (req, res) => {
    res.render("login");
});
app.get("/signup", (req, res) => {
    res.render("signup");
});

app.get("/search/:id",(req,res)=>{
    res.render("search");
})


app.listen(8080,()=>{
    console.log("port connected");
});

