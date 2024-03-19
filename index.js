const express = require("express");
const app = express();
const path = require("path");
const ejs = require("ejs");
const templatepath= path.join(__dirname,'./templates')
const collection = require("./src/mongodb");
const mongoose = require('mongoose');
const { Console } = require("console");
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
res.redirect('/');
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
           res.redirect(`/search`);
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

app.get("/blog", (req, res) => {
    res.render("blog");
});
app.get("/aboutus", (req, res) => {
    res.render("aboutus");
});

app.get("/contactus", (req, res) => {
    res.render("contactus");
});

app.get("/destination", (req, res) => {
    res.render("destination");
});

app.get("/search",(req,res)=>{
    const id=req.params.id;
    res.render("search",{id:id});
})

app.get("/plans", (req, res) => {

    const id = req.params.id;
    const city = req.query.city;
    const placelistParam = req.query.placelist; // Retrieve placelist from query parameters
    const descriptionListParam = req.query.description_list;
    console.log("hello");
    console.log(typeof(descriptionListParam))
    console.log(descriptionListParam)
    let placelist = [];
    let descriptionList=[];

    if (placelistParam) {
        placelist = placelistParam.split(','); // Split placelist into an array
    }

    try{
     descriptionList=JSON.parse(descriptionListParam);
    }catch{
     console.log(Error);

    }

    console.log(placelist)
    console.log(descriptionList);

    res.render("myplans", { id: id, city: city, placelist: placelist, descriptionList: descriptionList });
});



app.listen(8080,()=>{
    console.log("port connected");
});

