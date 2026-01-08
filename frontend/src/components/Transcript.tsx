import { Bot, User } from "lucide-react";
import React from "react";

interface Message {
	role: "user" | "agent";
	content: string;
	timestamp: string;
}

interface TranscriptProps {
	messages: Message[];
}

const Transcript: React.FC<TranscriptProps> = ({ messages }) => {
	const scrollRef = React.useRef<HTMLDivElement>(null);

	React.useEffect(() => {
		if (scrollRef.current) {
			scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
		}
	}, [messages]);

	return (
		<div className="flex flex-col h-[500px] bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
			<div className="p-4 border-b border-slate-100 bg-slate-50/50">
				<h2 className="font-semibold text-slate-800 flex items-center gap-2">
					<Bot size={18} className="text-blue-600" />
					Live Transcript
				</h2>
			</div>

			<div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
				{messages.length === 0 && (
					<div className="text-center text-slate-400 mt-20 text-sm">
						No conversation yet. Tap the microphone to start.
					</div>
				)}

				{messages.map((msg, idx) => (
					<div
						key={idx}
						className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}
					>
						<div
							className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
								msg.role === "user"
									? "bg-slate-200 text-slate-600"
									: "bg-blue-100 text-blue-600"
							}`}
						>
							{msg.role === "user" ? <User size={16} /> : <Bot size={16} />}
						</div>

						<div
							className={`max-w-[80%] p-3 rounded-2xl text-sm leading-relaxed ${
								msg.role === "user"
									? "bg-slate-100 text-slate-800 rounded-tr-none"
									: "bg-blue-50 text-slate-800 rounded-tl-none border border-blue-100"
							}`}
						>
							{msg.content}
						</div>
					</div>
				))}
			</div>
		</div>
	);
};

export default Transcript;
