/**
 * SlotSelector Component
 * Displays and allows selection of appointment slots
 */

import { Calendar, Clock } from 'lucide-react';
import React from 'react';
import { AppointmentSlot } from '../services/agentService';

interface SlotSelectorProps {
    slots: AppointmentSlot[];
    onSelectSlot: (slot: AppointmentSlot) => void;
    selectedSlot: AppointmentSlot | null;
}

const SlotSelector: React.FC<SlotSelectorProps> = ({
    slots,
    onSelectSlot,
    selectedSlot,
}) => {
    const formatDateTime = (isoString: string) => {
        const date = new Date(isoString);
        const dateStr = date.toLocaleDateString('en-US', {
            weekday: 'short',
            month: 'short',
            day: 'numeric',
        });
        const timeStr = date.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true,
        });
        return { dateStr, timeStr };
    };

    if (slots.length === 0) {
        return (
            <div className="p-4 bg-slate-50 rounded-lg text-center text-slate-500 text-sm">
                No available slots at the moment.
            </div>
        );
    }

    return (
        <div className="space-y-3">
            <p className="text-sm font-medium text-slate-700">
                Available appointment slots:
            </p>
            {slots.map((slot, index) => {
                const { dateStr, timeStr } = formatDateTime(slot.datetime);
                const isSelected =
                    selectedSlot?.datetime === slot.datetime &&
                    selectedSlot?.doctor_id === slot.doctor_id;

                return (
                    <button
                        key={`${slot.doctor_id}-${slot.datetime}-${index}`}
                        onClick={() => onSelectSlot(slot)}
                        className={`w-full p-4 rounded-xl border-2 transition-all duration-200 text-left ${isSelected
                                ? 'border-blue-500 bg-blue-50 shadow-md'
                                : 'border-slate-200 bg-white hover:border-blue-300 hover:shadow-sm'
                            }`}
                    >
                        <div className="flex items-start justify-between gap-3">
                            <div className="flex-1">
                                <div className="font-semibold text-slate-800 mb-1">
                                    {slot.doctor_name}
                                </div>
                                <div className="flex items-center gap-3 text-sm text-slate-600">
                                    <div className="flex items-center gap-1.5">
                                        <Calendar size={14} />
                                        <span>{dateStr}</span>
                                    </div>
                                    <div className="flex items-center gap-1.5">
                                        <Clock size={14} />
                                        <span>{timeStr}</span>
                                    </div>
                                </div>
                            </div>
                            {isSelected && (
                                <div className="flex-shrink-0 w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                                    <svg
                                        className="w-4 h-4 text-white"
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                    >
                                        <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth={2}
                                            d="M5 13l4 4L19 7"
                                        />
                                    </svg>
                                </div>
                            )}
                        </div>
                    </button>
                );
            })}
        </div>
    );
};

export default SlotSelector;
