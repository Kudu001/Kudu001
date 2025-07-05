import React from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Chip,
  Divider,
  Paper,
} from '@mui/material';
import {
  Download as DownloadIcon,
  FindInPage as PlagiarismIcon,
  Description as FileIcon,
} from '@mui/icons-material';

const DocumentView: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  // Mock document data
  const document = {
    id,
    title: 'Advanced Machine Learning Techniques in Computer Vision',
    description: 'A comprehensive study of modern ML approaches for image recognition and processing, including deep neural networks, convolutional architectures, and transfer learning methodologies.',
    type: 'RESEARCH_PAPER',
    author: 'John Smith',
    uploadDate: '2024-01-15',
    fileSize: '2.4 MB',
    plagiarismScore: 12,
    tags: ['Machine Learning', 'Computer Vision', 'AI'],
    courseCode: 'CS 545',
    academicYear: '2023-2024',
    semester: 'Fall',
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 4 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
            {document.title}
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {document.description}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="outlined" startIcon={<DownloadIcon />}>
            Download
          </Button>
          <Button variant="contained" startIcon={<PlagiarismIcon />}>
            Check Plagiarism
          </Button>
        </Box>
      </Box>

      <Box sx={{ display: 'flex', gap: 3 }}>
        {/* Document Details */}
        <Box sx={{ flex: 2 }}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Document Information
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">Type:</Typography>
                  <Chip label={document.type.replace('_', ' ')} color="primary" size="small" />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">Author:</Typography>
                  <Typography variant="body2">{document.author}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">Upload Date:</Typography>
                  <Typography variant="body2">{document.uploadDate}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">File Size:</Typography>
                  <Typography variant="body2">{document.fileSize}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">Course:</Typography>
                  <Typography variant="body2">{document.courseCode}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">Academic Year:</Typography>
                  <Typography variant="body2">{document.academicYear}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">Semester:</Typography>
                  <Typography variant="body2">{document.semester}</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Tags
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {document.tags.map((tag) => (
                  <Chip 
                    key={tag} 
                    label={tag} 
                    variant="outlined"
                    color="primary"
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Box>

        {/* Plagiarism Results */}
        <Box sx={{ flex: 1 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Plagiarism Analysis
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              <Box sx={{ textAlign: 'center', mb: 3 }}>
                <Typography variant="h2" color="success.main" fontWeight="bold">
                  {document.plagiarismScore}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Similarity Score
                </Typography>
              </Box>
              
              <Paper sx={{ p: 2, bgcolor: 'success.light', color: 'success.contrastText', mb: 2 }}>
                <Typography variant="body2" fontWeight="bold">
                  ✓ Low Similarity Detected
                </Typography>
                <Typography variant="caption">
                  This document appears to be original content.
                </Typography>
              </Paper>
              
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Last checked: {document.uploadDate}
              </Typography>
              
              <Button
                fullWidth
                variant="outlined"
                startIcon={<PlagiarismIcon />}
              >
                Run New Check
              </Button>
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Box>
  );
};

export default DocumentView;