import React, { useState, ChangeEvent, DragEvent } from 'react';
import { toast } from 'react-toastify';
import { ClipLoader } from 'react-spinners';
import * as api from '../api';
import { FileUploadResponse } from '../types';

interface FileUploadProps {
    onUploadSuccess: () => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess }:any) => {
    const [file, setFile] = useState<File | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [uploading, setUploading] = useState<boolean>(false);
    const [isDragging, setIsDragging] = useState<boolean>(false);

    const handleFileChange = (selectedFile: File) => {
        const ext = selectedFile.name.split('.').pop()?.toLowerCase();
        if (!['txt', 'jpg', 'png', 'json'].includes(ext || '')) {
            setError('Only .txt, .jpg, .png, .json files are allowed');
            setFile(null);
        } else {
            setError(null);
            setFile(selectedFile);
        }
    };

    const onFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            handleFileChange(selectedFile);
        }
    };

    const onDragOver = (e: DragEvent<HTMLLabelElement>) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const onDragLeave = () => {
        setIsDragging(false);
    };

    const onDrop = (e: DragEvent<HTMLLabelElement>) => {
        e.preventDefault();
        setIsDragging(false);
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) {
            handleFileChange(droppedFile);
        }
    };

    const handleUpload = async () => {
        if (!file) {
            setError('Please select a file');
            toast.error('No file selected');
            return;
        }

        setUploading(true);
        try {
            const formData = new FormData();
            formData.append('file', file);
            const response = await api.uploadFile(formData);
            toast.success(`File "${response.filename}" uploaded successfully`);
            setError(null);
            setFile(null);
            onUploadSuccess();
        } catch (err: any) {
            const errorMessage = err.message || 'Upload failed';
            setError(errorMessage);
            toast.error(errorMessage);
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="mb-8">
            <h2 className="text-2xl font-semibold mb-4 text-gray-700">Upload File</h2>
            <div className="flex items-center justify-center w-full">
                <label
                    htmlFor="dropzone-file"
                    className={`flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer transition-all ${
                        isDragging
                            ? 'bg-gray-200 border-gray-400'
                            : 'bg-gray-50 border-gray-300 hover:bg-gray-100'
                    }`}
                    onDragOver={onDragOver}
                    onDragLeave={onDragLeave}
                    onDrop={onDrop}
                >
                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                        {uploading ? (
                            <ClipLoader color="#4B5563" size={40} className="mb-4" />
                        ) : (
                            <svg
                                className="w-8 h-8 mb-4 text-gray-500"
                                aria-hidden="true"
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 20 16"
                            >
                                <path
                                    stroke="currentColor"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="2"
                                    d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"
                                />
                            </svg>
                        )}
                        <p className="mb-2 text-sm text-gray-500">
                            <span className="font-semibold">Click to upload</span> or drag and drop
                        </p>
                        <p className="text-xs text-gray-500">TXT, JPG, PNG, JSON (MAX. 10MB)</p>
                    </div>
                    <input
                        id="dropzone-file"
                        type="file"
                        accept=".txt,.jpg,.png,.json"
                        onChange={onFileInputChange}
                        className="hidden"
                        disabled={uploading}
                    />
                </label>
            </div>
            {file && (
                <div className="mt-4 flex items-center justify-between">
                    <span className="text-gray-600">{file.name}</span>
                    <button
                        onClick={handleUpload}
                        disabled={uploading}
                        className={`px-4 py-2 rounded text-white font-medium ${
                            uploading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-500 hover:bg-blue-600'
                        }`}
                    >
                        {uploading ? 'Uploading...' : 'Upload'}
                    </button>
                </div>
            )}
            {error && <p className="text-red-500 mt-2 text-sm">{error}</p>}
        </div>
    );
};

export default FileUpload;