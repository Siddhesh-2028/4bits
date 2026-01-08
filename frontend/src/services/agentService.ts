/**
 * Agent Service
 * API service layer for backend agent endpoints
 */

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// TypeScript Interfaces
export interface AppointmentSlot {
	datetime: string;
	doctor_name: string;
	doctor_id: string;
}

export interface BookingResponse {
	success: boolean;
	booking?: {
		schedule_id: string;
		patient_id: string;
		doctor_id: string;
		appointment_time: string;
		status: string;
	};
	status: string;
	message: string;
	error?: string;
}

export interface ScheduleSuggestResponse {
	success: boolean;
	slots: AppointmentSlot[];
	message: string;
}

export interface CancelBookingResponse {
	success: boolean;
	message: string;
	status: string;
	error?: string;
}

/**
 * Create axios instance with auth headers
 */
const createAuthClient = (token: string): AxiosInstance => {
	return axios.create({
		baseURL: API_BASE_URL,
		headers: {
			'Authorization': `Bearer ${token}`,
			'Content-Type': 'application/json',
		},
	});
};

/**
 * Suggest appointment slots based on natural language input
 */
export const suggestSlots = async (
	userInput: string,
	patientId: string,
	token: string
): Promise<ScheduleSuggestResponse> => {
	try {
		const client = createAuthClient(token);
		const response = await client.post('/api/agents/schedule/suggest', {
			user_input: userInput,
			patient_id: patientId,
		});

		return response.data;
	} catch (error: any) {
		console.error('Error suggesting slots:', error);
		throw new Error(
			error.response?.data?.detail || 'Failed to fetch appointment slots'
		);
	}
};

/**
 * Book an appointment slot
 */
export const bookAppointment = async (
	patientId: string,
	doctorId: string,
	appointmentTime: string,
	token: string,
	uploadId?: string
): Promise<BookingResponse> => {
	try {
		const client = createAuthClient(token);
		const response = await client.post('/api/agents/booking/create', {
			patient_id: patientId,
			doctor_id: doctorId,
			appointment_time: appointmentTime,
			upload_id: uploadId,
		});

		return response.data;
	} catch (error: any) {
		console.error('Error booking appointment:', error);
		throw new Error(
			error.response?.data?.detail || 'Failed to book appointment'
		);
	}
};

/**
 * Cancel an existing appointment
 */
export const cancelAppointment = async (
	scheduleId: string,
	token: string
): Promise<CancelBookingResponse> => {
	try {
		const client = createAuthClient(token);
		const response = await client.post('/api/agents/booking/cancel', {
			schedule_id: scheduleId,
		});

		return response.data;
	} catch (error: any) {
		console.error('Error cancelling appointment:', error);
		throw new Error(
			error.response?.data?.detail || 'Failed to cancel appointment'
		);
	}
};

/**
 * Check agent system health
 */
export const checkAgentHealth = async (token: string): Promise<any> => {
	try {
		const client = createAuthClient(token);
		const response = await client.get('/api/agents/health');
		return response.data;
	} catch (error: any) {
		console.error('Error checking agent health:', error);
		throw new Error('Agent system unavailable');
	}
};
