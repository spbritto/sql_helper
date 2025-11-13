"""
Serviço para geração de queries SQL usando Langchain
"""
from typing import Optional
from datetime import datetime
from loguru import logger
import json
import re

from langchain_openai import ChatOpenAI
try:
    from langchain_core.prompts import ChatPromptTemplate
except ImportError:
    from langchain.prompts import ChatPromptTemplate

from ..config import settings
from ..models import SQLQueryResponse, DatabaseStructure
from .structure_manager import StructureManager


class QueryGenerator:
    """Gerador de queries SQL a partir de linguagem natural"""
    
    def __init__(self):
        self.llm = self._initialize_llm()
        self.prompt_template = self._create_prompt_template()
    
    def _initialize_llm(self):
        """Inicializa o modelo de linguagem"""
        if not settings.openai_api_key:
            logger.warning("OpenAI API key não configurada")
            return None
            
        return ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key
        )
    
    def _create_prompt_template(self):
        """Cria o template de prompt para geração de queries"""
        template = """Você é um especialista em SQL e otimização de banco de dados.

ESTRUTURA DO BANCO DE DADOS:
{database_structure}

CONTEXTO ADICIONAL:
{context}

PERGUNTA DO USUÁRIO:
{question}

INSTRUÇÕES:
1. Analise cuidadosamente a estrutura do banco de dados fornecida
2. Gere uma query SQL otimizada e precisa que responda à pergunta
3. Use APENAS as tabelas e campos que existem na estrutura fornecida
4. Forneça uma explicação clara do que a query faz
5. Sugira otimizações se aplicável
6. Indique avisos sobre possíveis problemas

IMPORTANTE: Responda APENAS com um objeto JSON válido no seguinte formato:
{{
  "sql": "SELECT ... FROM ...",
  "explanation": "Esta query busca...",
  "confidence": 0.95,
  "optimizations": ["Sugestão 1", "Sugestão 2"],
  "warnings": ["Aviso 1"]
}}

NÃO inclua texto antes ou depois do JSON. APENAS o JSON puro."""
        
        return ChatPromptTemplate.from_template(template)
    
    def _format_structure_for_llm(self, structure: DatabaseStructure) -> str:
        """
        Formata a estrutura do banco de dados em texto legível para o LLM
        
        Args:
            structure: Estrutura do banco de dados
            
        Returns:
            String formatada com a estrutura
        """
        lines = []
        lines.append("=" * 60)
        lines.append("ESTRUTURA DO BANCO DE DADOS")
        lines.append("=" * 60)
        lines.append("")
        
        # Informações gerais
        if structure.metadata.get("database_name"):
            lines.append(f"Banco de dados: {structure.metadata['database_name']}")
            lines.append("")
        
        # Formata cada tabela
        for i, table in enumerate(structure.tables, 1):
            table_name = table.get("name", "N/A")
            fields = table.get("fields", [])
            
            lines.append(f"[{i}] TABELA: {table_name}")
            lines.append("-" * 60)
            
            if not fields:
                lines.append("    ⚠️ Nenhum campo definido")
            else:
                lines.append("    CAMPOS:")
                for field in fields:
                    field_name = field.get("name", "N/A")
                    field_type = field.get("type", "unknown")
                    
                    # Monta informações adicionais
                    extras = []
                    if field.get("primary_key"):
                        extras.append("PRIMARY KEY")
                    if field.get("foreign_key"):
                        ref = field.get("reference")
                        if ref:
                            extras.append(f"FOREIGN KEY -> {ref}")
                        else:
                            extras.append("FOREIGN KEY")
                    if not field.get("nullable", True):
                        extras.append("NOT NULL")
                    
                    extra_info = f" ({', '.join(extras)})" if extras else ""
                    lines.append(f"      • {field_name}: {field_type}{extra_info}")
            
            lines.append("")
        
        # Relacionamentos
        if structure.relationships:
            lines.append("=" * 60)
            lines.append("RELACIONAMENTOS")
            lines.append("=" * 60)
            for rel in structure.relationships:
                from_table = rel.get("from_table", "N/A")
                from_field = rel.get("from_field", "N/A")
                to_table = rel.get("to_table", "N/A")
                to_field = rel.get("to_field", "N/A")
                rel_type = rel.get("type", "N/A")
                
                lines.append(f"  {from_table}.{from_field} -> {to_table}.{to_field} ({rel_type})")
            lines.append("")
        
        lines.append("=" * 60)
        
        formatted_text = "\n".join(lines)
        logger.debug(f"Estrutura formatada para LLM:\n{formatted_text}")
        
        return formatted_text
    
    def _parse_llm_response(self, response_text: str) -> dict:
        """
        Faz parse da resposta do LLM para extrair o JSON
        
        Args:
            response_text: Texto da resposta do LLM
            
        Returns:
            Dict com os dados parseados
        """
        logger.debug(f"Resposta bruta do LLM (primeiros 500 chars):\n{response_text[:500]}")
        
        try:
            # Tenta fazer parse direto como JSON
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Se falhar, tenta extrair JSON do texto
            logger.warning("Resposta não é JSON puro, tentando extrair...")
            
            # Procura por padrão ```json ... ```
            json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
            match = re.search(json_pattern, response_text, re.DOTALL)
            
            if match:
                json_str = match.group(1)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    logger.error(f"Erro ao parsear JSON extraído: {e}")
            
            # Tenta encontrar qualquer objeto JSON no texto
            json_pattern2 = r'\{[^}]*"sql"[^}]*\}'
            match2 = re.search(json_pattern2, response_text, re.DOTALL)
            
            if match2:
                json_str = match2.group(0)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    logger.error(f"Erro ao parsear JSON alternativo: {e}")
            
            # Se tudo falhar, retorna estrutura padrão com o texto
            logger.error("Não foi possível extrair JSON válido da resposta do LLM")
            return {
                "sql": "-- Erro ao parsear resposta do LLM",
                "explanation": f"Resposta do LLM não está em formato JSON válido. Resposta: {response_text[:200]}",
                "confidence": 0.0,
                "optimizations": [],
                "warnings": ["Formato de resposta inválido"]
            }
    
    async def generate(
        self, 
        question: str, 
        structure_id: Optional[str] = None,
        context: Optional[str] = None
    ) -> SQLQueryResponse:
        """
        Gera uma query SQL a partir de linguagem natural
        
        Args:
            question: Pergunta em linguagem natural
            structure_id: ID da estrutura do banco de dados
            context: Contexto adicional
            
        Returns:
            SQLQueryResponse com a query gerada
        """
        try:
            logger.info(f"🔍 Iniciando geração de query para: '{question}'")
            
            # Verifica se LLM está configurado
            if not self.llm:
                logger.error("❌ LLM não configurado - API key ausente")
                return SQLQueryResponse(
                    sql="-- LLM não configurado. Configure OPENAI_API_KEY no arquivo .env",
                    explanation="Configure a API key da OpenAI para usar este recurso",
                    confidence=0.0,
                    optimizations=[],
                    warnings=["API key não configurada"]
                )
            
            # Busca estrutura do banco de dados usando StructureManager
            structure = StructureManager.get_structure()
            
            if structure is None:
                logger.error("❌ Nenhuma estrutura de banco de dados carregada")
                return SQLQueryResponse(
                    sql="-- Nenhuma estrutura de banco de dados carregada",
                    explanation="Por favor, carregue uma estrutura de banco de dados antes de gerar queries",
                    confidence=0.0,
                    optimizations=[],
                    warnings=["Estrutura não carregada. Vá em 'Carregar Estrutura' e faça upload de um arquivo."]
                )
            
            # Formata a estrutura para o LLM
            logger.info(f"📊 Estrutura carregada: {len(structure.tables)} tabelas")
            database_structure = self._format_structure_for_llm(structure)
            
            # Cria o prompt com a estrutura REAL
            logger.debug("📝 Criando prompt com estrutura real...")
            messages = self.prompt_template.format_messages(
                database_structure=database_structure,
                context=context or "Nenhum contexto adicional fornecido",
                question=question
            )
            
            # Gera a query usando o LLM
            logger.info("🤖 Chamando LLM para gerar query...")
            result = await self.llm.ainvoke(messages)
            
            # Extrai o texto da resposta
            response_text = result.content if hasattr(result, 'content') else str(result)
            logger.debug(f"✅ LLM respondeu ({len(response_text)} chars)")
            
            # Parse da resposta do LLM
            parsed_response = self._parse_llm_response(response_text)
            
            # Constrói a resposta final
            sql_response = SQLQueryResponse(
                sql=parsed_response.get("sql", "-- Erro ao extrair SQL"),
                explanation=parsed_response.get("explanation", "Explicação não disponível"),
                confidence=float(parsed_response.get("confidence", 0.8)),
                optimizations=parsed_response.get("optimizations", []),
                warnings=parsed_response.get("warnings", [])
            )
            
            logger.success(f"✅ Query gerada com sucesso! Confiança: {sql_response.confidence:.2%}")
            logger.debug(f"SQL gerado:\n{sql_response.sql}")
            
            return sql_response
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar query: {e}", exc_info=True)
            
            # Retorna resposta de erro amigável
            return SQLQueryResponse(
                sql="-- Erro ao gerar query",
                explanation=f"Ocorreu um erro ao gerar a query: {str(e)}",
                confidence=0.0,
                optimizations=[],
                warnings=[f"Erro: {str(e)}"]
            )
    
    async def optimize(self, sql: str) -> dict:
        """
        Otimiza uma query SQL existente
        
        Args:
            sql: Query SQL a ser otimizada
            
        Returns:
            Dict com query otimizada e sugestões
        """
        # TODO: Implementar otimização real
        return {
            "original_sql": sql,
            "optimized_sql": sql,
            "suggestions": ["Implementar otimização real"],
            "estimated_improvement": "N/A"
        }
    
    async def validate(self, sql: str) -> dict:
        """
        Valida uma query SQL
        
        Args:
            sql: Query SQL a ser validada
            
        Returns:
            Dict com resultado da validação
        """
        # TODO: Implementar validação real
        return {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }

