import dotenv from "dotenv"
dotenv.config();
import { Client, LocalAuth } from "whatsapp-web.js"
import qrcode from "qrcode-terminal"
import { MessageEvent } from "./message_event";
import express from "express";

export const wwclient: Client = new Client({
    authStrategy: new LocalAuth({
        dataPath: "whatsapp_cache"
    }),
    puppeteer: {
        headless: true, // change to false for debugging
        args: [
            '--no-sandbox',
            '--disable-setupid-sandbox'
        ]
    }
});

wwclient.on('qr', (qr) => {
    console.log('QR RECEIVED');
    qrcode.generate(qr, { small: true });
});

wwclient.on("auth_failure", () => {
    console.log("Authentication failure");
});

wwclient.on("ready", async () => {
    console.log("WhatsApp Client is ready!");
    const phoneNumber = process.env.PHONE_NUMBER_SERIALIZED;
    if (phoneNumber) {
        try {
            await wwclient.sendMessage("91" + phoneNumber + "@c.us", "WhatsApp API Bridge Started");
        } catch (e) {
            console.error("Failed to send startup message:", e);
        }
    }
});

wwclient.on("message", async (message) => {
    MessageEvent(message);
});

wwclient.initialize();

const app = express();
const port = 3001;

app.use(express.json());

app.post("/send-message", async (req, res) => {
    const { contact, message } = req.body;

    if (!contact || !message) {
        return res.status(400).json({ success: false, error: "Missing contact or message" });
    }

    try {
        const chatId = "91" + contact + "@c.us";
        await wwclient.sendMessage(chatId, message);
        console.log(`Message sent to ${contact}: ${message}`);
        res.json({ success: true });
    } catch (error) {
        console.error("Failed to send message:", error);
        res.status(500).json({ success: false, error: (error as Error).message });
    }
});

app.get("/health", (req, res) => {
    res.json({ status: "ok", whatsapp_ready: wwclient.info !== undefined });
});

app.listen(port, () => {
    console.log(`WhatsApp API server listening at http://localhost:${port}`);
});
