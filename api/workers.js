export default function handler(req, res) {
    // يمكنك ربط هذا بقاعدة بيانات
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.status(200).json({});
}
