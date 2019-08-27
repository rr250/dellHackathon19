const handleRegisterPost = (req, res, db, bcrypt) => {
    console.log(req.body);
    const { email, name, password, username } = req.body;
    if (!email || !name || !password || !username) {
        return res.status(400).json("Incorrect form submission");
    }
    var fullName = name.split(" ");
    var hash = bcrypt.hashSync(password, 10);

    // find latest userId
    var latest;
    db.collection("users")
        .find({}, { limit: 1, sort: ["userId", "desc"] })
        .toArray(function(err, result) {
            // console.log(result);
            latest = result[0].userId;
        });
    db.collection("users").insertOne(
        {
            userId: Number(latest) + 1,
            firstName: fullName[0],
            lastName: fullName[1],
            email: email,
            password: hash,
            username: username,
            createdOn: Date.now(),
            updatedOn: null,
            isAuthenticated: false
        },
        function(err, r) {}
    );
    return res.status(200).json("User registered successfully");
};

module.exports = {
    handleRegisterPost: handleRegisterPost
};
