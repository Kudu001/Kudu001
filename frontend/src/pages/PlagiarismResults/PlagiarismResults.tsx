import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  List,
  ListItem,
  ListItemText,
  Chip,
  LinearProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
} from '@mui/material';
import {
  FindInPage as PlagiarismIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';

const PlagiarismResults: React.FC = () => {
  const [selectedJob, setSelectedJob] = useState('all');

  // Mock plagiarism jobs data
  const plagiarismJobs = [
    {
      id: '1',
      documentTitle: 'Machine Learning Research Paper',
      status: 'COMPLETED',
      similarity: 12,
      dateRun: '2024-01-15',
      matches: 3,
    },
    {
      id: '2',
      documentTitle: 'Software Engineering Report',
      status: 'PROCESSING',
      similarity: null,
      dateRun: '2024-01-15',
      matches: null,
    },
    {
      id: '3',
      documentTitle: 'Database Systems Assignment',
      status: 'COMPLETED',
      similarity: 75,
      dateRun: '2024-01-14',
      matches: 12,
    },
  ];

  const similarityMatches = [
    {
      id: '1',
      sourceText: 'Machine learning algorithms have revolutionized the field of computer vision...',
      matchedText: 'Machine learning techniques have transformed computer vision applications...',
      similarity: 89,
      documentTitle: 'Computer Vision Fundamentals',
      author: 'Dr. Jane Smith',
    },
    {
      id: '2',
      sourceText: 'Neural networks consist of interconnected nodes that process information...',
      matchedText: 'Neural networks are composed of connected nodes for information processing...',
      similarity: 76,
      documentTitle: 'Introduction to Neural Networks',
      author: 'Prof. Michael Johnson',
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED': return 'success';
      case 'PROCESSING': return 'warning';
      case 'FAILED': return 'error';
      default: return 'default';
    }
  };

  const getSimilarityColor = (score: number) => {
    if (score > 50) return 'error';
    if (score > 25) return 'warning';
    return 'success';
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
        Plagiarism Detection Results
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        View and manage plagiarism detection results
      </Typography>

      <Box sx={{ display: 'flex', gap: 3 }}>
        {/* Jobs List */}
        <Box sx={{ flex: 1 }}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Detection Jobs</Typography>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>Filter</InputLabel>
                  <Select
                    value={selectedJob}
                    label="Filter"
                    onChange={(e) => setSelectedJob(e.target.value)}
                  >
                    <MenuItem value="all">All Jobs</MenuItem>
                    <MenuItem value="completed">Completed</MenuItem>
                    <MenuItem value="processing">Processing</MenuItem>
                  </Select>
                </FormControl>
              </Box>
              
              <List>
                {plagiarismJobs.map((job) => (
                  <ListItem
                    key={job.id}
                    sx={{
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 1,
                      mb: 1,
                    }}
                  >
                    <ListItemText
                      primary={job.documentTitle}
                      secondary={
                        <Box sx={{ mt: 1 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <Chip 
                              label={job.status} 
                              color={getStatusColor(job.status)}
                              size="small"
                            />
                            {job.similarity !== null && (
                              <Chip 
                                label={`${job.similarity}% Similar`}
                                color={getSimilarityColor(job.similarity)}
                                size="small"
                              />
                            )}
                          </Box>
                          <Typography variant="caption" color="text.secondary">
                            {job.dateRun} • {job.matches ? `${job.matches} matches` : 'Processing...'}
                          </Typography>
                          {job.status === 'PROCESSING' && (
                            <LinearProgress sx={{ mt: 1 }} />
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Box>

        {/* Detailed Results */}
        <Box sx={{ flex: 2 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Similarity Matches
              </Typography>
              
              {similarityMatches.map((match) => (
                <Paper key={match.id} sx={{ p: 2, mb: 2, bgcolor: 'grey.50' }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="subtitle2">
                      Similarity: {match.similarity}%
                    </Typography>
                    <Chip 
                      label={getSimilarityColor(match.similarity) === 'error' ? 'High' : 'Medium'}
                      color={getSimilarityColor(match.similarity)}
                      size="small"
                    />
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" color="text.secondary" display="block">
                      Your text:
                    </Typography>
                    <Typography variant="body2" sx={{ p: 1, bgcolor: 'warning.light', borderRadius: 1 }}>
                      {match.sourceText}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" color="text.secondary" display="block">
                      Matched text:
                    </Typography>
                    <Typography variant="body2" sx={{ p: 1, bgcolor: 'error.light', borderRadius: 1 }}>
                      {match.matchedText}
                    </Typography>
                  </Box>
                  
                  <Typography variant="caption" color="text.secondary">
                    Source: {match.documentTitle} by {match.author}
                  </Typography>
                </Paper>
              ))}
              
              {similarityMatches.length === 0 && (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <CheckIcon sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary">
                    No Significant Matches Found
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    This document appears to be original content.
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Box>
  );
};

export default PlagiarismResults;