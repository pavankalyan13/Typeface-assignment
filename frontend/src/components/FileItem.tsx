import React from 'react';
import { FileMetadata } from '../types';

interface FileItemProps {
    file: FileMetadata;
    onViewFile: (file: FileMetadata) => void;
}

const FileItem: React.FC<FileItemProps> = ({ file, onViewFile }) => {
    return (
        <li
            className="flex justify-between items-center p-3 bg-gray-50 hover:bg-gray-100 rounded-lg cursor-pointer transition-all shadow-sm"
            onClick={() => onViewFile(file)}
        >
            <span className="text-gray-800 font-medium">{file.filename}</span>
            <span className="text-gray-500 text-sm">
                {new Date(file.upload_date).toLocaleDateString()}
            </span>
        </li>
    );
};

export default FileItem;