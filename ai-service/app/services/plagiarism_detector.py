import asyncio
import logging
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import difflib
from fuzzywuzzy import fuzz
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import nltk

from app.core.config import settings
from app.models.schemas import PlagiarismResult, TextSegment, SimilarityMatch

logger = logging.getLogger(__name__)

@dataclass
class DocumentChunk:
    text: str
    start_pos: int
    end_pos: int
    chunk_id: int

class PlagiarismDetector:
    """Advanced plagiarism detection using multiple AI techniques"""
    
    def __init__(self):
        self.sentence_model: Optional[SentenceTransformer] = None
        self.stopwords = set()
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the plagiarism detector with models and resources"""
        try:
            logger.info("Initializing plagiarism detector...")
            
            # Download NLTK data if not present
            try:
                nltk.data.find('tokenizers/punkt')
                nltk.data.find('corpora/stopwords')
            except LookupError:
                logger.info("Downloading NLTK data...")
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
            
            # Load sentence transformer model
            logger.info(f"Loading sentence transformer model: {settings.SENTENCE_TRANSFORMER_MODEL}")
            self.sentence_model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
            
            # Load stopwords
            self.stopwords = set(stopwords.words('english'))
            
            self.is_initialized = True
            logger.info("Plagiarism detector initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize plagiarism detector: {e}")
            raise
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for comparison"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove citations and references patterns
        text = re.sub(r'\[[0-9]+\]', '', text)  # Remove [1], [2], etc.
        text = re.sub(r'\([^)]*\d{4}[^)]*\)', '', text)  # Remove year citations
        
        return text
    
    def create_chunks(self, text: str) -> List[DocumentChunk]:
        """Split document into overlapping chunks for processing"""
        sentences = sent_tokenize(text)
        chunks = []
        chunk_id = 0
        
        current_chunk = ""
        current_start = 0
        
        for i, sentence in enumerate(sentences):
            if len(current_chunk) + len(sentence) <= settings.CHUNK_SIZE:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(DocumentChunk(
                        text=current_chunk.strip(),
                        start_pos=current_start,
                        end_pos=current_start + len(current_chunk),
                        chunk_id=chunk_id
                    ))
                    chunk_id += 1
                
                current_chunk = sentence
                current_start = sum(len(s) for s in sentences[:i])
        
        # Add the last chunk
        if current_chunk:
            chunks.append(DocumentChunk(
                text=current_chunk.strip(),
                start_pos=current_start,
                end_pos=current_start + len(current_chunk),
                chunk_id=chunk_id
            ))
        
        return chunks
    
    async def compute_semantic_similarity(self, text1: str, text2: str) -> float:
        """Compute semantic similarity using sentence transformers"""
        try:
            if not self.sentence_model:
                raise ValueError("Sentence model not initialized")
            
            # Generate embeddings
            embeddings = self.sentence_model.encode([text1, text2])
            
            # Compute cosine similarity
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error computing semantic similarity: {e}")
            return 0.0
    
    def compute_lexical_similarity(self, text1: str, text2: str) -> float:
        """Compute lexical similarity using string matching"""
        # Use SequenceMatcher for similarity
        seq_similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
        
        # Use fuzzy matching
        fuzzy_similarity = fuzz.ratio(text1, text2) / 100.0
        
        # Combine both metrics
        combined_similarity = (seq_similarity + fuzzy_similarity) / 2.0
        
        return combined_similarity
    
    def find_exact_matches(self, text1: str, text2: str, min_length: int = 50) -> List[SimilarityMatch]:
        """Find exact text matches between two documents"""
        matches = []
        
        # Split into words for more granular matching
        words1 = word_tokenize(text1.lower())
        words2 = word_tokenize(text2.lower())
        
        # Find common subsequences
        matcher = difflib.SequenceMatcher(None, words1, words2)
        
        for match in matcher.get_matching_blocks():
            if match.size > min_length // 5:  # Approximate word count threshold
                start1_char = len(' '.join(words1[:match.a]))
                end1_char = len(' '.join(words1[:match.a + match.size]))
                start2_char = len(' '.join(words2[:match.b]))
                end2_char = len(' '.join(words2[:match.b + match.size]))
                
                matched_text = ' '.join(words1[match.a:match.a + match.size])
                
                if len(matched_text) >= min_length:
                    matches.append(SimilarityMatch(
                        source_start=start1_char,
                        source_end=end1_char,
                        target_start=start2_char,
                        target_end=end2_char,
                        matched_text=matched_text,
                        similarity_score=1.0,
                        match_type="exact"
                    ))
        
        return matches
    
    async def detect_plagiarism(
        self,
        source_text: str,
        target_documents: List[Dict[str, Any]],
        min_similarity: float = None
    ) -> PlagiarismResult:
        """
        Detect plagiarism between source text and target documents
        
        Args:
            source_text: The text to check for plagiarism
            target_documents: List of documents to compare against
            min_similarity: Minimum similarity threshold
        
        Returns:
            PlagiarismResult with detailed analysis
        """
        if not self.is_initialized:
            raise ValueError("Plagiarism detector not initialized")
        
        if min_similarity is None:
            min_similarity = settings.SIMILARITY_THRESHOLD
        
        logger.info(f"Starting plagiarism detection for {len(target_documents)} documents")
        
        # Preprocess source text
        processed_source = self.preprocess_text(source_text)
        source_chunks = self.create_chunks(processed_source)
        
        all_matches = []
        document_similarities = {}
        
        for target_doc in target_documents:
            target_text = target_doc.get('content', '')
            target_id = target_doc.get('id')
            
            if not target_text or not target_id:
                continue
            
            # Preprocess target text
            processed_target = self.preprocess_text(target_text)
            target_chunks = self.create_chunks(processed_target)
            
            # Find matches between chunks
            doc_matches = []
            similarities = []
            
            for source_chunk in source_chunks:
                for target_chunk in target_chunks:
                    # Compute semantic similarity
                    semantic_sim = await self.compute_semantic_similarity(
                        source_chunk.text, target_chunk.text
                    )
                    
                    # Compute lexical similarity
                    lexical_sim = self.compute_lexical_similarity(
                        source_chunk.text, target_chunk.text
                    )
                    
                    # Combined similarity score
                    combined_sim = (semantic_sim * 0.7 + lexical_sim * 0.3)
                    similarities.append(combined_sim)
                    
                    if combined_sim >= min_similarity:
                        # Find exact matches within this chunk pair
                        exact_matches = self.find_exact_matches(
                            source_chunk.text, target_chunk.text
                        )
                        
                        match = SimilarityMatch(
                            source_start=source_chunk.start_pos,
                            source_end=source_chunk.end_pos,
                            target_start=target_chunk.start_pos,
                            target_end=target_chunk.end_pos,
                            matched_text=source_chunk.text[:200] + "..." if len(source_chunk.text) > 200 else source_chunk.text,
                            similarity_score=combined_sim,
                            match_type="semantic",
                            exact_matches=exact_matches
                        )
                        doc_matches.append(match)
            
            # Calculate overall document similarity
            if similarities:
                max_similarity = max(similarities)
                avg_similarity = sum(similarities) / len(similarities)
                overall_similarity = (max_similarity * 0.6 + avg_similarity * 0.4)
            else:
                overall_similarity = 0.0
            
            document_similarities[target_id] = {
                'similarity': overall_similarity,
                'matches': doc_matches,
                'title': target_doc.get('title', 'Unknown'),
                'author': target_doc.get('author', 'Unknown')
            }
            
            all_matches.extend(doc_matches)
        
        # Calculate overall plagiarism score
        if document_similarities:
            max_doc_similarity = max(doc['similarity'] for doc in document_similarities.values())
            overall_score = max_doc_similarity
        else:
            overall_score = 0.0
        
        # Determine plagiarism status
        is_plagiarized = overall_score >= min_similarity
        confidence = min(overall_score * 1.2, 1.0)  # Boost confidence slightly
        
        result = PlagiarismResult(
            overall_similarity=overall_score,
            is_plagiarized=is_plagiarized,
            confidence_score=confidence,
            total_matches=len(all_matches),
            document_similarities=document_similarities,
            detection_method="hybrid_semantic_lexical",
            processing_time=0,  # Will be calculated by caller
            matches=all_matches[:100]  # Limit to top 100 matches
        )
        
        logger.info(f"Plagiarism detection completed. Score: {overall_score:.3f}, Matches: {len(all_matches)}")
        
        return result