# multi_modal_rag/orchestration/research_orchestrator.py
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import Document
from typing import List, Dict

from multi_modal_rag.indexing.opensearch_manager import OpenSearchManager
from multi_modal_rag.logging_config import get_logger

logger = get_logger(__name__)

class ResearchOrchestrator:
    """Orchestrate complex research queries with LangChain"""

    def __init__(self, gemini_api_key: str, opensearch_manager: OpenSearchManager):
        logger.info("Initializing ResearchOrchestrator...")
        try:
            logger.debug("Creating ChatGoogleGenerativeAI with model: gemini-pro")
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-pro",
                google_api_key=gemini_api_key,
                temperature=0.3,
                convert_system_message_to_human=True
            )
            self.opensearch = opensearch_manager
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            logger.info("✅ ResearchOrchestrator initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ResearchOrchestrator: {type(e).__name__}: {e}", exc_info=True)
            raise
        
    def create_research_chain(self):
        """
        Create a research chain with citation tracking
        """
        prompt_template = """
        You are a research assistant analyzing multi-modal academic content.
        
        Context from various sources:
        {context}
        
        Previous conversation:
        {chat_history}
        
        Question: {question}
        
        Instructions:
        1. Provide a comprehensive answer based on the context
        2. Cite sources using [Author, Year] format
        3. Mention if information comes from videos or podcasts
        4. Highlight any diagrams or visual content that supports the answer
        5. Suggest related topics for further exploration
        
        Answer:
        """
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "chat_history", "question"]
        )
        
        return PROMPT
    
    def process_query(self, query: str, index_name: str) -> Dict:
        """
        Process a research query with full pipeline
        """
        logger.info(f"Processing research query: '{query}' on index '{index_name}'")
        try:
            # Step 1: Retrieve relevant documents
            logger.debug("Step 1: Retrieving relevant documents from OpenSearch")
            search_results = self.opensearch.hybrid_search(index_name, query, k=10)
            logger.info(f"Retrieved {len(search_results)} search results")

            # Step 2: Format context with citations
            logger.debug("Step 2: Formatting context with citations")
            context_with_citations = self.format_context_with_citations(search_results)

            # Step 3: Generate response
            logger.debug("Step 3: Generating LLM response")
            prompt = self.create_research_chain()

            full_prompt = prompt.format(
                context=context_with_citations,
                chat_history=str(self.memory.chat_memory) if hasattr(self.memory, 'chat_memory') else "",
                question=query
            )

            logger.debug("Invoking LLM...")
            response = self.llm.invoke(full_prompt).content
            logger.info(f"Generated response ({len(response)} chars)")

            # Step 4: Extract and track citations
            logger.debug("Step 4: Extracting citations from response")
            citations = self.extract_citations(response, search_results)
            logger.info(f"Extracted {len(citations)} citations")

            # Step 5: Update memory
            logger.debug("Step 5: Updating conversation memory")
            self.memory.save_context({"input": query}, {"output": response})

            # Step 6: Generate related queries
            logger.debug("Step 6: Generating related queries")
            related_queries = self.generate_related_queries(query, response)

            logger.info("✅ Successfully processed research query")
            return {
                'answer': response,
                'citations': citations,
                'source_documents': search_results,
                'related_queries': related_queries
            }

        except Exception as e:
            logger.error(f"Error processing query '{query}': {type(e).__name__}: {e}", exc_info=True)
            return {
                'answer': f"Error processing query: {str(e)}",
                'citations': [],
                'source_documents': [],
                'related_queries': []
            }
    
    def format_context_with_citations(self, search_results: List[Dict]) -> str:
        """
        Format search results with proper citation markers
        """
        context = []
        
        for i, result in enumerate(search_results):
            source = result['source']
            
            # Create citation marker
            if source['content_type'] == 'paper':
                citation = f"[{source.get('authors', ['Unknown'])[0]}, {source.get('publication_date', 'n.d.')[:4]}]"
            elif source['content_type'] == 'video':
                citation = f"[Video: {source.get('author', 'Unknown')}, {source.get('title', 'Untitled')[:30]}...]"
            else:  # podcast
                citation = f"[Podcast: {source.get('title', 'Untitled')[:30]}...]"
            
            # Format content
            content_text = f"""
            Source {i+1} {citation}:
            Title: {source.get('title', 'Untitled')}
            Type: {source.get('content_type', 'unknown')}
            Content: {source.get('content', source.get('transcript', source.get('abstract', '')))[:500]}...
            """
            
            if source.get('diagram_descriptions'):
                content_text += f"\nVisual Content: {source['diagram_descriptions'][:200]}..."
            
            context.append(content_text)
        
        return "\n\n".join(context)
    
    def extract_citations(self, response: str, search_results: List[Dict]) -> List[Dict]:
        """
        Extract citations from the generated response
        """
        import re
        
        citations = []
        
        # Find all citation patterns in response
        citation_patterns = [
            r'\[([^,\]]+),\s*(\d{4})\]',  # [Author, Year]
            r'\[Video:\s*([^\]]+)\]',      # [Video: ...]
            r'\[Podcast:\s*([^\]]+)\]'     # [Podcast: ...]
        ]
        
        for pattern in citation_patterns:
            matches = re.findall(pattern, response)
            
            for match in matches:
                # Match with source documents
                for result in search_results:
                    source = result['source']
                    
                    # Check if citation matches this source
                    if self.citation_matches_source(match, source):
                        citations.append({
                            'citation_text': match,
                            'source': source,
                            'content_type': source['content_type'],
                            'url': source.get('url', ''),
                            'title': source.get('title', '')
                        })
                        break
        
        return citations
    
    def citation_matches_source(self, citation_match, source: Dict) -> bool:
        """
        Check if a citation matches a source document
        """
        if source['content_type'] == 'paper':
            authors = source.get('authors', [])
            if authors and citation_match[0] in authors[0]:
                return True
        elif source['content_type'] == 'video':
            if citation_match[0] in source.get('title', ''):
                return True
        elif source['content_type'] == 'podcast':
            if citation_match[0] in source.get('title', ''):
                return True
        
        return False
    
    def generate_related_queries(self, original_query: str, response: str) -> List[str]:
        """
        Generate related research queries
        """
        prompt = f"""
        Based on this research query: "{original_query}"
        And this response: "{response[:500]}..."

        Generate 5 related research questions that would deepen understanding of this topic.
        Format as a JSON list.
        """

        try:
            related_response = self.llm.invoke(prompt)
            related = related_response.content if hasattr(related_response, 'content') else str(related_response)

            import json
            return json.loads(related)
        except:
            # Fallback: return simple related queries
            return [
                f"What are the key concepts in {original_query}?",
                f"How does {original_query} relate to current research?",
                f"What are recent developments in {original_query}?"
            ]