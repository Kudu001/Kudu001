import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Paper,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Chip,
  IconButton,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  FindInPage as PlagiarismIcon,
  FolderOpen as DocumentsIcon,
  TrendingUp as TrendingIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Description as FileIcon,
  MoreVert as MoreIcon,
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  // Mock data - in a real app, this would come from API
  const stats = {
    totalDocuments: 156,
    recentUploads: 12,
    plagiarismChecks: 45,
    warnings: 3,
  };

  const recentDocuments = [
    {
      id: '1',
      title: 'Research Paper on Machine Learning',
      type: 'RESEARCH_PAPER',
      uploadDate: '2024-01-15',
      status: 'checked',
      similarity: 15,
    },
    {
      id: '2',
      title: 'Software Engineering Project Report',
      type: 'PROJECT_REPORT',
      uploadDate: '2024-01-14',
      status: 'warning',
      similarity: 75,
    },
    {
      id: '3',
      title: 'Database Systems Assignment',
      type: 'ASSIGNMENT',
      uploadDate: '2024-01-13',
      status: 'checked',
      similarity: 8,
    },
  ];

  const quickActions = [
    {
      title: 'Upload Document',
      description: 'Upload a new document to the archive',
      icon: <UploadIcon />,
      action: () => navigate('/upload'),
      color: 'primary',
    },
    {
      title: 'Check Plagiarism',
      description: 'Run plagiarism detection on documents',
      icon: <PlagiarismIcon />,
      action: () => navigate('/plagiarism'),
      color: 'secondary',
    },
    {
      title: 'Browse Documents',
      description: 'Explore the document archive',
      icon: <DocumentsIcon />,
      action: () => navigate('/documents'),
      color: 'success',
    },
  ];

  const getStatusIcon = (status: string, similarity: number) => {
    if (status === 'warning' || similarity > 50) {
      return <WarningIcon color="warning" />;
    }
    return <CheckIcon color="success" />;
  };

  const getStatusChip = (status: string, similarity: number) => {
    if (status === 'warning' || similarity > 50) {
      return <Chip label={`${similarity}% Similar`} color="warning" size="small" />;
    }
    return <Chip label={`${similarity}% Similar`} color="success" size="small" />;
  };

  return (
    <Box>
      {/* Welcome Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          Welcome back, {user?.firstName}!
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Here's an overview of your document archive activity
        </Typography>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Total Documents
                  </Typography>
                  <Typography variant="h4" component="h2">
                    {stats.totalDocuments}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  <DocumentsIcon />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Recent Uploads
                  </Typography>
                  <Typography variant="h4" component="h2">
                    {stats.recentUploads}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'success.main' }}>
                  <TrendingIcon />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Plagiarism Checks
                  </Typography>
                  <Typography variant="h4" component="h2">
                    {stats.plagiarismChecks}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'info.main' }}>
                  <PlagiarismIcon />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Warnings
                  </Typography>
                  <Typography variant="h4" component="h2">
                    {stats.warnings}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'warning.main' }}>
                  <WarningIcon />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              Quick Actions
            </Typography>
            <Grid container spacing={2}>
              {quickActions.map((action, index) => (
                <Grid item xs={12} key={index}>
                  <Card variant="outlined" sx={{ cursor: 'pointer' }} onClick={action.action}>
                    <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Avatar sx={{ bgcolor: `${action.color}.main` }}>
                        {action.icon}
                      </Avatar>
                      <Box>
                        <Typography variant="h6">{action.title}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {action.description}
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>

        {/* Recent Documents */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" fontWeight="bold">
                Recent Documents
              </Typography>
              <Button variant="text" onClick={() => navigate('/documents')}>
                View All
              </Button>
            </Box>
            <List>
              {recentDocuments.map((doc) => (
                <ListItem
                  key={doc.id}
                  sx={{
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    mb: 1,
                  }}
                  secondaryAction={
                    <IconButton edge="end">
                      <MoreIcon />
                    </IconButton>
                  }
                >
                  <ListItemAvatar>
                    <Avatar sx={{ bgcolor: 'grey.100' }}>
                      {getStatusIcon(doc.status, doc.similarity)}
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={doc.title}
                    secondary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                        <Typography variant="caption">
                          {doc.type.replace('_', ' ')} • {doc.uploadDate}
                        </Typography>
                        {getStatusChip(doc.status, doc.similarity)}
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;