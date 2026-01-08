import axios from "axios";
import { Activity, HeartPulse, LogOut, ShieldCheck, FileUp, MessageSquare } from "lucide-react";
import { useEffect, useState } from "react";
import Auth from "./components/Auth";
import Chatbot from "./components/Chatbot";
import PrescriptionUpload from "./components/PrescriptionUpload";
import ToolLog, { ToolLogEntry } from "./components/ToolLog";
import Transcript from "./components/Transcript";
import VoiceControlPanel from "./components/VoiceControlPanel";

interface ChatMessage {
	role: "user" | "agent";
	content: string;
	timestamp: string;
}

interface UserData {
	user_id: string;
	username: string;
	name: string;
}

function App() {
	const [isAuthenticated, setIsAuthenticated] = useState(false);
	const [userData, setUserData] = useState<UserData | null>(null);
	const [authToken, setAuthToken] = useState<string | null>(null);
	const [activeTab, setActiveTab] = useState<'voice' | 'chatbot' | 'prescription'>('chatbot');
	const [messages, setMessages] = useState<ChatMessage[]>([]);
	const [logs, setLogs] = useState<ToolLogEntry[]>([]);
	const [isProcessing, setIsProcessing] = useState(false);

	// Check for existing auth token on mount
	useEffect(() => {
		const token = localStorage.getItem("vita_token");
		const userId = localStorage.getItem("vita_user_id");
		const username = localStorage.getItem("vita_username");
		const name = localStorage.getItem("vita_name");

		if (token && userId && username && name) {
			setAuthToken(token);
			setUserData({ user_id: userId, username, name });
			setIsAuthenticated(true);
		}
	}, []);

	const handleAuthSuccess = (token: string, user: UserData) => {
		setAuthToken(token);
		setUserData(user);
		setIsAuthenticated(true);
	};

	const handleLogout = () => {
		localStorage.removeItem("vita_token");
		localStorage.removeItem("vita_user_id");
		localStorage.removeItem("vita_username");
		localStorage.removeItem("vita_name");
		setAuthToken(null);
		setUserData(null);
		setIsAuthenticated(false);
		setMessages([]);
		setLogs([]);
		setActiveTab('chatbot');
	};

	// Simple TTS
	const speak = (text: string) => {
		const utterance = new SpeechSynthesisUtterance(text);
		window.speechSynthesis.speak(utterance);
	};

	const handleTranscript = async (text: string) => {
		const userMsg: ChatMessage = {
			role: "user",
			content: text,
			timestamp: new Date().toLocaleTimeString(),
		};
		setMessages((prev) => [...prev, userMsg]);
		setIsProcessing(true);

		try {
			const response = await axios.post(
				"http://localhost:8000/api/chat",
				{
					message: text,
					conversation_history: [],
				},
				{
					headers: { Authorization: `Bearer ${authToken}` }
				}
			);

			const data = response.data;

			const agentMsg: ChatMessage = {
				role: "agent",
				content: data.response,
				timestamp: new Date().toLocaleTimeString(),
			};
			setMessages((prev) => [...prev, agentMsg]);

			if (data.logs && data.logs.length > 0) {
				const newLogs = data.logs.map((l: any) => ({
					...l,
					timestamp: new Date().toLocaleTimeString(),
				}));
				setLogs((prevLogs) => [...prevLogs, ...newLogs]);
			}

			speak(data.response);
		} catch (error) {
			console.error("API Error", error);
			const errorMsg: ChatMessage = {
				role: "agent",
				content: "I'm having trouble connecting to the server. Please ensure you are logged in and the backend is running.",
				timestamp: new Date().toLocaleTimeString(),
			};
			setMessages((prev) => [...prev, errorMsg]);
		} finally {
			setIsProcessing(false);
		}
	};

	if (!isAuthenticated) {
		return <Auth onAuthSuccess={handleAuthSuccess} />;
	}

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
							<h1 className="text-xl font-bold text-slate-900 tracking-tight">
								VITA-Care
							</h1>
							<p className="text-xs text-slate-500 font-medium">
								Autonomous Care Coordinator
							</p>
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
						<button
							onClick={handleLogout}
							className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition-colors border border-red-100"
						>
							<LogOut size={14} />
							Logout
						</button>
					</div>
				</div>
			</header>

			{/* Main Content */}
			<main className="flex-1 max-w-6xl mx-auto w-full p-6 space-y-6">
				{/* Tabs */}
				<div className="flex gap-2 bg-white p-2 rounded-lg shadow-sm border border-slate-200">
					<button
						onClick={() => setActiveTab('voice')}
						className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-all flex items-center justify-center gap-2 ${activeTab === 'voice'
							? 'bg-blue-600 text-white shadow-md'
							: 'bg-slate-100 text-slate-600 hover:bg-slate-200'
							}`}
					>
						<Activity size={20} />
						Voice Assistant
					</button>
					<button
						onClick={() => setActiveTab('chatbot')}
						className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-all flex items-center justify-center gap-2 ${activeTab === 'chatbot'
							? 'bg-blue-600 text-white shadow-md'
							: 'bg-slate-100 text-slate-600 hover:bg-slate-200'
							}`}
					>
						<MessageSquare size={20} />
						Smart Scheduling
					</button>
					<button
						onClick={() => setActiveTab('prescription')}
						className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-all flex items-center justify-center gap-2 ${activeTab === 'prescription'
							? 'bg-blue-600 text-white shadow-md'
							: 'bg-slate-100 text-slate-600 hover:bg-slate-200'
							}`}
					>
						<FileUp size={20} />
						Upload Prescription
					</button>
				</div>

				{/* Tab Content */}
				{activeTab === 'voice' ? (
					<div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
						{/* Left Column: Voice & Transcript (7 cols) */}
						<div className="lg:col-span-7 space-y-6">
							<VoiceControlPanel
								onTranscript={handleTranscript}
								isProcessing={isProcessing}
							/>
							<Transcript messages={messages} />
						</div>

						{/* Right Column: System State (5 cols) */}
						<div className="lg:col-span-5 space-y-6">
							{/* Dashboard / Patient Context */}
							<div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100">
								<h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">
									Patient Context
								</h3>
								<div className="space-y-3">
									<div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg border border-slate-100">
										<span className="text-sm text-slate-500">Name</span>
										<span className="font-medium text-slate-800">
											{userData?.name}
										</span>
									</div>
									<div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg border border-slate-100">
										<span className="text-sm text-slate-500">Username</span>
										<span className="font-medium text-slate-800">
											@{userData?.username}
										</span>
									</div>
									<div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg border border-slate-100">
										<span className="text-sm text-slate-500">User ID</span>
										<span className="font-mono text-xs text-slate-600 bg-slate-100 px-2 py-1 rounded">
											{userData?.user_id.substring(0, 8)}...
										</span>
									</div>
								</div>
							</div>

							<ToolLog logs={logs} />

							<div className="p-4 bg-amber-50 border border-amber-100 rounded-xl text-amber-800 text-xs leading-relaxed">
								<strong>⚠️ Medical Disclaimer:</strong> VITA-Care is for coordination
								only. It does not provide medical advice or diagnosis. In
								emergencies, call 911.
							</div>
						</div>
					</div>
				) : activeTab === 'chatbot' ? (
					/* Chatbot Tab */
					<div className="max-w-5xl mx-auto">
						<Chatbot
							authToken={authToken!}
							userId={userData!.user_id}
							userName={userData!.name}
						/>
					</div>
				) : (
					/* Prescription Upload Tab */
					<div className="max-w-4xl mx-auto">
						<PrescriptionUpload authToken={authToken!} />
					</div>
				)}
			</main>
		</div>
	);
}

export default App;
