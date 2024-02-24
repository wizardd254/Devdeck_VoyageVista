const mongoose = require('mongoose');

const connectionstring = "mongodb+srv://priyansh:gydxAOflyryQCjXr@userdata.j2vcztu.mongodb.net/?retryWrites=true&w=majority&appName=Userdata"
mongoose
   .connect(connectionstring)
   .then(()=>console.log("CONNECTED TO THE DB"))
   .catch((err)=>console.log(err))

const userSchema = new mongoose.Schema({

    name:{
        type:String,
        required:true,
        unique: true
    },
    password:{
        type:String,
        required:true
    }
})

const collection = new mongoose.model("collection1",userSchema);

module.exports=collection;

