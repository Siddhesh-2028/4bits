import axios from "axios";
import { AlertCircle, HeartPulse, Lock, Mail, User } from "lucide-react";
import { useState } from "react";

interface AuthProps {
	onAuthSuccess: (token: string, userData: any) => void;
}

export default function Auth({ onAuthSuccess }: AuthProps) {
	const [isLogin, setIsLogin] = useState(true);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");

	// Form data
	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");
	const [name, setName] = useState("");
	const [phone, setPhone] = useState("");  // REQUIRED for signup
	const [email, setEmail] = useState("");

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setError("");
		setLoading(true);

		try {
			const endpoint = isLogin ? "/api/login" : "/api/register";
			const payload = isLogin
				? { username, password }
				: { username, password, name, phone, email };  // phone now included

			const response = await axios.post(
				`http://localhost:8000${endpoint}`,
				payload
			);

			const { access_token, user_id, username: userName, name: fullName } = response.data;

			// Store token in localStorage
			localStorage.setItem("vita_token", access_token);
			localStorage.setItem("vita_user_id", user_id);
			localStorage.setItem("vita_username", userName);
			localStorage.setItem("vita_name", fullName);

			// Notify parent component
			onAuthSuccess(access_token, {
				user_id,
				username: userName,
				name: fullName,
			});
		} catch (err: any) {
			console.error("Auth error:", err);
			if (err.response?.data?.detail) {
				setError(err.response.data.detail);
			} else {
				setError(
					isLogin
						? "Login failed. Please check your credentials."
						: "Registration failed. Please try again."
				);
			}
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center p-6">
			<div className="w-full max-w-md">
				{/* Logo/Header */}
				<div className="text-center mb-8">
					<div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-2xl shadow-lg shadow-blue-200 mb-4">
						<HeartPulse size={32} className="text-white" />
					</div>
					<h1 className="text-3xl font-bold text-slate-900 mb-2">
						VITA-Care
					</h1>
					<p className="text-slate-600">
						Voice-Integrated Task-Autonomous Care
					</p>
				</div>

				{/* Auth Card */}
				<div className="bg-white rounded-2xl shadow-xl border border-slate-100 p-8">
					<div className="flex gap-2 mb-6">
						<button
							onClick={() => {
								setIsLogin(true);
								setError("");
							}}
							className={`flex-1 py-2.5 rounded-lg font-semibold transition-all ${isLogin
								? "bg-blue-600 text-white shadow-md"
								: "bg-slate-100 text-slate-600 hover:bg-slate-200"
								}`}
						>
							Login
						</button>
						<button
							onClick={() => {
								setIsLogin(false);
								setError("");
							}}
							className={`flex-1 py-2.5 rounded-lg font-semibold transition-all ${!isLogin
								? "bg-blue-600 text-white shadow-md"
								: "bg-slate-100 text-slate-600 hover:bg-slate-200"
								}`}
						>
							Sign Up
						</button>
					</div>

					{error && (
						<div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2 text-red-700 text-sm">
							<AlertCircle size={18} className="flex-shrink-0 mt-0.5" />
							<span>{error}</span>
						</div>
					)}

					<form onSubmit={handleSubmit} className="space-y-4">
						{!isLogin && (
							<div>
								<label className="block text-sm font-medium text-slate-700 mb-1.5">
									Full Name
								</label>
								<div className="relative">
									<User
										size={18}
										className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
									/>
									<input
										type="text"
										value={name}
										onChange={(e) => setName(e.target.value)}
										className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
										placeholder="John Doe"
										required={!isLogin}
									/>
								</div>
							</div>
						)}

						<div>
							<label className="block text-sm font-medium text-slate-700 mb-1.5">
								Username
							</label>
							<div className="relative">
								<User
									size={18}
									className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
								/>
								<input
									type="text"
									value={username}
									onChange={(e) => setUsername(e.target.value)}
									className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
									placeholder="johndoe"
									required
								/>
							</div>
						</div>

						{!isLogin && (
							<div>
								<label className="block text-sm font-medium text-slate-700 mb-1.5">
									Mobile Number
								</label>
								<div className="relative">
									<User
										size={18}
										className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
									/>
									<input
										type="tel"
										value={phone}
										onChange={(e) => setPhone(e.target.value)}
										className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
										placeholder="+91 98765 43210"
										required={!isLogin}
										minLength={10}
										maxLength={15}
									/>
								</div>
								<p className="text-xs text-slate-500 mt-1">
									Required for account verification
								</p>
							</div>
						)}

						{!isLogin && (
							<div>
								<label className="block text-sm font-medium text-slate-700 mb-1.5">
									Email (Optional)
								</label>
								<div className="relative">
									<Mail
										size={18}
										className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
									/>
									<input
										type="email"
										value={email}
										onChange={(e) => setEmail(e.target.value)}
										className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
										placeholder="john@example.com"
									/>
								</div>
							</div>
						)}

						<div>
							<label className="block text-sm font-medium text-slate-700 mb-1.5">
								Password
							</label>
							<div className="relative">
								<Lock
									size={18}
									className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
								/>
								<input
									type="password"
									value={password}
									onChange={(e) => setPassword(e.target.value)}
									className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
									placeholder="••••••••"
									required
									minLength={6}
									maxLength={72}
								/>
							</div>
							{!isLogin && (
								<p className="text-xs text-slate-500 mt-1">
									6-72 characters
								</p>
							)}
						</div>

						<button
							type="submit"
							disabled={loading}
							className="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 active:scale-98 transition-all shadow-lg shadow-blue-200 disabled:opacity-50 disabled:cursor-not-allowed"
						>
							{loading
								? "Processing..."
								: isLogin
									? "Login"
									: "Create Account"}
						</button>
					</form>

					<div className="mt-6 p-4 bg-amber-50 border border-amber-100 rounded-lg text-xs text-amber-800 leading-relaxed">
						<strong>⚠️ Medical Disclaimer:</strong> VITA-Care is for
						coordination only. It does not provide medical advice or
						diagnosis.
					</div>
				</div>
			</div>
		</div>
	);
}
