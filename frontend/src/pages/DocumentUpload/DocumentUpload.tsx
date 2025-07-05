import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  LinearProgress,
} from '@mui/material';
import { CloudUpload as UploadIcon } from '@mui/icons-material';
import { useNotification } from '../../contexts/NotificationContext';

const DocumentUpload: React.FC = () => {
  const { showSuccess, showError } = useNotification();
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    documentType: '',
    courseCode: '',
    academicYear: '',
    semester: '',
  });

  const handleFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    const file = files[0];
    setIsUploading(true);

    // Simulate upload progress
    for (let i = 0; i <= 100; i += 10) {
      setUploadProgress(i);
      await new Promise(resolve => setTimeout(resolve, 200));
    }

    setIsUploading(false);
    showSuccess('Document uploaded successfully!');
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
        Upload Document
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Upload a new document to the university archive
      </Typography>

      <Paper
        sx={{
          p: 4,
          border: '2px dashed',
          borderColor: 'primary.main',
          textAlign: 'center',
          cursor: 'pointer',
          mb: 4,
        }}
        onClick={() => document.getElementById('file-input')?.click()}
      >
        <input
          id="file-input"
          type="file"
          hidden
          onChange={(e) => handleFileUpload(e.target.files)}
          accept=".pdf,.doc,.docx,.txt"
        />
        <UploadIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          Drop files here or click to upload
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Supported formats: PDF, DOC, DOCX, TXT (Max 100MB)
        </Typography>
      </Paper>

      {isUploading && (
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="body2" gutterBottom>
              Uploading... {uploadProgress}%
            </Typography>
            <LinearProgress variant="determinate" value={uploadProgress} />
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Document Information
          </Typography>
          
          <TextField
            fullWidth
            label="Document Title"
            value={formData.title}
            onChange={(e) => setFormData({...formData, title: e.target.value})}
            margin="normal"
            required
          />
          
          <TextField
            fullWidth
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
            margin="normal"
            multiline
            rows={3}
          />
          
          <FormControl fullWidth margin="normal" required>
            <InputLabel>Document Type</InputLabel>
            <Select
              value={formData.documentType}
              label="Document Type"
              onChange={(e) => setFormData({...formData, documentType: e.target.value})}
            >
              <MenuItem value="RESEARCH_PAPER">Research Paper</MenuItem>
              <MenuItem value="THESIS">Thesis</MenuItem>
              <MenuItem value="DISSERTATION">Dissertation</MenuItem>
              <MenuItem value="ASSIGNMENT">Assignment</MenuItem>
              <MenuItem value="PROJECT_REPORT">Project Report</MenuItem>
            </Select>
          </FormControl>
          
          <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
            <TextField
              label="Course Code"
              value={formData.courseCode}
              onChange={(e) => setFormData({...formData, courseCode: e.target.value})}
            />
            <TextField
              label="Academic Year"
              value={formData.academicYear}
              onChange={(e) => setFormData({...formData, academicYear: e.target.value})}
              placeholder="2023-2024"
            />
            <TextField
              label="Semester"
              value={formData.semester}
              onChange={(e) => setFormData({...formData, semester: e.target.value})}
              placeholder="Fall"
            />
          </Box>
          
          <Button
            variant="contained"
            size="large"
            sx={{ mt: 3 }}
            disabled={!formData.title || !formData.documentType}
          >
            Save Document
          </Button>
        </CardContent>
      </Card>
    </Box>
  );
};

export default DocumentUpload;