const handleRegisterPost = (req, res, db, bcrypt) => {
    console.log(req.body);
    const { email, name, password, username } = req.body;
    if (!email || !name || !password) {
        return res.status(400).json("Incorrect form submission");
    }
    var fullName = name.split(" ");
    var hash = bcrypt.hashSync(password, 10);
    db.collection("users").insertOne(
        {
            first_name: fullName[0],
            last_name: fullName[1],
            email: email,
            password: hash,
            username: username,
            created_on: "Date.now()",
            updated_on: null
        },
        function(err, r) {
            
        }
    );
    return res.status(200).json("User registered successfully");
};

module.exports = {
    handleRegisterPost: handleRegisterPost
};
