/**
 * Chatbot Component
 * Conversational interface for scheduling and booking appointments
 */

import { Bot, Send, User, Loader2, CheckCircle, XCircle } from 'lucide-react';
import React, { useState, useRef, useEffect } from 'react';
import SlotSelector from './SlotSelector';
import {
    AppointmentSlot,
    suggestSlots,
    bookAppointment,
} from '../services/agentService';

interface ChatbotProps {
    authToken: string;
    userId: string;
    userName: string;
}

interface ChatMessage {
    role: 'user' | 'bot';
    content: string;
    timestamp: string;
    slots?: AppointmentSlot[];
    showConfirmation?: boolean;
    bookingSuccess?: boolean;
    bookingError?: string;
}

enum ChatState {
    IDLE = 'idle',
    LOADING_SLOTS = 'loading_slots',
    SHOWING_SLOTS = 'showing_slots',
    CONFIRMING_BOOKING = 'confirming_booking',
    BOOKING = 'booking',
}

const Chatbot: React.FC<ChatbotProps> = ({ authToken, userId, userName }) => {
    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            role: 'bot',
            content: `Hi ${userName}! I'm your scheduling assistant. I can help you book appointments with your doctors. Just tell me when you'd like to schedule an appointment, like "I need to see my doctor tomorrow" or "Book an appointment next week".`,
            timestamp: new Date().toLocaleTimeString(),
        },
    ]);
    const [input, setInput] = useState('');
    const [chatState, setChatState] = useState<ChatState>(ChatState.IDLE);
    const [selectedSlot, setSelectedSlot] = useState<AppointmentSlot | null>(null);
    const [currentSlots, setCurrentSlots] = useState<AppointmentSlot[]>([]);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const addMessage = (role: 'user' | 'bot', content: string, extra?: Partial<ChatMessage>) => {
        const newMessage: ChatMessage = {
            role,
            content,
            timestamp: new Date().toLocaleTimeString(),
            ...extra,
        };
        setMessages((prev) => [...prev, newMessage]);
    };

    const handleSendMessage = async () => {
        if (!input.trim() || chatState !== ChatState.IDLE) return;

        const userMessage = input.trim();
        setInput('');
        addMessage('user', userMessage);

        // Check if user is asking for scheduling
        const schedulingKeywords = [
            'appointment',
            'schedule',
            'book',
            'doctor',
            'visit',
            'see',
            'tomorrow',
            'next week',
            'monday',
            'tuesday',
            'wednesday',
            'thursday',
            'friday',
        ];

        const isSchedulingRequest = schedulingKeywords.some((keyword) =>
            userMessage.toLowerCase().includes(keyword)
        );

        if (isSchedulingRequest) {
            await handleSchedulingRequest(userMessage);
        } else {
            // General response for non-scheduling queries
            addMessage(
                'bot',
                "I'm primarily here to help you schedule appointments. If you'd like to book an appointment, just let me know when you're available!"
            );
        }
    };

    const handleSchedulingRequest = async (userMessage: string) => {
        setChatState(ChatState.LOADING_SLOTS);
        addMessage('bot', 'Let me check available appointment slots for you...');

        try {
            const response = await suggestSlots(userMessage, userId, authToken);

            if (response.slots && response.slots.length > 0) {
                setCurrentSlots(response.slots);
                setChatState(ChatState.SHOWING_SLOTS);
                addMessage(
                    'bot',
                    `I found ${response.slots.length} available slots. Please select one:`,
                    { slots: response.slots }
                );
            } else {
                setChatState(ChatState.IDLE);
                addMessage(
                    'bot',
                    'Sorry, I couldn\'t find any available slots. This might be because you haven\'t uploaded a prescription yet. Please upload a prescription first to link with a doctor.'
                );
            }
        } catch (error: any) {
            setChatState(ChatState.IDLE);
            addMessage(
                'bot',
                `I encountered an error: ${error.message}. Please make sure you've uploaded a prescription and try again.`
            );
        }
    };

    const handleSlotSelection = (slot: AppointmentSlot) => {
        setSelectedSlot(slot);
        setChatState(ChatState.CONFIRMING_BOOKING);

        const { dateStr, timeStr } = formatDateTime(slot.datetime);
        addMessage(
            'bot',
            `You've selected an appointment with ${slot.doctor_name} on ${dateStr} at ${timeStr}. Would you like to confirm this booking?`,
            { showConfirmation: true }
        );
    };

    const handleConfirmBooking = async () => {
        if (!selectedSlot) return;

        setChatState(ChatState.BOOKING);
        addMessage('bot', 'Booking your appointment...');

        try {
            const response = await bookAppointment(
                userId,
                selectedSlot.doctor_id,
                selectedSlot.datetime,
                authToken
            );

            if (response.success) {
                setChatState(ChatState.IDLE);
                setSelectedSlot(null);
                setCurrentSlots([]);
                addMessage(
                    'bot',
                    `✅ Success! Your appointment with ${selectedSlot.doctor_name} has been booked. You'll receive a confirmation notification shortly.`,
                    { bookingSuccess: true }
                );
            } else {
                setChatState(ChatState.IDLE);
                addMessage(
                    'bot',
                    `❌ Booking failed: ${response.error || 'Unknown error'}. Please try again or contact support.`,
                    { bookingError: response.error }
                );
            }
        } catch (error: any) {
            setChatState(ChatState.IDLE);
            addMessage(
                'bot',
                `❌ Booking failed: ${error.message}. Please try again.`,
                { bookingError: error.message }
            );
        }
    };

    const handleCancelBooking = () => {
        setSelectedSlot(null);
        setChatState(ChatState.IDLE);
        addMessage('bot', 'Booking cancelled. Let me know if you\'d like to try a different time!');
    };

    const formatDateTime = (isoString: string) => {
        const date = new Date(isoString);
        const dateStr = date.toLocaleDateString('en-US', {
            weekday: 'long',
            month: 'long',
            day: 'numeric',
        });
        const timeStr = date.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true,
        });
        return { dateStr, timeStr };
    };

    return (
        <div className="flex flex-col h-[600px] bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
            {/* Header */}
            <div className="p-4 border-b border-slate-100 bg-gradient-to-r from-blue-50 to-indigo-50">
                <h2 className="font-semibold text-slate-800 flex items-center gap-2">
                    <Bot size={20} className="text-blue-600" />
                    Smart Scheduling Assistant
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                    Book appointments with natural language
                </p>
            </div>

            {/* Messages */}
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg, idx) => (
                    <div
                        key={idx}
                        className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                    >
                        <div
                            className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${msg.role === 'user'
                                    ? 'bg-slate-200 text-slate-600'
                                    : 'bg-blue-100 text-blue-600'
                                }`}
                        >
                            {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                        </div>

                        <div className={`max-w-[75%] ${msg.role === 'user' ? 'items-end' : 'items-start'} flex flex-col gap-2`}>
                            <div
                                className={`p-3 rounded-2xl text-sm leading-relaxed ${msg.role === 'user'
                                        ? 'bg-slate-100 text-slate-800 rounded-tr-none'
                                        : 'bg-blue-50 text-slate-800 rounded-tl-none border border-blue-100'
                                    }`}
                            >
                                {msg.content}

                                {msg.bookingSuccess && (
                                    <div className="mt-2 flex items-center gap-2 text-green-600">
                                        <CheckCircle size={16} />
                                        <span className="text-xs font-medium">Booking Confirmed</span>
                                    </div>
                                )}

                                {msg.bookingError && (
                                    <div className="mt-2 flex items-center gap-2 text-red-600">
                                        <XCircle size={16} />
                                        <span className="text-xs font-medium">Booking Failed</span>
                                    </div>
                                )}
                            </div>

                            {/* Slot Selector */}
                            {msg.slots && chatState === ChatState.SHOWING_SLOTS && (
                                <div className="w-full">
                                    <SlotSelector
                                        slots={msg.slots}
                                        onSelectSlot={handleSlotSelection}
                                        selectedSlot={selectedSlot}
                                    />
                                </div>
                            )}

                            {/* Confirmation Buttons */}
                            {msg.showConfirmation && chatState === ChatState.CONFIRMING_BOOKING && (
                                <div className="flex gap-2">
                                    <button
                                        onClick={handleConfirmBooking}
                                        className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors flex items-center gap-2"
                                    >
                                        <CheckCircle size={16} />
                                        Confirm Booking
                                    </button>
                                    <button
                                        onClick={handleCancelBooking}
                                        className="px-4 py-2 bg-slate-200 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-300 transition-colors flex items-center gap-2"
                                    >
                                        <XCircle size={16} />
                                        Cancel
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {/* Loading State */}
                {(chatState === ChatState.LOADING_SLOTS || chatState === ChatState.BOOKING) && (
                    <div className="flex gap-3">
                        <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 bg-blue-100 text-blue-600">
                            <Loader2 size={16} className="animate-spin" />
                        </div>
                        <div className="p-3 rounded-2xl rounded-tl-none bg-blue-50 border border-blue-100 text-sm text-slate-600">
                            <div className="flex items-center gap-2">
                                <Loader2 size={14} className="animate-spin" />
                                Processing...
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Input */}
            <div className="p-4 border-t border-slate-100 bg-slate-50/50">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                        placeholder="Type your message..."
                        disabled={chatState !== ChatState.IDLE}
                        className="flex-1 px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-slate-100 disabled:cursor-not-allowed text-sm"
                    />
                    <button
                        onClick={handleSendMessage}
                        disabled={!input.trim() || chatState !== ChatState.IDLE}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-slate-300 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                        <Send size={18} />
                    </button>
                </div>
                <p className="text-xs text-slate-400 mt-2">
                    Try: "I need an appointment tomorrow" or "Schedule with my doctor next week"
                </p>
            </div>
        </div>
    );
};

export default Chatbot;
