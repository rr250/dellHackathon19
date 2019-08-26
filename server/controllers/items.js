const handleItemGet = (req, res, db) => {
    const { id } = req.params;
    if (!id || id <= 0) {
        return res.status(400).json("Incorrect form submission");
    }
    db.collection("items")
        .find({ itemId: Number(id) })
        .toArray(function(err, doc) {
            if (doc.length != 1)
                return res.status(400).json("incorrect item id");
            else return res.status(200).json(doc[0]);
        });
};

module.exports = {
    handleItemGet: handleItemGet
};
