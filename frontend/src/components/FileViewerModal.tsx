import React, { useState, useEffect } from 'react';
import { ClipLoader } from 'react-spinners';
import * as api from '../api';
import { FileMetadata } from '../types';

interface FileViewerModalProps {
    file: FileMetadata | null;
    onClose: () => void;
}

const FileViewerModal: React.FC<FileViewerModalProps> = ({ file, onClose }) => {
    const [content, setContent] = useState<string | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!file) return;

        const fetchFileContent = async () => {
            setLoading(true);
            try {
                const response = await api.downloadFileForView(file.file_id);
                const ext = file.filename.split('.').pop()?.toLowerCase();
                if (['txt', 'json'].includes(ext || '')) {
                    const text = await response.text();
                    setContent(text);
                } else if (['jpg', 'png'].includes(ext || '')) {
                    const url = window.URL.createObjectURL(response);
                    setContent(url);
                } else {
                    setError('File type not supported for viewing');
                }
            } catch (err: any) {
                setError(err.message || 'Failed to load file content');
            } finally {
                setLoading(false);
            }
        };

        fetchFileContent();

        return () => {
            if (content && content.startsWith('blob:')) {
                window.URL.revokeObjectURL(content);
            }
        };
    }, [file]);

    if (!file) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-auto">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-semibold text-gray-800">{file.filename}</h2>
                    <button
                        onClick={onClose}
                        className="text-gray-500 hover:text-gray-700 font-bold"
                    >
                        ✕
                    </button>
                </div>
                {loading ? (
                    <div className="flex justify-center">
                        <ClipLoader color="#4B5563" size={40} />
                    </div>
                ) : error ? (
                    <p className="text-red-500 text-sm">{error}</p>
                ) : content ? (
                    <div className="mt-4">
                        {['txt', 'json'].includes(file.filename.split('.').pop()?.toLowerCase() || '') ? (
                            <textarea
                                className="w-full h-96 p-4 border rounded-lg text-gray-700"
                                value={content}
                                readOnly
                            />
                        ) : (
                            <img
                                src={content}
                                alt={file.filename}
                                className="max-w-full h-auto rounded-lg"
                            />
                        )}
                    </div>
                ) : (
                    <p className="text-gray-500">No content available</p>
                )}
                <div className="mt-4 flex justify-end">
                    <button
                        onClick={() => api.downloadFile(file.file_id, file.filename)}
                        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                        Download
                    </button>
                </div>
            </div>
        </div>
    );
};

export default FileViewerModal;