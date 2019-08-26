const items = require('./items.js');

const handleOrderPost = (req, res, db) => {
    const { itemId, buyer, amount } = req.body;
    const latestItemId = items.handleLatestItem(db);

    db.collection('orders').insertOne(
        { }
    )
}

module.exports = {
    handleOrderPost: handleOrderPost
}