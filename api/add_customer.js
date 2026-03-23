export default function handler(req, res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    if (req.method === 'POST') {
        res.status(200).json({ success: true, queueNumber: 1 });
    }
}
