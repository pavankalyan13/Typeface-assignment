export interface FileMetadata {
    file_id: string;
    filename: string;
    upload_date: string;
}

export interface FileUploadResponse {
    file_id: string;
    filename: string;
    size: number;
    detail?: string;
}