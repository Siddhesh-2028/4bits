import { Chat, Message } from "whatsapp-web.js";

export const MessageEvent = async (message: Message) => {
    let contact: string = (await message.getContact()).id._serialized;
    let chat: Chat = await message.getChat();

    if (chat.isGroup) return;
}