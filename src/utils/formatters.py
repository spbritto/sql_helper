"""
Formatadores e utilitários de formatação
"""
import json
from typing import Any, Dict
from datetime import datetime


class SQLFormatter:
    """Formatador de queries SQL"""
    
    @staticmethod
    def format_query(sql: str, indent: int = 2) -> str:
        """
        Formata uma query SQL para melhor legibilidade
        
        Args:
            sql: Query SQL
            indent: Número de espaços para indentação
            
        Returns:
            Query formatada
        """
        # Palavras-chave para quebrar linha
        keywords = [
            'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER JOIN',
            'LEFT JOIN', 'RIGHT JOIN', 'ORDER BY', 'GROUP BY',
            'HAVING', 'LIMIT', 'UNION', 'AND', 'OR'
        ]
        
        formatted = sql
        
        # Adiciona quebras de linha após palavras-chave
        for keyword in keywords:
            formatted = formatted.replace(
                f' {keyword} ',
                f'\n{keyword} '
            )
        
        # Indenta
        lines = formatted.split('\n')
        indented_lines = []
        current_indent = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Ajusta indentação
            if line.startswith(('WHERE', 'JOIN', 'ORDER BY', 'GROUP BY')):
                current_indent = indent
            elif line.startswith('SELECT'):
                current_indent = 0
            
            indented_lines.append(' ' * current_indent + line)
        
        return '\n'.join(indented_lines)
    
    @staticmethod
    def minify_query(sql: str) -> str:
        """
        Remove espaços extras e formatação
        
        Args:
            sql: Query SQL
            
        Returns:
            Query minificada
        """
        import re
        # Remove múltiplos espaços
        sql = re.sub(r'\s+', ' ', sql)
        return sql.strip()


class JSONFormatter:
    """Formatador de JSON"""
    
    @staticmethod
    def to_pretty_json(data: Any, indent: int = 2) -> str:
        """
        Converte dados para JSON formatado
        
        Args:
            data: Dados para converter
            indent: Indentação
            
        Returns:
            String JSON formatada
        """
        return json.dumps(
            data,
            indent=indent,
            ensure_ascii=False,
            default=str  # Converte datetime e outros tipos
        )
    
    @staticmethod
    def from_json(json_str: str) -> Any:
        """
        Parse de string JSON
        
        Args:
            json_str: String JSON
            
        Returns:
            Dados parseados
        """
        return json.loads(json_str)


class DateTimeFormatter:
    """Formatador de datas"""
    
    @staticmethod
    def format_datetime(
        dt: datetime, 
        format_str: str = "%Y-%m-%d %H:%M:%S"
    ) -> str:
        """
        Formata datetime
        
        Args:
            dt: Datetime
            format_str: Formato
            
        Returns:
            String formatada
        """
        return dt.strftime(format_str)
    
    @staticmethod
    def parse_datetime(
        date_str: str, 
        format_str: str = "%Y-%m-%d %H:%M:%S"
    ) -> datetime:
        """
        Parse de string para datetime
        
        Args:
            date_str: String com data
            format_str: Formato esperado
            
        Returns:
            Datetime parseado
        """
        return datetime.strptime(date_str, format_str)
    
    @staticmethod
    def to_iso(dt: datetime) -> str:
        """
        Converte para formato ISO
        
        Args:
            dt: Datetime
            
        Returns:
            String ISO
        """
        return dt.isoformat()

