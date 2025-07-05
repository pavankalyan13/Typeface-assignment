import axios from 'axios';
import { FileMetadata, FileUploadResponse } from './types';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001/api';

export const uploadFile = async (formData: FormData): Promise<FileUploadResponse> => {
    try {
        const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    } catch (err: any) {
        throw new Error(err.response?.data?.detail || 'Upload failed');
    }
};

export const getFiles = async (): Promise<FileMetadata[]> => {
    try {
        const response = await axios.get(`${API_BASE_URL}/files`);
        return response.data;
    } catch (err: any) {
        throw new Error(err.response?.data?.detail || 'Failed to fetch files');
    }
};

export const downloadFile = async (fileId: string, filename: string): Promise<void> => {
    try {
        const response = await axios.get(`${API_BASE_URL}/download/${fileId}`, {
            responseType: 'blob',
        });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    } catch (err: any) {
        throw new Error(err.response?.data?.detail || 'Download failed');
    }
};

export const downloadFileForView = async (fileId: string): Promise<Blob> => {
    try {
        const response = await axios.get(`${API_BASE_URL}/download/${fileId}`, {
            responseType: 'blob',
        });
        return response.data;
    } catch (err: any) {
        throw new Error(err.response?.data?.detail || 'Failed to fetch file content');
    }
};