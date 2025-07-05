import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { ClipLoader } from 'react-spinners';
import * as api from '../api';
import FileItem from './FileItem';
import { FileMetadata } from '../types';

interface FileListProps {
    refresh: boolean;
    onViewFile: (file: FileMetadata) => void;
}

const FileList: React.FC<FileListProps> = ({ refresh, onViewFile }) => {
    const [files, setFiles] = useState<FileMetadata[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState<boolean>(false);

    useEffect(() => {
        const fetchFiles = async () => {
            setLoading(true);
            try {
                const response = await api.getFiles();
                setFiles(response);
                setError(null);
            } catch (err: any) {
                const errorMessage = err.message || 'Failed to load files';
                setError(errorMessage);
                toast.error(errorMessage);
            } finally {
                setLoading(false);
            }
        };
        fetchFiles();
    }, [refresh]);

    return (
        <div>
            <h2 className="text-2xl font-semibold mb-4 text-gray-700">Files</h2>
            {loading ? (
                <div className="flex justify-center">
                    <ClipLoader color="#4B5563" size={40} />
                </div>
            ) : error ? (
                <p className="text-red-500 mb-2 text-sm">{error}</p>
            ) : files.length === 0 ? (
                <p className="text-gray-500">No files available</p>
            ) : (
                <ul className="space-y-3">
                    {files.map((file) => (
                        <FileItem key={file.file_id} file={file} onViewFile={onViewFile} />
                    ))}
                </ul>
            )}
        </div>
    );
};

export default FileList;