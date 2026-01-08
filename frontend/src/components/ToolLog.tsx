import { CheckCircle2, Clock, Terminal, XCircle } from "lucide-react";
import React from "react";

export interface ToolLogEntry {
	tool: string;
	status: "called" | "success" | "failed" | "skipped";
	args: any;
	timestamp: string;
}

interface ToolLogProps {
	logs: ToolLogEntry[];
}

const ToolLog: React.FC<ToolLogProps> = ({ logs }) => {
	const scrollRef = React.useRef<HTMLDivElement>(null);

	React.useEffect(() => {
		if (scrollRef.current)
			scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
	}, [logs]);

	return (
		<div className="flex flex-col h-[300px] bg-slate-900 rounded-2xl shadow-lg border border-slate-800 overflow-hidden text-slate-300 font-mono text-xs">
			<div className="p-3 border-b border-slate-800 bg-slate-950 flex items-center justify-between">
				<h2 className="font-semibold flex items-center gap-2 text-slate-100">
					<Terminal size={14} className="text-emerald-400" />
					System Internals & Tool Logs
				</h2>
				<span className="bg-slate-800 px-2 py-0.5 rounded text-[10px] text-slate-400">
					LIVE
				</span>
			</div>

			<div ref={scrollRef} className="flex-1 overflow-y-auto p-3 space-y-2">
				{logs.length === 0 && (
					<div className="text-slate-600 italic">
						Waiting for agent actions...
					</div>
				)}
				{logs.map((log, idx) => (
					<div key={idx} className="border-l-2 border-slate-700 pl-3 py-1">
						<div className="flex items-center gap-2 mb-1">
							<span className="text-blue-400 font-bold">{log.tool}()</span>
							{log.status === "success" && (
								<CheckCircle2 size={10} className="text-emerald-500" />
							)}
							{log.status === "failed" && (
								<XCircle size={10} className="text-red-500" />
							)}
							{log.status === "called" && (
								<Clock size={10} className="text-amber-500" />
							)}
							<span className="text-slate-500 ml-auto">{log.timestamp}</span>
						</div>
						<div className="bg-slate-950 p-2 rounded overflow-x-auto">
							<pre className="text-slate-400">
								{JSON.stringify(log.args, null, 2)}
							</pre>
						</div>
					</div>
				))}
			</div>
		</div>
	);
};

export default ToolLog;
