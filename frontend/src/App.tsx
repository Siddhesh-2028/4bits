import React, { useState } from 'react';
import VoiceControlPanel from './components/VoiceControlPanel';
import Transcript from './components/Transcript';
import ToolLog, { ToolLogEntry } from './components/ToolLog';
import { Activity, HeartPulse, ShieldCheck } from 'lucide-react';
import axios from 'axios';

interface ChatMessage {
    role: 'user' | 'agent';
    content: string;
    timestamp: string;
}

function App() {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [logs, setLogs] = useState<ToolLogEntry[]>([]);
    const [isProcessing, setIsProcessing] = useState(false);

    // Simple TTS
    const speak = (text: string) => {
        const utterance = new SpeechSynthesisUtterance(text);
        // utterance.voice = window.speechSynthesis.getVoices().find(v => v.name.includes("Google US English")) || null;
        window.speechSynthesis.speak(utterance);
    };

    const handleTranscript = async (text: string) => {
        // 1. Add User Message
        const userMsg: ChatMessage = {
            role: 'user',
            content: text,
            timestamp: new Date().toLocaleTimeString()
        };
        setMessages(prev => [...prev, userMsg]);
        setIsProcessing(true);

        try {
            // 2. Call Backend
            const response = await axios.post('http://localhost:8000/api/chat', {
                message: text,
                conversation_history: [] // We could pass full history if needed
            });

            const data = response.data;

            // 3. Add Agent Message
            const agentMsg: ChatMessage = {
                role: 'agent',
                content: data.response,
                timestamp: new Date().toLocaleTimeString()
            };
            setMessages(prev => [...prev, agentMsg]);

            // 4. Update Logs
            if (data.logs && data.logs.length > 0) {
                const newLogs = data.logs.map((l: any) => ({
                    ...l,
                    timestamp: new Date().toLocaleTimeString()
                }));
                setLogs(prevLogs => [...prevLogs, ...newLogs]);
            }

            // 5. TTS
            speak(data.response);

        } catch (error) {
            console.error("API Error", error);
            const errorMsg: ChatMessage = {
                role: 'agent',
                content: "I'm having trouble connecting to the server. Please ensure the backend is running.",
                timestamp: new Date().toLocaleTimeString()
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900">
            {/* Header */}
            <header className="bg-white border-b border-slate-200 px-6 py-4 sticky top-0 z-50">
                <div className="max-w-6xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-white shadow-blue-200 shadow-lg">
                            <HeartPulse size={24} />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold text-slate-900 tracking-tight">VITA-Care</h1>
                            <p className="text-xs text-slate-500 font-medium">Autonomous Care Coordinator</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-1.5 px-3 py-1 bg-emerald-50 text-emerald-700 rounded-full text-xs font-semibold border border-emerald-100">
                            <ShieldCheck size={14} />
                            HIPAA Compliant Mode
                        </div>
                        <div className="flex items-center gap-1.5 px-3 py-1 bg-slate-100 text-slate-600 rounded-full text-xs font-medium">
                            <Activity size={14} />
                            v1.0.0-beta
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 max-w-6xl mx-auto w-full p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">

                {/* Left Column: Voice & Transcript (7 cols) */}
                <div className="lg:col-span-7 space-y-6">
                    <VoiceControlPanel onTranscript={handleTranscript} isProcessing={isProcessing} />
                    <Transcript messages={messages} />
                </div>

                {/* Right Column: System State (5 cols) */}
                <div className="lg:col-span-5 space-y-6">
                    {/* Dashboard / Patient Context Mock */}
                    <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100">
                        <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Patient Context</h3>
                        <div className="space-y-3">
                            <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg border border-slate-100">
                                <span className="text-sm text-slate-500">Name</span>
                                <span className="font-medium text-slate-800">Alice Smith (P001)</span>
                            </div>
                            <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg border border-slate-100">
                                <span className="text-sm text-slate-500">DOB</span>
                                <span className="font-medium text-slate-800">1985-04-12</span>
                            </div>
                            <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg border border-slate-100">
                                <span className="text-sm text-slate-500">Status</span>
                                <span className="text-xs font-bold text-emerald-600 bg-emerald-100 px-2 py-1 rounded">ACTIVE</span>
                            </div>
                        </div>
                    </div>

                    <ToolLog logs={logs} />

                    <div className="p-4 bg-amber-50 border border-amber-100 rounded-xl text-amber-800 text-xs leading-relaxed">
                        <strong>⚠️ Medical Disclaimer:</strong> VITA-Care is for coordination only. It does not provide medical advice or diagnosis. In emergencies, call 911.
                    </div>
                </div>

            </main>
        </div>
    );
}

export default App;
