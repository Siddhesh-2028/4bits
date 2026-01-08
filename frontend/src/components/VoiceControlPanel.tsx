import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Activity, Volume2 } from 'lucide-react';

interface VoiceControlPanelProps {
    onTranscript: (text: string) => void;
    isProcessing: boolean;
}

const VoiceControlPanel: React.FC<VoiceControlPanelProps> = ({ onTranscript, isProcessing }) => {
    const [isListening, setIsListening] = useState(false);
    const [interimText, setInterimText] = useState('');
    const recognitionRef = useRef<any>(null);

    useEffect(() => {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
            recognitionRef.current = new SpeechRecognition();
            recognitionRef.current.continuous = true; // Keep listening
            recognitionRef.current.interimResults = true;
            recognitionRef.current.lang = 'en-US';

            recognitionRef.current.onresult = (event: any) => {
                let finalTranscript = '';
                let interimTranscript = '';

                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    } else {
                        interimTranscript += event.results[i][0].transcript;
                    }
                }

                if (finalTranscript) {
                    onTranscript(finalTranscript);
                    setInterimText('');
                }
                if (interimTranscript) {
                    setInterimText(interimTranscript);
                }
            };

            recognitionRef.current.onerror = (event: any) => {
                console.error("Speech recognition error", event.error);
                if (event.error === 'not-allowed') {
                    setIsListening(false);
                }
            };

            recognitionRef.current.onend = () => {
                // Auto-restart if we think we should still be listening, 
                // but for this button-controlled demo, we verify state
                if (isListening) {
                    try {
                        recognitionRef.current.start();
                    } catch (e) {
                        // ignore
                    }
                }
            }
        } else {
            alert("Web Speech API not supported in this browser.");
        }

        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.stop();
            }
        };
    }, []);

    const toggleListening = () => {
        if (isListening) {
            recognitionRef.current?.stop();
            setIsListening(false);
        } else {
            recognitionRef.current?.start();
            setIsListening(true);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center p-6 bg-white rounded-2xl shadow-sm border border-slate-100">
            <div className="relative mb-6">
                {isListening && (
                    <div className="absolute inset-0 bg-blue-100 rounded-full animate-pulse-ring -z-10"></div>
                )}
                <button
                    onClick={toggleListening}
                    className={`w-20 h-20 flex items-center justify-center rounded-full transition-all duration-300 shadow-lg ${isListening
                            ? 'bg-red-500 hover:bg-red-600 text-white shadow-red-200'
                            : 'bg-blue-600 hover:bg-blue-700 text-white shadow-blue-200'
                        }`}
                >
                    {isListening ? <MicOff size={32} /> : <Mic size={32} />}
                </button>
            </div>

            <div className="text-center space-y-2">
                <h3 className="text-lg font-semibold text-slate-800">
                    {isListening ? "Listening..." : "Tap to Speak"}
                </h3>
                <p className="text-sm text-slate-500 h-6">
                    {interimText || (isProcessing ? "Processing..." : "Ready")}
                </p>
            </div>
        </div>
    );
};

export default VoiceControlPanel;
