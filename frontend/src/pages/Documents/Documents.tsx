import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  IconButton,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Pagination,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Description as FileIcon,
  Download as DownloadIcon,
  FindInPage as PlagiarismIcon,
  MoreVert as MoreIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const Documents: React.FC = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('ALL');
  const [currentPage, setCurrentPage] = useState(1);

  // Mock data - in a real app, this would come from API
  const documents = [
    {
      id: '1',
      title: 'Advanced Machine Learning Techniques in Computer Vision',
      description: 'A comprehensive study of modern ML approaches for image recognition and processing.',
      type: 'RESEARCH_PAPER',
      author: 'John Smith',
      uploadDate: '2024-01-15',
      fileSize: '2.4 MB',
      plagiarismScore: 12,
      tags: ['Machine Learning', 'Computer Vision', 'AI'],
    },
    {
      id: '2',
      title: 'Software Engineering Best Practices',
      description: 'Guidelines and methodologies for modern software development projects.',
      type: 'PROJECT_REPORT',
      author: 'Sarah Johnson',
      uploadDate: '2024-01-14',
      fileSize: '1.8 MB',
      plagiarismScore: 75,
      tags: ['Software Engineering', 'Best Practices'],
    },
    {
      id: '3',
      title: 'Database Systems and Optimization',
      description: 'Analysis of database performance optimization techniques and query planning.',
      type: 'ASSIGNMENT',
      author: 'Mike Wilson',
      uploadDate: '2024-01-13',
      fileSize: '3.1 MB',
      plagiarismScore: 8,
      tags: ['Database', 'Optimization', 'SQL'],
    },
    {
      id: '4',
      title: 'Blockchain Technology in Finance',
      description: 'Exploring the applications of blockchain technology in financial services.',
      type: 'THESIS',
      author: 'Emily Brown',
      uploadDate: '2024-01-12',
      fileSize: '5.2 MB',
      plagiarismScore: 22,
      tags: ['Blockchain', 'Finance', 'Cryptocurrency'],
    },
    {
      id: '5',
      title: 'Neural Networks and Deep Learning',
      description: 'Comprehensive analysis of neural network architectures and their applications.',
      type: 'DISSERTATION',
      author: 'David Chen',
      uploadDate: '2024-01-11',
      fileSize: '7.8 MB',
      plagiarismScore: 15,
      tags: ['Neural Networks', 'Deep Learning', 'AI'],
    },
  ];

  const getTypeColor = (type: string) => {
    const colors: { [key: string]: any } = {
      RESEARCH_PAPER: 'primary',
      PROJECT_REPORT: 'secondary',
      ASSIGNMENT: 'success',
      THESIS: 'warning',
      DISSERTATION: 'info',
    };
    return colors[type] || 'default';
  };

  const getPlagiarismColor = (score: number) => {
    if (score > 50) return 'error';
    if (score > 25) return 'warning';
    return 'success';
  };

  const filteredDocuments = documents.filter((doc) => {
    const matchesSearch = doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         doc.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         doc.author.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = filterType === 'ALL' || doc.type === filterType;
    return matchesSearch && matchesType;
  });

  const itemsPerPage = 6;
  const totalPages = Math.ceil(filteredDocuments.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedDocuments = filteredDocuments.slice(startIndex, startIndex + itemsPerPage);

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          Document Archive
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Browse and manage your academic documents
        </Typography>
      </Box>

      {/* Search and Filters */}
      <Box sx={{ mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Search documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Document Type</InputLabel>
              <Select
                value={filterType}
                label="Document Type"
                onChange={(e) => setFilterType(e.target.value)}
              >
                <MenuItem value="ALL">All Types</MenuItem>
                <MenuItem value="RESEARCH_PAPER">Research Paper</MenuItem>
                <MenuItem value="PROJECT_REPORT">Project Report</MenuItem>
                <MenuItem value="ASSIGNMENT">Assignment</MenuItem>
                <MenuItem value="THESIS">Thesis</MenuItem>
                <MenuItem value="DISSERTATION">Dissertation</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <Button
              fullWidth
              variant="contained"
              startIcon={<FilterIcon />}
              onClick={() => navigate('/upload')}
            >
              Upload New
            </Button>
          </Grid>
        </Grid>
      </Box>

      {/* Results Summary */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="body2" color="text.secondary">
          Showing {paginatedDocuments.length} of {filteredDocuments.length} documents
        </Typography>
      </Box>

      {/* Documents Grid */}
      <Grid container spacing={3}>
        {paginatedDocuments.map((doc) => (
          <Grid item xs={12} md={6} lg={4} key={doc.id}>
            <Card 
              sx={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column',
                cursor: 'pointer',
                '&:hover': {
                  boxShadow: 6,
                },
              }}
              onClick={() => navigate(`/document/${doc.id}`)}
            >
              <CardContent sx={{ flexGrow: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Chip 
                    label={doc.type.replace('_', ' ')} 
                    color={getTypeColor(doc.type)}
                    size="small"
                  />
                  <IconButton size="small" onClick={(e) => e.stopPropagation()}>
                    <MoreIcon />
                  </IconButton>
                </Box>
                
                <Typography variant="h6" component="h2" gutterBottom>
                  {doc.title}
                </Typography>
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {doc.description}
                </Typography>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="caption" display="block">
                    By {doc.author} • {doc.uploadDate}
                  </Typography>
                  <Typography variant="caption" display="block">
                    Size: {doc.fileSize}
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <Typography variant="caption">Plagiarism Score:</Typography>
                  <Chip 
                    label={`${doc.plagiarismScore}%`}
                    color={getPlagiarismColor(doc.plagiarismScore)}
                    size="small"
                  />
                </Box>
                
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {doc.tags.map((tag) => (
                    <Chip 
                      key={tag} 
                      label={tag} 
                      variant="outlined" 
                      size="small"
                      sx={{ fontSize: '0.7rem' }}
                    />
                  ))}
                </Box>
              </CardContent>
              
              <CardActions>
                <Button 
                  size="small" 
                  startIcon={<DownloadIcon />}
                  onClick={(e) => e.stopPropagation()}
                >
                  Download
                </Button>
                <Button 
                  size="small" 
                  startIcon={<PlagiarismIcon />}
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate('/plagiarism');
                  }}
                >
                  Check
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Pagination */}
      {totalPages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <Pagination
            count={totalPages}
            page={currentPage}
            onChange={(event, value) => setCurrentPage(value)}
            color="primary"
          />
        </Box>
      )}

      {/* No Results */}
      {filteredDocuments.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <FileIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No documents found
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Try adjusting your search criteria or upload a new document.
          </Typography>
          <Button variant="contained" onClick={() => navigate('/upload')}>
            Upload Document
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default Documents;