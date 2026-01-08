import axios from "axios";
import { Upload, FileImage, CheckCircle, AlertCircle, Pill } from "lucide-react";
import { useState } from "react";

interface PrescriptionUploadProps {
    authToken: string;
}

interface ExtractedData {
    upload_id: string;
    doctor_name: string;
    doctor_id: string | null;
    medications: Array<{
        drug_name: string;
        slots: string[];
    }>;
}

export default function PrescriptionUpload({ authToken }: PrescriptionUploadProps) {
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState("");
    const [extractedData, setExtractedData] = useState<ExtractedData | null>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setError("");
        setExtractedData(null);

        if (e.target.files && e.target.files[0]) {
            const selectedFile = e.target.files[0];

            // Validate file type
            const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'application/pdf'];
            if (!validTypes.includes(selectedFile.type)) {
                setError("Please upload a PNG, JPG, or PDF file");
                return;
            }

            // Validate file size (5MB)
            if (selectedFile.size > 5 * 1024 * 1024) {
                setError("File size must be less than 5MB");
                return;
            }

            setFile(selectedFile);
        }
    };

    const handleUpload = async () => {
        if (!file) {
            setError("Please select a file first");
            return;
        }

        setUploading(true);
        setError("");

        try {
            const formData = new FormData();
            formData.append("file", file);

            const response = await axios.post(
                "http://localhost:8000/api/upload_prescription",
                formData,
                {
                    headers: {
                        Authorization: `Bearer ${authToken}`,
                        "Content-Type": "multipart/form-data",
                    },
                }
            );

            setExtractedData(response.data);
            setFile(null);
        } catch (err: any) {
            console.error("Upload error:", err);
            if (err.response?.data?.detail) {
                setError(err.response.data.detail);
            } else {
                setError("Failed to upload prescription. Please try again.");
            }
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="space-y-6">
            {/* Upload Section */}
            <div className="bg-white rounded-xl shadow-md border border-slate-200 p-6">
                <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
                    <Upload size={24} className="text-blue-600" />
                    Upload Prescription
                </h2>

                <div className="space-y-4">
                    {/* File Input */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                            Select prescription image or PDF
                        </label>
                        <input
                            type="file"
                            accept="image/png,image/jpeg,image/jpg,application/pdf"
                            onChange={handleFileChange}
                            className="w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                        />
                    </div>

                    {/* Selected File Preview */}
                    {file && (
                        <div className="flex items-center gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                            <FileImage size={20} className="text-blue-600" />
                            <span className="text-sm text-slate-700 flex-1">{file.name}</span>
                            <span className="text-xs text-slate-500">
                                {(file.size / 1024 / 1024).toFixed(2)} MB
                            </span>
                        </div>
                    )}

                    {/* Error Message */}
                    {error && (
                        <div className="p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2 text-red-700 text-sm">
                            <AlertCircle size={18} className="flex-shrink-0 mt-0.5" />
                            <span>{error}</span>
                        </div>
                    )}

                    {/* Upload Button */}
                    <button
                        onClick={handleUpload}
                        disabled={!file || uploading}
                        className="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 active:scale-98 transition-all shadow-lg shadow-blue-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {uploading ? "Processing..." : "Upload & Extract"}
                    </button>
                </div>
            </div>

            {/* Extracted Data Display */}
            {extractedData && (
                <div className="bg-white rounded-xl shadow-md border border-slate-200 p-6">
                    <div className="flex items-center gap-2 mb-4">
                        <CheckCircle size={24} className="text-green-600" />
                        <h2 className="text-xl font-bold text-slate-900">Extracted Data</h2>
                    </div>

                    {/* Doctor Info */}
                    <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                        <h3 className="text-sm font-semibold text-green-900 mb-2">
                            Doctor Information
                        </h3>
                        <p className="text-slate-700">
                            <span className="font-medium">Name:</span> {extractedData.doctor_name}
                        </p>
                        {extractedData.doctor_id && (
                            <p className="text-slate-700">
                                <span className="font-medium">ID:</span> {extractedData.doctor_id}
                            </p>
                        )}
                    </div>

                    {/* Medications */}
                    <div>
                        <h3 className="text-sm font-semibold text-slate-900 mb-3 flex items-center gap-2">
                            <Pill size={18} className="text-blue-600" />
                            Medications ({extractedData.medications.length})
                        </h3>
                        <div className="space-y-3">
                            {extractedData.medications.map((med, index) => (
                                <div
                                    key={index}
                                    className="p-4 bg-slate-50 border border-slate-200 rounded-lg"
                                >
                                    <p className="font-medium text-slate-900 mb-2">{med.drug_name}</p>
                                    <div className="flex gap-2">
                                        {med.slots.map((slot) => (
                                            <span
                                                key={slot}
                                                className="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-semibold rounded-full capitalize"
                                            >
                                                {slot}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
