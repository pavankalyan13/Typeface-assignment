import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import FileList from './components/FileList';
import FileViewerModal from './components/FileViewerModal';
import { FileMetadata } from './types';

const App: React.FC = () => {
    const [refresh, setRefresh] = useState<boolean>(false);
    const [selectedFile, setSelectedFile] = useState<FileMetadata | null>(null);

    // Trigger file list refresh after upload
    const handleUploadSuccess = () => {
        setRefresh(!refresh);
    };

    // Open modal for file viewing
    const handleViewFile = (file: FileMetadata) => {
        setSelectedFile(file);
    };

    // Close modal
    const handleCloseModal = () => {
        setSelectedFile(null);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-100 flex flex-col items-center p-6">
            <h1 className="text-4xl font-bold mb-8 text-gray-800">Dropbox Clone</h1>
            <div className="w-full max-w-3xl bg-white shadow-xl rounded-lg p-8">
                <FileUpload onUploadSuccess={handleUploadSuccess} />
                <FileList refresh={refresh} onViewFile={handleViewFile} />
                <FileViewerModal file={selectedFile} onClose={handleCloseModal} />
            </div>
        </div>
    );
};

export default App;