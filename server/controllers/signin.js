const handleSigninPost = (req, res, db, bcrypt) => {
    const { email, password } = req.body;
    if (!email || !password) {
        return res.status(400).json("Incorrect form submission");
    }
    db.collection("users")
        .find({ email: email })
        .toArray(function(err, docs) {
            console.log(docs);
            if (docs.length != 1)
                return res.status(400).json("incorrect email id");
            const isPasswordValid = bcrypt.compareSync(
                password,
                docs[0].password
            );
            if (isPasswordValid) {
                return res.status(200).json(docs[0]);
            } else {
                return res.status(400).json("incorrect credentials");
            }
        });
};

module.exports = {
    handleSigninPost: handleSigninPost
};
